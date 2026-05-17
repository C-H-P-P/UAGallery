import hashlib
import hmac
import json
import logging
import re
import time

from django.conf import settings
from django.http import JsonResponse
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, generics
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from deep_translator import GoogleTranslator

from .models import Gallery, FavoriteGallery, Review, Exhibition
from .serializers import GalleryListSerializer, GalleryDetailSerializer, ReviewSerializer

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


class FavoriteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = FavoriteGallery.objects.filter(user=request.user).values_list('gallery__slug', flat=True)
        return Response({'favorites': list(favorites)})


class FavoriteToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        slug = request.data.get('slug')
        if not slug:
            return Response({'error': 'slug is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        gallery = get_object_or_404(Gallery, slug=slug)
        favorite, created = FavoriteGallery.objects.get_or_create(user=request.user, gallery=gallery)
        
        if not created:
            favorite.delete()
            return Response({'detail': 'Removed from favorites', 'is_favorite': False}, status=status.HTTP_200_OK)
        
        return Response({'detail': 'Added to favorites', 'is_favorite': True}, status=status.HTTP_200_OK)


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET /api/galleries/<slug>/reviews/ - Отримати всі відгуки до галереї (доступно всім)
    POST /api/galleries/<slug>/reviews/ - Додати відгук (тільки для авторизованих)
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        gallery = get_object_or_404(Gallery, slug=slug)
        return Review.objects.filter(gallery=gallery).select_related('user')

    def perform_create(self, serializer):
        slug = self.kwargs.get('slug')
        gallery = get_object_or_404(Gallery, slug=slug)
        
        # Перевірка: чи не залишав вже користувач відгук на цю галерею
        if Review.objects.filter(user=self.request.user, gallery=gallery).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Ви вже залишили відгук для цієї галереї."})
            
        serializer.save(user=self.request.user, gallery=gallery)


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
        def _get_rich_text_lang(rt, lang):
            if isinstance(rt, dict):
                val = rt.get(lang, rt)
                if isinstance(val, dict):
                    return _rich_text_to_plain(val)
                return str(val)
            return str(rt) if rt else ''
        
        desc_ua = _get_rich_text_lang(raw_description, 'uk')
        desc_en = _get_rich_text_lang(raw_description, 'en-US')
        
        # Обробка social links
        social_links_raw = fields.get('socialLinks', {})
        if isinstance(social_links_raw, dict):
            social_links_raw = social_links_raw.get('en-US', {})
        if social_links_raw is None:
            social_links_raw = {}
        social_links = social_links_raw.get('links', []) if isinstance(social_links_raw, dict) else []
        
        # Отримуємо значення полів для двох мов
        def _get_lang(field, lang, default=''):
            if isinstance(field, dict):
                return field.get(lang, field.get('en-US', default))
            return field if field is not None else default

        name_ua_raw = _get_lang(fields.get('name'), 'uk', '')
        name_en_raw = _get_lang(fields.get('name'), 'en-US', '')
        city_ua_raw = _get_lang(fields.get('city'), 'uk', '')
        city_en_raw = _get_lang(fields.get('city'), 'en-US', '')
        address_ua_raw = _get_lang(fields.get('address'), 'uk', '')
        address_en_raw = _get_lang(fields.get('address'), 'en-US', '')
        short_desc_ua_raw = _get_lang(fields.get('shortDescription', fields.get('short_description', {})), 'uk', '')
        short_desc_en_raw = _get_lang(fields.get('shortDescription', fields.get('short_description', {})), 'en-US', '')
        founders_ua_raw = _get_lang(fields.get('founders'), 'uk', '')
        founders_en_raw = _get_lang(fields.get('founders'), 'en-US', '')
        curators_ua_raw = _get_lang(fields.get('curators'), 'uk', '')
        curators_en_raw = _get_lang(fields.get('curators'), 'en-US', '')

        # Обробка artists
        artists_data = fields.get('artistsList', {})
        artists_ua_raw = _get_lang(artists_data, 'uk', [])
        artists_en_raw = _get_lang(artists_data, 'en-US', [])
        artists_ua_raw = '\n'.join(str(a) for a in artists_ua_raw) if isinstance(artists_ua_raw, list) else str(artists_ua_raw)
        artists_en_raw = '\n'.join(str(a) for a in artists_en_raw) if isinstance(artists_en_raw, list) else str(artists_en_raw)

        email = _get_localized_value(fields.get('email'), '')
        phone = _get_localized_value(fields.get('phone'), '')
        website_url = _get_localized_value(fields.get('websiteUrl'), '')
        founding_year = _get_localized_value(fields.get('foundingYear'), None)
        status_val = _get_localized_value(fields.get('status'), True)
        specialization_ua_raw = _get_lang(fields.get('specialization', {}), 'uk', '')
        specialization_en_raw = _get_lang(fields.get('specialization', {}), 'en-US', '')

        # --- АВТОМАТИЧНИЙ ПЕРЕКЛАД ---
        def has_cyrillic(text):
            return bool(re.search('[а-яА-ЯёЁіІїЇєЄґҐ]', str(text)))

        def smart_translate(uk_text, en_text, is_address=False):
            u = str(uk_text).strip() if uk_text else ''
            e = str(en_text).strip() if en_text else ''

            if not u and e and has_cyrillic(e):
                u, e = e, ''

            if not u or u == '-':
                return u, e

            if e and not has_cyrillic(e):
                return u, e

            text_to_translate = u
            if is_address:
                text_to_translate = u.replace('вул.', 'vul.').replace('просп.', 'prosp.').replace('пров.', 'prov.')

            for attempt in range(3):
                try:
                    translated = GoogleTranslator(source='uk', target='en').translate(text_to_translate)
                    if is_address and translated:
                        translated = translated.replace('vul.', 'St.').replace('prosp.', 'Ave.').replace('prov.', 'Ln.')
                    time.sleep(1.0)
                    return u, translated or e or ''
                except Exception as ex:
                    wait = (attempt + 1) * 3
                    logger.warning(f"Webhook translate attempt {attempt+1} failed: {ex}. Waiting {wait}s...")
                    time.sleep(wait)

            logger.error(f"Webhook translate completely failed for: '{u}'")
            return u, ''

        name_ua, name_en = smart_translate(name_ua_raw, name_en_raw)
        city_ua, city_en = smart_translate(city_ua_raw, city_en_raw)
        address_ua, address_en = smart_translate(address_ua_raw, address_en_raw, is_address=True)
        short_desc_ua, short_desc_en = smart_translate(short_desc_ua_raw, short_desc_en_raw)
        specialization_ua, specialization_en = smart_translate(specialization_ua_raw, specialization_en_raw)
        desc_ua_res, desc_en_res = smart_translate(desc_ua, desc_en)
        founders_ua, founders_en = smart_translate(founders_ua_raw, founders_en_raw)
        curators_ua, curators_en = smart_translate(curators_ua_raw, curators_en_raw)
        artists_ua, artists_en = smart_translate(artists_ua_raw, artists_en_raw)
        
        # Моніторинг та AI
        monitoring_url = _get_localized_value(fields.get('monitoringUrl'), '')
        source_type = _get_localized_value(fields.get('sourceType'), '')
        
        # Зберігання в базу
        gallery, created = Gallery.objects.update_or_create(
            slug=slug,
            defaults={
                'name_ua': name_ua,
                'name_en': name_en,
                'status': bool(status_val) if status_val is not None else True,
                'city_ua': city_ua,
                'city_en': city_en,
                'address_ua': address_ua,
                'address_en': address_en,
                'short_description_ua': short_desc_ua,
                'short_description_en': short_desc_en,
                'specialization_ua': specialization_ua,
                'specialization_en': specialization_en,
                'description_ua': desc_ua_res,
                'description_en': desc_en_res,
                'founders_ua': founders_ua,
                'founders_en': founders_en,
                'curators_ua': curators_ua,
                'curators_en': curators_en,
                'artists_ua': artists_ua,
                'artists_en': artists_en,
                'email': email,
                'phone': phone,
                'website_url': website_url,
                'founding_year': founding_year,
                'social_links': social_links,
                'image': image_url,
                'monitoring_url': monitoring_url,
                'source_type': source_type,
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


import os
import sys
import traceback
from io import StringIO
from django.http import HttpResponse
from django.conf import settings
from django.core.management import call_command
import hmac
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def run_csv_import_view(request):
    """
    Секретний ендпоінт для імпорту CSV без доступу до Shell.
    Використання: /api/system/import-csv/?secret=ВАШ_СЕКРЕТ
    """
    secret = request.GET.get('secret')
    expected_secret = os.environ.get('SYSTEM_ENDPOINT_SECRET') or getattr(settings, 'SYSTEM_ENDPOINT_SECRET', '')
    if not expected_secret:
        return HttpResponse("Service misconfigured", status=503)
    if not secret or not hmac.compare_digest(str(secret), str(expected_secret)):
        return HttpResponse("Unauthorized", status=401)
        
    try:
        # Шукаємо файл
        base_dir = settings.BASE_DIR
        csv_path_1 = os.path.join(base_dir, 'galleries.csv')
        csv_path_2 = os.path.join(os.path.dirname(base_dir), 'galleries.csv')
        
        actual_path = None
        if os.path.exists(csv_path_1):
            actual_path = csv_path_1
        elif os.path.exists(csv_path_2):
            actual_path = csv_path_2
            
        if not actual_path:
            return HttpResponse(f"Помилка: Файл galleries.csv не знайдено ні в {csv_path_1}, ні в {csv_path_2}", status=404)
            
        # Робимо імпорт
        out = StringIO()
        
        # Передаємо stdout напряму в call_command
        call_command('import_urls', actual_path, stdout=out, stderr=out)
        
        result = out.getvalue()
        return HttpResponse(f"<pre>{result}</pre>")
        
    except Exception as e:
        error_details = traceback.format_exc()
        return HttpResponse(f"Internal Error:\n<pre>{error_details}</pre>", status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def run_ai_detector_view(request):
    """
    Секретний ендпоінт для запуску AI-детектора без доступу до Shell.
    Використання: /api/system/run-detector/?secret=ВАШ_СЕКРЕТ
    """
    secret = request.GET.get('secret')
    expected_secret = os.environ.get('SYSTEM_ENDPOINT_SECRET') or getattr(settings, 'SYSTEM_ENDPOINT_SECRET', '')
    if not expected_secret:
        from django.http import HttpResponse
        return HttpResponse("Service misconfigured", status=503)
    if not secret or not hmac.compare_digest(str(secret), str(expected_secret)):
        from django.http import HttpResponse
        return HttpResponse("Unauthorized", status=401)
        
    try:
        from io import StringIO
        from django.http import HttpResponse
        from django.core.management import call_command
        import traceback
        
        out = StringIO()
        kwargs = {}
        limit = request.GET.get('limit')
        slug = request.GET.get('slug')
        if limit:
            try:
                kwargs['limit'] = int(limit)
            except ValueError:
                return HttpResponse("Invalid limit", status=400)
        if slug:
            kwargs['slug'] = slug

        call_command('run_detector', stdout=out, stderr=out, **kwargs)
        result = out.getvalue()
        
        return HttpResponse(f"<pre>{result}</pre>")
    except Exception as e:
        from django.http import HttpResponse
        import traceback
        error_details = traceback.format_exc()
        return HttpResponse(f"Internal Error:\n<pre>{error_details}</pre>", status=500)


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
