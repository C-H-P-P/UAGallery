from django.core.management.base import BaseCommand
from app.models import Gallery, Exhibition, ExhibitionPage
from app.utils.scraper import WebScraper, PlaywrightScraper, InstagramScraper, FacebookScraper
from app.utils.gemini_parser import GeminiParser
import logging
import os
import time
from datetime import datetime
logger = logging.getLogger(__name__)
class Command(BaseCommand):
    help = 'Запускає AI-детектор для моніторингу нових виставок (підтримує сайти, Instagram, Facebook)'
    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None,
                            help='Обробити тільки перші N галерей')
        parser.add_argument('--slug', type=str, default=None,
                            help='Обробити конкретну галерею за slug')
        parser.add_argument('--debug', action='store_true',
                            help='Показувати деталі помилок')
        parser.add_argument('--include-social', action='store_true',
                            help='Включити обробку Instagram і Facebook')
        parser.add_argument('--force', action='store_true',
                            help='Ігнорувати хеші — переобробити всі сторінки')
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('═' * 60))
        self.stdout.write(self.style.SUCCESS('  Запуск AI-детектора виставок'))
        self.stdout.write(self.style.SUCCESS('═' * 60))
        if not os.environ.get('GEMINI_API_KEY'):
            self.stdout.write(self.style.ERROR(
                'GEMINI_API_KEY не знайдено. AI парсинг неможливий.'
            ))
            return
        gemini = GeminiParser()
        debug = bool(options.get('debug'))
        include_social = bool(options.get('include_social'))
        force = bool(options.get('force'))
        galleries_qs = Gallery.objects.exclude(monitoring_url="").order_by('source_type', 'slug')
        if options.get('slug'):
            galleries_qs = galleries_qs.filter(slug=options['slug'])
        total = galleries_qs.count()
        limit = options.get('limit')
        if limit:
            galleries_qs = galleries_qs[:limit]
            count = min(total, limit)
        else:
            count = total
        self.stdout.write(f'Знайдено галерей для моніторингу: {count}\n')
        stats = {'processed': 0, 'skipped': 0, 'exhibitions_created': 0, 'exhibitions_updated': 0, 'errors': 0}
        for gallery in galleries_qs:
            self.stdout.write(f'\n{"─" * 50}')
            self.stdout.write(f'📍 {gallery.name_ua}')
            self.stdout.write(f'   URL: {gallery.monitoring_url}')
            self.stdout.write(f'   Тип: {gallery.source_type or "website"}')
            try:
                created, updated = self._process_gallery(
                    gallery, gemini, debug=debug,
                    include_social=include_social, force=force
                )
                stats['exhibitions_created'] += created
                stats['exhibitions_updated'] += updated
                stats['processed'] += 1
            except Exception as e:
                stats['errors'] += 1
                self.stdout.write(self.style.ERROR(f'   ❌ Критична помилка: {e}'))
                if debug:
                    import traceback
                    self.stdout.write(traceback.format_exc())
        self.stdout.write(f'\n{"═" * 60}')
        self.stdout.write(self.style.SUCCESS('  Сканування завершено!'))
        self.stdout.write(f'  Оброблено галерей:    {stats["processed"]}')
        self.stdout.write(f'  Пропущено:            {stats["skipped"]}')
        self.stdout.write(f'  Виставок створено:    {stats["exhibitions_created"]}')
        self.stdout.write(f'  Виставок оновлено:    {stats["exhibitions_updated"]}')
        if stats['errors']:
            self.stdout.write(self.style.ERROR(f'  Помилок:              {stats["errors"]}'))
        self.stdout.write('═' * 60)
    def _process_gallery(self, gallery, gemini: GeminiParser,
                         debug=False, include_social=False, force=False):
        source_type = (gallery.source_type or "website").lower().strip()
        if source_type in ('instagram', 'facebook') and not include_social:
            self.stdout.write(self.style.WARNING(
                '   ⏭  Соцмережа. Пропускаємо (додай --include-social щоб увімкнути).'
            ))
            return 0, 0
        if source_type == 'instagram':
            return self._process_instagram(gallery, gemini, force=force)
        if source_type == 'facebook':
            return self._process_facebook(gallery, gemini, force=force)
        return self._process_website(gallery, gemini, debug=debug, force=force)
    def _process_website(self, gallery, gemini: GeminiParser, debug=False, force=False):
        url = gallery.monitoring_url
        created_total, updated_total = 0, 0
        scraper = PlaywrightScraper if gallery.needs_js else WebScraper
        scraper_name = "Playwright" if gallery.needs_js else "requests"
        self.stdout.write(f'   Скрапер: {scraper_name}')
        listings_text = self._fetch_text(scraper, url, debug)
        if not listings_text:
            self.stdout.write(self.style.WARNING(f'   ⚠️  Не вдалося отримати текст з {url}'))
            return 0, 0
        self.stdout.write(f'   Отримано текст: {len(listings_text)} символів')
        listings_hash = WebScraper.get_text_hash(listings_text)
        if not force and listings_hash == gallery.last_scraped_hash:
            self.stdout.write('   ✓ Головна сторінка не змінилась. Пропускаємо.')
            return 0, 0
        self.stdout.write('   🔍 Шукаємо посилання на виставки...')
        exhibition_links = gemini.extract_exhibition_links(listings_text, url)
        if exhibition_links:
            self.stdout.write(f'   📋 Знайдено підсторінок: {len(exhibition_links)}')
            created, updated = self._process_exhibition_pages(
                gallery, gemini, exhibition_links, scraper, force=force
            )
            created_total += created
            updated_total += updated
        else:
            self.stdout.write('   ℹ️  Підсторінок не знайдено. Парсимо головну сторінку напряму.')
            created, updated = self._parse_and_save(
                gallery, gemini, listings_text, source_url=url
            )
            created_total += created
            updated_total += updated
        gallery.last_scraped_hash = listings_hash
        gallery.save(update_fields=['last_scraped_hash'])
        return created_total, updated_total
    def _process_exhibition_pages(self, gallery, gemini: GeminiParser,
                                  links: list, scraper, force=False):
        created_total, updated_total = 0, 0
        for link in links:
            self.stdout.write(f'     → {link}')
            page_text = self._fetch_text(scraper, link, debug=False)
            if not page_text:
                self.stdout.write(self.style.WARNING(f'       ⚠️  Не вдалося отримати текст'))
                continue
            current_hash = WebScraper.get_text_hash(page_text)
            page_record, _ = ExhibitionPage.objects.get_or_create(
                url=link,
                defaults={'gallery': gallery, 'last_hash': ''}
            )
            if not force and page_record.last_hash == current_hash:
                self.stdout.write('       ✓ Не змінилась')
                continue
            self.stdout.write('       🤖 Змінилась! Передаємо Gemini...')
            created, updated = self._parse_and_save(
                gallery, gemini, page_text, source_url=link
            )
            created_total += created
            updated_total += updated
            page_record.gallery = gallery
            page_record.last_hash = current_hash
            page_record.save()
            time.sleep(0.5)
        return created_total, updated_total
    def _process_instagram(self, gallery, gemini: GeminiParser, force=False):
        username = gallery.instagram_username.strip()
        if not username and gallery.monitoring_url:
            username = InstagramScraper._extract_username_from_url(gallery.monitoring_url)
        if not username:
            self.stdout.write(self.style.ERROR(
                '   ❌ Не вдалося визначити Instagram username. '
                'Заповни поле instagram_username або monitoring_url.'
            ))
            return 0, 0
        self.stdout.write(f'   Instagram: @{username}')
        text = InstagramScraper.fetch_posts(username)
        if not text:
            self.stdout.write(self.style.WARNING('   ⚠️  Не вдалося отримати пости Instagram'))
            return 0, 0
        current_hash = InstagramScraper.get_text_hash(text)
        if not force and current_hash == gallery.last_scraped_hash:
            self.stdout.write('   ✓ Пости не змінились. Пропускаємо.')
            return 0, 0
        self.stdout.write(f'   Отримано текст: {len(text)} символів. Передаємо Gemini...')
        created, updated = self._parse_and_save(
            gallery, gemini, text, source_url=gallery.monitoring_url
        )
        gallery.last_scraped_hash = current_hash
        gallery.save(update_fields=['last_scraped_hash'])
        return created, updated
    def _process_facebook(self, gallery, gemini: GeminiParser, force=False):
        self.stdout.write(f'   Facebook: {gallery.monitoring_url}')
        text = FacebookScraper.fetch_posts(gallery.monitoring_url)
        if not text:
            self.stdout.write(self.style.WARNING('   ⚠️  Не вдалося отримати пости Facebook'))
            return 0, 0
        current_hash = FacebookScraper.get_text_hash(text)
        if not force and current_hash == gallery.last_scraped_hash:
            self.stdout.write('   ✓ Пости не змінились. Пропускаємо.')
            return 0, 0
        self.stdout.write(f'   Отримано текст: {len(text)} символів. Передаємо Gemini...')
        created, updated = self._parse_and_save(
            gallery, gemini, text, source_url=gallery.monitoring_url
        )
        gallery.last_scraped_hash = current_hash
        gallery.save(update_fields=['last_scraped_hash'])
        return created, updated
    def _parse_and_save(self, gallery, gemini: GeminiParser,
                        text: str, source_url: str = "") -> tuple[int, int]:
        exhibitions_data = gemini.extract_exhibitions(text, gallery.name_ua)
        if not exhibitions_data:
            self.stdout.write('       Gemini не знайшов виставок у тексті.')
            return 0, 0
        self.stdout.write(self.style.SUCCESS(f'       Знайдено виставок: {len(exhibitions_data)}'))
        created_count = 0
        updated_count = 0
        for item in exhibitions_data:
            title = (item.get('title') or '').strip()
            if not title:
                continue
            start_date = self._parse_date(item.get('start_date'))
            end_date = self._parse_date(item.get('end_date'))
            exhibition, created = Exhibition.objects.update_or_create(
                gallery=gallery,
                title=title,
                defaults={
                    'description': item.get('description', ''),
                    'start_date': start_date,
                    'end_date': end_date,
                    'artists': item.get('artists', []),
                    'source_url': source_url,
                    'source_text': text[:5000],
                    'is_active': True,
                }
            )
            action = "✅ Створено" if created else "🔄 Оновлено"
            self.stdout.write(f'       {action}: {title}')
            if created:
                created_count += 1
            else:
                updated_count += 1
        return created_count, updated_count
    @staticmethod
    def _fetch_text(scraper_class, url: str, debug: bool) -> str:
        if scraper_class == WebScraper:
            if debug:
                text, error = WebScraper.fetch_text_from_url(url, return_error=True)
                if error:
                    logger.warning(f"fetch_text error for {url}: {error}")
                return text
            else:
                return WebScraper.fetch_text_from_url(url)
        else:
            return scraper_class.fetch_text_from_url(url)
    @staticmethod
    def _parse_date(date_str):
        if not date_str:
            return None
        try:
            return datetime.strptime(str(date_str).strip(), '%Y-%m-%d').date()
        except ValueError:
            return None
