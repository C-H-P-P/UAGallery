import contentful
from django.conf import settings
import logging

# Налаштовуємо логування, щоб бачити помилки в консолі Docker
logger = logging.getLogger(__name__)

# 1. Ініціалізація клієнта
# Беремо налаштування з settings.py (переконайся, що вони там є)
try:
    client = contentful.Client(
        settings.CONTENTFUL_SPACE_ID,
        settings.CONTENTFUL_ACCESS_TOKEN,
        environment=getattr(settings, 'CONTENTFUL_ENVIRONMENT', 'master') # За замовчуванням master
    )
except Exception as e:
    logger.error(f"❌ Contentful Connection Error: {e}")
    client = None

def _get_image_url(asset):
    """Допоміжна функція для витягування URL картинки з об'єкта Contentful Asset"""
    if not asset:
        return None
    try:
        # SDK повертає об'єкт, у якого є метод url(), або треба лізти в поля
        # Спробуємо надійний метод:
        if hasattr(asset, 'url'):
            url = asset.url()
        else:
            # Якщо це "сирий" об'єкт
            url = asset.fields().get('file', {}).get('url')

        # Contentful часто віддає посилання без протоколу (наприклад //images.ctfassets.net...)
        if url and url.startswith('//'):
            return f'https:{url}'
        return url
    except Exception as e:
        logger.warning(f"⚠️ Error parsing image URL: {e}")
        return None

def fetch_all_galleries():
    """Отримує всі галереї (проекти) і формує чистий список"""
    if not client:
        return []

    try:
        # include=1 дозволяє зразу підтягнути пов'язані картинки, щоб не було помилок
        entries = client.entries({'content_type': 'project', 'include': 1})
        results = []

        for item in entries:
            fields = item.fields()
            
            # Обробка картинки
            cover_image = fields.get('coverImage')
            image_url = _get_image_url(cover_image)

            # Обробка JSON поля socialLinks (якщо воно пусте — повертаємо пустий список)
            social_links = fields.get('socialLinks', {})
            if social_links is None: 
                social_links = {}
            
            results.append({
                "id": item.sys.get('id'),
                "name": fields.get('name', ''),
                "slug": fields.get('slug', ''),
                "city": fields.get('city', ''),
                "address": fields.get('address', ''),
                "image": image_url,
                # Тут структура залежить від того, як ти заповнюєш JSON в адмінці Contentful
                "socials": social_links.get('links', []), 
                "short_desc": fields.get('shortDescription', ''),
                "year": fields.get('foundingYear')
            })
        return results
    except Exception as e:
        logger.error(f"❌ Error fetching galleries: {e}")
        return []

def fetch_gallery_by_slug(slug: str):
    """Шукає одну конкретну галерею за посиланням (slug)"""
    if not client:
        return None
        
    try:
        entries = client.entries({
            'content_type': 'project', 
            'fields.slug': slug,
            'limit': 1,
            'include': 2 # Глибина вкладеності (якщо всередині є інші зв'язки)
        })
        
        if not entries:
            return None
            
        item = entries[0]
        fields = item.fields()

        return {
            "name": fields.get('name', ''),
            "description": fields.get('description', {}), # Поверне Rich Text JSON
            "founders": fields.get('founders', ''),
            "curators": fields.get('curators', ''),
            "artists": fields.get('artistsList', []), # Це може бути список імен або зв'язаних об'єктів
            "contacts": {
                "email": fields.get('email', ''),
                "phone": fields.get('phone', ''),
                "website": fields.get('websiteUrl', '')
            },
             # Додаємо картинку і сюди, раптом треба на сторінці деталізації
            "image": _get_image_url(fields.get('coverImage'))
        }
    except Exception as e:
        logger.error(f"❌ Error fetching gallery by slug '{slug}': {e}")
        return None