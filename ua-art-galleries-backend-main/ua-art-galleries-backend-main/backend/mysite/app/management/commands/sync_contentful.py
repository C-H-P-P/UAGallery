import contentful
import logging
import re

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

        # 2. Забираємо всі записи типу 'project' з Contentful у всіх локалях
        try:
            entries = client.entries({
                'content_type': 'project',
                'include': 2,
                'limit': 1000,
                'locale': '*'
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
                # Отримуємо raw поля (json від Contentful) де локалі знаходяться в саб-об'єктах
                fields = item.raw.get('fields', {})
                contentful_id = item.sys.get('id', '')
                
                # Допоміжна функція для витягування локалізованих полів
                def _get_lang(field_dict, lang, default=''):
                    if isinstance(field_dict, dict):
                        return field_dict.get(lang, field_dict.get('en-US', default))
                    return field_dict if field_dict is not None else default

                # Визначаємо slug
                slug_field = fields.get('slug', {})
                slug = _get_lang(slug_field, 'en-US', '')
                if not slug:
                    name_field = fields.get('name', {})
                    name_fallback = _get_lang(name_field, 'en-US', contentful_id)
                    slug = slugify(name_fallback, allow_unicode=True) or contentful_id

                # Отримуємо URL картинки (через resolved fields від SDK)
                try:
                    resolved_fields = item.fields() or {}
                    cover_asset = resolved_fields.get('coverImage', resolved_fields.get('cover_image'))
                except Exception:
                    cover_asset = None
                image_url = self._get_image_url(cover_asset)

                # Обробка Rich Text (description) для обох локалей
                raw_description = fields.get('description', {})
                def _get_rich_text_lang(rt, lang):
                    if isinstance(rt, dict):
                        val = rt.get(lang, rt)
                        if isinstance(val, dict):
                            return self._rich_text_to_plain(val)
                        return str(val)
                    return str(rt) if rt else ''
                
                description_ua = _get_rich_text_lang(raw_description, 'uk')
                description_en = _get_rich_text_lang(raw_description, 'en-US')

             
                social_links_raw = fields.get('socialLinks', {})
                social_links_val = _get_lang(social_links_raw, 'en-US', {})
                social_links = social_links_val.get('links', []) if isinstance(social_links_val, dict) else []

                # Обробка artists
                artists_data = fields.get('artistsList', fields.get('artists_list', {}))
                artists_ua_raw = _get_lang(artists_data, 'uk', [])
                artists_en_raw = _get_lang(artists_data, 'en-US', [])
                artists_ua = '\n'.join(str(a) for a in artists_ua_raw) if isinstance(artists_ua_raw, list) else str(artists_ua_raw)
                artists_en = '\n'.join(str(a) for a in artists_en_raw) if isinstance(artists_en_raw, list) else str(artists_en_raw)

                # Отримуємо статус
                status_val = _get_lang(fields.get('status', {}), 'en-US', True)
                status_bool = bool(status_val) if status_val is not None else True

         
                gallery, created = Gallery.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'name_ua': _get_lang(fields.get('name'), 'uk', ''),
                        'name_en': _get_lang(fields.get('name'), 'en-US', ''),
                        'city_ua': _get_lang(fields.get('city'), 'uk', ''),
                        'city_en': _get_lang(fields.get('city'), 'en-US', ''),
                        'address_ua': _get_lang(fields.get('address'), 'uk', ''),
                        'address_en': _get_lang(fields.get('address'), 'en-US', ''),
                        'short_description_ua': _get_lang(fields.get('shortDescription', fields.get('short_description', {})), 'uk', ''),
                        'short_description_en': _get_lang(fields.get('shortDescription', fields.get('short_description', {})), 'en-US', ''),
                        'specialization_ua': _get_lang(fields.get('specialization', {}), 'uk', ''),
                        'specialization_en': _get_lang(fields.get('specialization', {}), 'en-US', ''),
                        'description_ua': description_ua,
                        'description_en': description_en,
                        'founders_ua': _get_lang(fields.get('founders'), 'uk', ''),
                        'founders_en': _get_lang(fields.get('founders'), 'en-US', ''),
                        'curators_ua': _get_lang(fields.get('curators'), 'uk', ''),
                        'curators_en': _get_lang(fields.get('curators'), 'en-US', ''),
                        'artists_ua': artists_ua,
                        'artists_en': artists_en,
                        'status': status_bool,
                        'email': _get_lang(fields.get('email'), 'en-US', ''),
                        'phone': _get_lang(fields.get('phone'), 'en-US', ''),
                        'website_url': _get_lang(fields.get('websiteUrl', fields.get('website_url', {})), 'en-US', ''),
                        'founding_year': self._extract_year(_get_lang(fields.get('foundingYear', fields.get('founding_year', {})), 'en-US', None)),
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

        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'✅ Синхронізація завершена!'))
        self.stdout.write(f'   📥 Створено: {created_count}')
        self.stdout.write(f'   🔄 Оновлено: {updated_count}')
        if error_count:
            self.stdout.write(self.style.ERROR(f'   ❌ Помилок: {error_count}'))
        self.stdout.write(f'   📊 Всього в БД: {Gallery.objects.count()}')

    def _extract_year(self, year_value):
        """Витягує 4-значне число (рік) з рядка, наприклад '2005(Дубай)' → 2005"""
        if not year_value or year_value == '-':
            return None
        if isinstance(year_value, int):
            return year_value
        # Шукаємо 4-значне число в рядку
        import re
        match = re.search(r'\b(19|20)\d{2}\b', str(year_value))
        if match:
            return int(match.group(0))
        return None

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
