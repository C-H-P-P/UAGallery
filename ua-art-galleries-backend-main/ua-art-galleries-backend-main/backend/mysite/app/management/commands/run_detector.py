from django.core.management.base import BaseCommand
from app.models import Gallery, Exhibition, ExhibitionPage
from app.utils.scraper import WebScraper, PlaywrightScraper, InstagramScraper, FacebookScraper
from app.utils.gemini_parser import GeminiParser
import logging
import os
import time
from datetime import datetime

logger = logging.getLogger(__name__)

# Скільки найновіших виставок зберігати з однієї галереї за один прогін
MAX_EXHIBITIONS_PER_GALLERY = 3


class Command(BaseCommand):
    help = 'Запускає AI-детектор для моніторингу нових виставок'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None)
        parser.add_argument('--slug', type=str, default=None)
        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--include-social', action='store_true')
        parser.add_argument('--force', action='store_true',
                            help='Ігнорувати хеші — переобробити всі сторінки')
        parser.add_argument('--max-exhibitions', type=int, default=MAX_EXHIBITIONS_PER_GALLERY,
                            help='Скільки виставок брати з однієї галереї (default: 3)')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('  Запуск AI-детектора виставок'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        if not os.environ.get('GEMINI_API_KEY'):
            self.stdout.write(self.style.ERROR('GEMINI_API_KEY не знайдено.'))
            return

        gemini = GeminiParser()
        debug = bool(options.get('debug'))
        include_social = bool(options.get('include_social'))
        force = bool(options.get('force'))
        max_exhibitions = options.get('max_exhibitions') or MAX_EXHIBITIONS_PER_GALLERY

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

        self.stdout.write(f'Знайдено галерей: {count}\n')
        stats = {'processed': 0, 'skipped': 0, 'created': 0, 'updated': 0, 'errors': 0}

        for gallery in galleries_qs:
            self.stdout.write(f'\n{"-" * 50}')
            self.stdout.write(f'📍 {gallery.name_ua}')
            self.stdout.write(f'   URL: {gallery.monitoring_url}')
            self.stdout.write(f'   Тип: {gallery.source_type or "website"}')
            try:
                created, updated = self._process_gallery(
                    gallery, gemini,
                    debug=debug, include_social=include_social,
                    force=force, max_exhibitions=max_exhibitions
                )
                stats['created'] += created
                stats['updated'] += updated
                stats['processed'] += 1
            except Exception as e:
                stats['errors'] += 1
                self.stdout.write(self.style.ERROR(f'   ❌ Критична помилка: {e}'))
                if debug:
                    import traceback
                    self.stdout.write(traceback.format_exc())

        self.stdout.write(f'\n{"=" * 60}')
        self.stdout.write(self.style.SUCCESS('  Сканування завершено!'))
        self.stdout.write(f'  Оброблено:         {stats["processed"]}')
        self.stdout.write(f'  Виставок створено: {stats["created"]}')
        self.stdout.write(f'  Виставок оновлено: {stats["updated"]}')
        if stats['errors']:
            self.stdout.write(self.style.ERROR(f'  Помилок:           {stats["errors"]}'))
        self.stdout.write('=' * 60)

    # =========================================================================
    # Диспетчер
    # =========================================================================

    def _process_gallery(self, gallery, gemini, debug=False,
                         include_social=False, force=False, max_exhibitions=3):
        source_type = (gallery.source_type or "website").lower().strip()

        if source_type in ('instagram', 'facebook') and not include_social:
            self.stdout.write(self.style.WARNING(
                '   ⏭  Соцмережа. Пропускаємо (--include-social щоб увімкнути).'))
            return 0, 0

        if source_type == 'instagram':
            return self._process_instagram(gallery, gemini, force=force,
                                           max_exhibitions=max_exhibitions)
        if source_type == 'facebook':
            return self._process_facebook(gallery, gemini, force=force,
                                          max_exhibitions=max_exhibitions)

        return self._process_website(gallery, gemini, debug=debug,
                                     force=force, max_exhibitions=max_exhibitions)

    # =========================================================================
    # Стратегія: Website
    # =========================================================================

    def _process_website(self, gallery, gemini, debug=False, force=False, max_exhibitions=3):
        url = gallery.monitoring_url
        scraper = PlaywrightScraper if gallery.needs_js else WebScraper
        self.stdout.write(f'   Скрапер: {"Playwright" if gallery.needs_js else "requests"}')

        # --- Крок 1: отримати текст сторінки ---
        listings_text = self._fetch_text(scraper, url, debug)
        if not listings_text:
            self.stdout.write(self.style.WARNING(f'   ⚠️  Не вдалося отримати текст з {url}'))
            return 0, 0

        self.stdout.write(f'   Отримано: {len(listings_text)} символів')

        # --- Крок 2: перевірка хешу (чи взагалі щось змінилось) ---
        listings_hash = WebScraper.get_text_hash(listings_text)
        if not force and listings_hash == gallery.last_scraped_hash:
            self.stdout.write('   ✓ Сторінка не змінилась. Пропускаємо.')
            return 0, 0

        # --- Крок 3: Gemini аналізує структуру сторінки ---
        self.stdout.write('   🔍 Аналізуємо структуру...')
        extracted = gemini.extract_exhibition_links(listings_text, url)

        parse_directly = extracted.get('parse_listing_directly', False)
        index_pages = extracted.get('index_pages', [])
        exhibition_pages = extracted.get('exhibition_pages', [])

        created_total, updated_total = 0, 0

        # --- Сценарій А: сторінка вже є списком виставок ---
        if parse_directly:
            self.stdout.write('   📋 Сторінка-список → парсимо напряму (без підсторінок)')
            created, updated = self._parse_and_save(
                gallery, gemini, listings_text,
                source_url=url, max_exhibitions=max_exhibitions
            )
            created_total += created
            updated_total += updated

        # --- Сценарій Б: є прямі посилання на конкретні виставки ---
        elif exhibition_pages:
            self.stdout.write(f'   📋 Знайдено підсторінок виставок: {len(exhibition_pages)}')
            # Беремо тільки перші N — найновіші (Gemini повертає в порядку зверху вниз)
            pages_to_check = exhibition_pages[:max_exhibitions]
            if len(exhibition_pages) > max_exhibitions:
                self.stdout.write(f'   ℹ️  Обробляємо тільки перші {max_exhibitions} (найновіші)')
            created, updated = self._process_exhibition_pages(
                gallery, gemini, pages_to_check, scraper,
                force=force, max_exhibitions=max_exhibitions
            )
            created_total += created
            updated_total += updated

        # --- Сценарій В: є посилання на розділ виставок (треба зайти глибше) ---
        elif index_pages:
            index_url = index_pages[0]
            self.stdout.write(f'   🔀 Знайдено розділ виставок: {index_url}')
            index_text = self._fetch_text(scraper, index_url, debug)
            if index_text:
                # Повторно аналізуємо вже сторінку розділу
                extracted2 = gemini.extract_exhibition_links(index_text, index_url)
                if extracted2.get('parse_listing_directly'):
                    self.stdout.write('   📋 Розділ є списком → парсимо напряму')
                    created, updated = self._parse_and_save(
                        gallery, gemini, index_text,
                        source_url=index_url, max_exhibitions=max_exhibitions
                    )
                elif extracted2.get('exhibition_pages'):
                    pages = extracted2['exhibition_pages'][:max_exhibitions]
                    self.stdout.write(f'   📋 Знайдено підсторінок у розділі: {len(pages)}')
                    created, updated = self._process_exhibition_pages(
                        gallery, gemini, pages, scraper,
                        force=force, max_exhibitions=max_exhibitions
                    )
                else:
                    # Останній fallback — парсимо що є
                    self.stdout.write('   ℹ️  Парсимо розділ напряму (fallback)')
                    created, updated = self._parse_and_save(
                        gallery, gemini, index_text,
                        source_url=index_url, max_exhibitions=max_exhibitions
                    )
                created_total += created
                updated_total += updated

        # --- Сценарій Г: нічого не знайдено — парсимо головну напряму ---
        else:
            self.stdout.write('   ℹ️  Структура не визначена → парсимо сторінку напряму (fallback)')
            created, updated = self._parse_and_save(
                gallery, gemini, listings_text,
                source_url=url, max_exhibitions=max_exhibitions
            )
            created_total += created
            updated_total += updated

        # Оновлюємо хеш головної сторінки
        gallery.last_scraped_hash = listings_hash
        gallery.save(update_fields=['last_scraped_hash'])

        return created_total, updated_total

    def _process_exhibition_pages(self, gallery, gemini, links, scraper,
                                  force=False, max_exhibitions=3):
        """Обходить список підсторінок, перевіряє хеш кожної, парсить змінені."""
        created_total, updated_total = 0, 0

        for link in links:
            self.stdout.write(f'     → {link}')
            page_text = self._fetch_text(scraper, link, debug=False)
            if not page_text:
                self.stdout.write(self.style.WARNING('       ⚠️  Не вдалося отримати текст'))
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
            # Одна підсторінка = одна виставка, тому max=1
            created, updated = self._parse_and_save(
                gallery, gemini, page_text, source_url=link, max_exhibitions=1
            )
            created_total += created
            updated_total += updated

            page_record.gallery = gallery
            page_record.last_hash = current_hash
            page_record.save()

            time.sleep(0.5)

        return created_total, updated_total

    # =========================================================================
    # Стратегія: Instagram
    # =========================================================================

    def _process_instagram(self, gallery, gemini, force=False, max_exhibitions=3):
        username = gallery.instagram_username.strip()
        if not username and gallery.monitoring_url:
            username = InstagramScraper._extract_username_from_url(gallery.monitoring_url)
        if not username:
            self.stdout.write(self.style.ERROR('   ❌ Instagram username не визначено.'))
            return 0, 0

        self.stdout.write(f'   Instagram: @{username}')
        text = InstagramScraper.fetch_posts(username)
        if not text:
            self.stdout.write(self.style.WARNING('   ⚠️  Не вдалося отримати пости'))
            return 0, 0

        current_hash = InstagramScraper.get_text_hash(text)
        if not force and current_hash == gallery.last_scraped_hash:
            self.stdout.write('   ✓ Пости не змінились.')
            return 0, 0

        self.stdout.write(f'   {len(text)} символів → Gemini...')
        created, updated = self._parse_and_save(
            gallery, gemini, text,
            source_url=gallery.monitoring_url, max_exhibitions=max_exhibitions
        )
        gallery.last_scraped_hash = current_hash
        gallery.save(update_fields=['last_scraped_hash'])
        return created, updated

    # =========================================================================
    # Стратегія: Facebook
    # =========================================================================

    def _process_facebook(self, gallery, gemini, force=False, max_exhibitions=3):
        self.stdout.write(f'   Facebook: {gallery.monitoring_url}')
        text = FacebookScraper.fetch_posts(gallery.monitoring_url)
        if not text:
            self.stdout.write(self.style.WARNING('   ⚠️  Не вдалося отримати пости'))
            return 0, 0

        current_hash = FacebookScraper.get_text_hash(text)
        if not force and current_hash == gallery.last_scraped_hash:
            self.stdout.write('   ✓ Пости не змінились.')
            return 0, 0

        self.stdout.write(f'   {len(text)} символів → Gemini...')
        created, updated = self._parse_and_save(
            gallery, gemini, text,
            source_url=gallery.monitoring_url, max_exhibitions=max_exhibitions
        )
        gallery.last_scraped_hash = current_hash
        gallery.save(update_fields=['last_scraped_hash'])
        return created, updated

    # =========================================================================
    # Збереження
    # =========================================================================

    def _parse_and_save(self, gallery, gemini, text, source_url="", max_exhibitions=3):
        exhibitions_data = gemini.extract_exhibitions(
            text, gallery.name_ua, max_exhibitions=max_exhibitions
        )
        if not exhibitions_data:
            self.stdout.write('       Gemini не знайшов виставок.')
            return 0, 0

        self.stdout.write(self.style.SUCCESS(f'       Знайдено: {len(exhibitions_data)} виставок'))
        created_count, updated_count = 0, 0

        for item in exhibitions_data:
            title = (item.get('title') or '').strip()
            if not title:
                continue

            exhibition, created = Exhibition.objects.update_or_create(
                gallery=gallery,
                title=title,
                defaults={
                    'description': item.get('description') or '',
                    'start_date': self._parse_date(item.get('start_date')),
                    'end_date': self._parse_date(item.get('end_date')),
                    'image_url': item.get('image_url') or '',
                    'artists': item.get('artists') or [],
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

    # =========================================================================
    # Хелпери
    # =========================================================================

    @staticmethod
    def _fetch_text(scraper_class, url, debug=False):
        if scraper_class == WebScraper:
            if debug:
                text, error = WebScraper.fetch_text_from_url(url, return_error=True)
                if error:
                    logger.warning(f"fetch error {url}: {error}")
                return text
            return WebScraper.fetch_text_from_url(url)
        return scraper_class.fetch_text_from_url(url)

    @staticmethod
    def _parse_date(date_str):
        if not date_str:
            return None
        try:
            return datetime.strptime(str(date_str).strip(), '%Y-%m-%d').date()
        except ValueError:
            return None
