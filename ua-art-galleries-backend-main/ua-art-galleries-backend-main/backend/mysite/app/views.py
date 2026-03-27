import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Gallery
from .serializers import GalleryListSerializer, GalleryDetailSerializer

logger = logging.getLogger(__name__)


class GalleryListView(ListAPIView):
    """
    GET /api/galleries/
    Повертає список усіх галерей з бази даних (Neon PostgreSQL).
    """
    queryset = Gallery.objects.all()
    serializer_class = GalleryListSerializer
    permission_classes = [AllowAny]


class GalleryDetailView(RetrieveAPIView):
    """
    GET /api/galleries/<slug>/
    Повертає деталі однієї галереї за її slug.
    """
    queryset = Gallery.objects.all()
    serializer_class = GalleryDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser])
def contentful_webhook(request):
    """
    Webhook endpoint для Contentful.
    Contentful надсилає POST-запит при публікації/оновленні контенту.
    
    URL: /api/webhooks/contentful/
    Method: POST
    """
    # Перевіряємо секретний ключ webhook (опціонально, для безпеки)
    webhook_secret = getattr(settings, 'CONTENTFUL_WEBHOOK_SECRET', None)
    if webhook_secret:
        signature = request.headers.get('X-Contentful-Webhook-Signature', '')
        if not _verify_webhook_signature(request.body, signature, webhook_secret):
            logger.warning("Invalid webhook signature")
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    try:
        data = request.data
        
        # Contentful надсилає дані в форматі Entry
        sys_info = data.get('sys', {})
        content_type = sys_info.get('contentType', {}).get('sys', {}).get('id', '')
        
        # Обробляємо тільки 'project' (галереї)
        if content_type != 'project':
            return Response(
                {'message': f'Ignored content type: {content_type}'},
                status=status.HTTP_200_OK
            )
        
        fields = data.get('fields', {})
        contentful_id = sys_info.get('id', '')
        
        # Визначаємо slug
        slug = fields.get('slug', {}).get('en-US', '') if isinstance(fields.get('slug'), dict) else fields.get('slug', '')
        if not slug:
            name_field = fields.get('name', {})
            name = name_field.get('en-US', '') if isinstance(name_field, dict) else str(name_field)
            slug = slugify(name, allow_unicode=True) or contentful_id
        
        # Отримуємо URL картинки
        image_url = _get_image_url_from_webhook(fields.get('coverImage'))
        
        # Обробка Rich Text (description)
        raw_description = fields.get('description', {})
        if isinstance(raw_description, dict):
            desc_value = raw_description.get('en-US', raw_description)
            if isinstance(desc_value, dict):
                description = _rich_text_to_plain(desc_value)
            else:
                description = str(desc_value)
        else:
            description = str(raw_description) if raw_description else ''
        
        # Обробка social links
        social_links_raw = fields.get('socialLinks', {})
        if isinstance(social_links_raw, dict):
            social_links_raw = social_links_raw.get('en-US', {})
        if social_links_raw is None:
            social_links_raw = {}
        social_links = social_links_raw.get('links', []) if isinstance(social_links_raw, dict) else []
        
        # Обробка artists
        artists_raw = fields.get('artistsList', {})
        if isinstance(artists_raw, dict):
            artists_raw = artists_raw.get('en-US', [])
        if isinstance(artists_raw, list):
            artists = '\n'.join(str(a) for a in artists_raw)
        else:
            artists = str(artists_raw) if artists_raw else ''
        
        # Отримуємо значення полів (враховуючи локалізацію Contentful)
        name = _get_localized_value(fields.get('name'), '')
        city = _get_localized_value(fields.get('city'), '')
        address = _get_localized_value(fields.get('address'), '')
        short_description = _get_localized_value(fields.get('shortDescription'), '')
        founders = _get_localized_value(fields.get('founders'), '')
        curators = _get_localized_value(fields.get('curators'), '')
        email = _get_localized_value(fields.get('email'), '')
        phone = _get_localized_value(fields.get('phone'), '')
        website_url = _get_localized_value(fields.get('websiteUrl'), '')
        founding_year = _get_localized_value(fields.get('foundingYear'), None)
        
        # Створюємо або оновлюємо запис в БД
        gallery, created = Gallery.objects.update_or_create(
            slug=slug,
            defaults={
                'name_ua': name,
                'name_en': name,
                'city': city,
                'address': address,
                'short_description': short_description,
                'description': description,
                'founders': founders,
                'curators': curators,
                'artists': artists,
                'email': email,
                'phone': phone,
                'website_url': website_url,
                'founding_year': founding_year,
                'social_links': social_links,
                'image': image_url,
            },
        )
        
        action = 'created' if created else 'updated'
        logger.info(f"Gallery {action}: {gallery.name_ua} [{slug}]")
        
        return Response({
            'status': 'success',
            'action': action,
            'slug': slug,
            'name': gallery.name_ua,
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception("Webhook processing error")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _get_localized_value(field_value, default=''):
    """Отримує значення з локалізованого поля Contentful"""
    if isinstance(field_value, dict):
        # Спробуємо отримати en-US, якщо немає — беремо перше доступне
        if 'en-US' in field_value:
            return field_value['en-US']
        return field_value.get(list(field_value.keys())[0], default) if field_value else default
    return field_value if field_value is not None else default


def _get_image_url_from_webhook(asset_field):
    """Отримує URL картинки з webhook даних Contentful"""
    if not asset_field:
        return ''
    
    try:
        if isinstance(asset_field, dict):
            # Локалізоване поле
            asset = asset_field.get('en-US', asset_field)
            if isinstance(asset, dict):
                file_data = asset.get('fields', {}).get('file', {})
                url = file_data.get('url', '')
                if url and url.startswith('//'):
                    return f'https:{url}'
                return url
        return ''
    except Exception:
        return ''


def _rich_text_to_plain(rich_text):
    """Конвертує Contentful Rich Text JSON у простий текст"""
    if not isinstance(rich_text, dict):
        return str(rich_text)
    
    texts = []
    
    def extract_text(node):
        if isinstance(node, dict):
            if node.get('nodeType') == 'text':
                texts.append(node.get('value', ''))
            for child in node.get('content', []):
                extract_text(child)
        elif isinstance(node, list):
            for child in node:
                extract_text(child)
    
    extract_text(rich_text)
    return '\n'.join(texts)


def _verify_webhook_signature(body, signature, secret):
    """Перевіряє підпис webhook від Contentful"""
    if not signature:
        return False
    expected = hmac.new(
        secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
