"""
Management command для синхронізації даних з Contentful у базу даних.

Використання:
  python manage.py sync_contentful           # Синхронізувати всі галереї
  python manage.py sync_contentful --clear   # Очистити БД перед синхронізацією

У Docker:
  docker-compose exec backend python manage.py sync_contentful
"""

import contentful
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from app.models import Gallery

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Синхронізує галереї з Contentful у локальну базу даних (Neon PostgreSQL)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Видалити всі галереї з БД перед синхронізацією',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔄 Починаємо синхронізацію з Contentful...\n')

        # 1. Підключаємось до Contentful
        try:
            client = contentful.Client(
                settings.CONTENTFUL_SPACE_ID,
                settings.CONTENTFUL_ACCESS_TOKEN,
                environment=getattr(settings, 'CONTENTFUL_ENVIRONMENT', 'master'),
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ Помилка підключення до Contentful: {e}'))
            return

        # 2. Забираємо всі записи типу 'project' з Contentful
        try:
            entries = client.entries({
                'content_type': 'project',
                'include': 2,
                'limit': 1000,
            })
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ Помилка отримання даних: {e}'))
            return

        self.stdout.write(f'📦 Знайдено {len(entries)} галерей у Contentful\n')

        if not entries:
            self.stdout.write(self.style.WARNING('⚠️ Contentful порожній, нічого синхронізувати'))
            return

        # 3. Очищаємо БД якщо вказано --clear
        if options['clear']:
            deleted_count, _ = Gallery.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'🗑️  Видалено {deleted_count} старих записів з БД'))

        # 4. Синхронізуємо кожну галерею
        created_count = 0
        updated_count = 0
        error_count = 0

        for item in entries:
            try:
                fields = item.fields()
                contentful_id = item.sys.get('id', '')

                # Визначаємо slug
                slug = fields.get('slug', '')
                if not slug:
                    # Якщо slug порожній — генеруємо з назви
                    name = fields.get('name', contentful_id)
                    slug = slugify(name, allow_unicode=True) or contentful_id

                # Отримуємо URL картинки
                image_url = self._get_image_url(fields.get('coverImage'))

                # Обробка Rich Text (description)
                raw_description = fields.get('description', '')
                if isinstance(raw_description, dict):
                    # Rich Text — конвертуємо в текст
                    description = self._rich_text_to_plain(raw_description)
                else:
                    description = str(raw_description)

                # Обробка social links
                social_links_raw = fields.get('socialLinks', {})
                if social_links_raw is None:
                    social_links_raw = {}
                social_links = social_links_raw.get('links', []) if isinstance(social_links_raw, dict) else []

                # Обробка artists (може бути список або рядок)
                artists_raw = fields.get('artistsList', [])
                if isinstance(artists_raw, list):
                    artists = '\n'.join(str(a) for a in artists_raw)
                else:
                    artists = str(artists_raw) if artists_raw else ''

                # Створюємо або оновлюємо запис в БД (по slug)
                gallery, created = Gallery.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'name_ua': fields.get('name', {}).get('en-US', '') if isinstance(fields.get('name'), dict) else fields.get('name', ''),
                        'name_en': fields.get('name', {}).get('en-US', '') if isinstance(fields.get('name'), dict) else fields.get('name', ''),
                        'city': fields.get('city', {}).get('en-US', '') if isinstance(fields.get('city'), dict) else fields.get('city', ''),
                        'address': fields.get('address', {}).get('en-US', '') if isinstance(fields.get('address'), dict) else fields.get('address', ''),
                        'short_description': fields.get('shortDescription', {}).get('en-US', '') if isinstance(fields.get('shortDescription'), dict) else fields.get('shortDescription', ''),
                        'description': description,
                        'founders': fields.get('founders', {}).get('en-US', '') if isinstance(fields.get('founders'), dict) else fields.get('founders', ''),
                        'curators': fields.get('curators', {}).get('en-US', '') if isinstance(fields.get('curators'), dict) else fields.get('curators', ''),
                        'artists': artists,
                        'email': fields.get('email', {}).get('en-US', '') if isinstance(fields.get('email'), dict) else fields.get('email', ''),
                        'phone': fields.get('phone', {}).get('en-US', '') if isinstance(fields.get('phone'), dict) else fields.get('phone', ''),
                        'website_url': fields.get('websiteUrl', {}).get('en-US', '') if isinstance(fields.get('websiteUrl'), dict) else fields.get('websiteUrl', ''),
                        'founding_year': fields.get('foundingYear', {}).get('en-US') if isinstance(fields.get('foundingYear'), dict) else fields.get('foundingYear'),
                        'social_links': social_links,
                        'image': image_url,
                    },
                )

                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Створено: {gallery.name_ua} [{slug}]'))
                else:
                    updated_count += 1
                    self.stdout.write(f'  🔄 Оновлено: {gallery.name_ua} [{slug}]')

            except Exception as e:
                error_count += 1
                entry_id = item.sys.get('id', '???')
                self.stderr.write(self.style.ERROR(f'  ❌ Помилка для {entry_id}: {e}'))
                logger.exception(f'Sync error for entry {entry_id}')

        # 5. Підсумок
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'✅ Синхронізація завершена!'))
        self.stdout.write(f'   📥 Створено: {created_count}')
        self.stdout.write(f'   🔄 Оновлено: {updated_count}')
        if error_count:
            self.stdout.write(self.style.ERROR(f'   ❌ Помилок: {error_count}'))
        self.stdout.write(f'   📊 Всього в БД: {Gallery.objects.count()}')

    def _get_image_url(self, asset):
        """Отримує URL картинки з об'єкта Contentful Asset"""
        if not asset:
            return ''
        try:
            if hasattr(asset, 'url'):
                url = asset.url()
            else:
                url = asset.fields().get('file', {}).get('url', '')

            if url and url.startswith('//'):
                return f'https:{url}'
            return url or ''
        except Exception:
            return ''

    def _rich_text_to_plain(self, rich_text):
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
