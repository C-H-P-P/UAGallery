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
        results = []
        limit = 1000  # Максимальний ліміт Contentful API
        skip = 0
        total_fetched = 0
        
        # Пагінація: отримуємо всі галереї порціями
        while True:
            # include=1 дозволяє зразу підтягнути пов'язані картинки, щоб не було помилок
            entries = client.entries({
                'content_type': 'project', 
                'include': 1, 
                'limit': limit,
                'skip': skip
            })
            
            # Якщо нічого не прийшло, виходимо з циклу
            if not entries or len(entries) == 0:
                break
            
            for item in entries:
                fields = item.fields()
                
                # Обробка картинки
                cover_image = fields.get('coverImage')
                image_url = _get_image_url(cover_image)

                # Обробка JSON поля socialLinks
                social_links = fields.get('socialLinks', {})
                if social_links is None: 
                    social_links = {}
                
                results.append({
                    "id": item.sys.get('id'),
                    "slug": fields.get('slug', ''),
                    "status": True,  # За замовчуванням активна, якщо немає поля в Contentful
                    "name_ua": fields.get('name', ''),  # Припускаємо, що name - це UA
                    "name_en": fields.get('name', ''),  # Якщо немає окремого EN поля
                    "image": image_url,
                    "cover_image": image_url,
                    "short_description_ua": fields.get('shortDescription', ''),
                    "short_description_en": fields.get('shortDescription', ''),
                    "full_description_ua": fields.get('description', ''),
                    "full_description_en": fields.get('description', ''),
                    "specialization_ua": fields.get('specialization', ''),
                    "specialization_en": fields.get('specialization', ''),
                    "city_ua": fields.get('city', ''),
                    "city_en": fields.get('city', ''),
                    "address_ua": fields.get('address', ''),
                    "address_en": fields.get('address', ''),
                    "founders_ua": fields.get('founders', ''),
                    "founders_en": fields.get('founders', ''),
                    "curators_ua": fields.get('curators', ''),
                    "curators_en": fields.get('curators', ''),
                    "artists_ua": fields.get('artists', ''),
                    "artists_en": fields.get('artists', ''),
                    "email": fields.get('email', ''),
                    "phone": fields.get('phone', ''),
                    "website": fields.get('websiteUrl', ''),
                    "social_links": social_links,
                    "founding_year": str(fields.get('foundingYear', '')) if fields.get('foundingYear') else '',
                    "created_at": item.sys.get('created_at'),
                    "updated_at": item.sys.get('updated_at')
                })
            
            total_fetched = len(entries)
            logger.info(f"✅ Fetched {total_fetched} galleries (skip={skip})")
            
            # Якщо отримали меншеніж ліміт, значить це остання сторінка
            if total_fetched < limit:
                break
                
            # Переходимо до наступної сторінки
            skip += limit
        
        logger.info(f"✅ Total galleries fetched: {len(results)}")
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
        
        # Обробка картинки
        cover_image = fields.get('coverImage')
        image_url = _get_image_url(cover_image)
        
        # Обробка JSON поля socialLinks
        social_links = fields.get('socialLinks', {})
        if social_links is None: 
            social_links = {}

        return {
            "id": item.sys.get('id'),
            "slug": fields.get('slug', ''),
            "status": True,
            "name_ua": fields.get('name', ''),
            "name_en": fields.get('name', ''),
            "image": image_url,
            "cover_image": image_url,
            "short_description_ua": fields.get('shortDescription', ''),
            "short_description_en": fields.get('shortDescription', ''),
            "full_description_ua": fields.get('description', ''),
            "full_description_en": fields.get('description', ''),
            "specialization_ua": fields.get('specialization', ''),
            "specialization_en": fields.get('specialization', ''),
            "city_ua": fields.get('city', ''),
            "city_en": fields.get('city', ''),
            "address_ua": fields.get('address', ''),
            "address_en": fields.get('address', ''),
            "founders_ua": fields.get('founders', ''),
            "founders_en": fields.get('founders', ''),
            "curators_ua": fields.get('curators', ''),
            "curators_en": fields.get('curators', ''),
            "artists_ua": fields.get('artists', ''),
            "artists_en": fields.get('artists', ''),
            "email": fields.get('email', ''),
            "phone": fields.get('phone', ''),
            "website": fields.get('websiteUrl', ''),
            "social_links": social_links,
            "founding_year": str(fields.get('foundingYear', '')) if fields.get('foundingYear') else '',
            "created_at": item.sys.get('created_at'),
            "updated_at": item.sys.get('updated_at')
        }
    except Exception as e:
        logger.error(f"❌ Error fetching gallery by slug '{slug}': {e}")
        return None