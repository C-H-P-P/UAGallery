import os

path = r'd:\ua-art-galleries-backend-mainORIGIN\ua-art-galleries-backend-main\ua-art-galleries-backend-main\backend\mysite\app\management\commands\run_detector.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Update _process_website
pattern_website = r'    def _process_website\(self, gallery, gemini: GeminiParser, debug=False, force=False\):.*?        return created_total, updated_total'
replacement_website = '''    def _process_website(self, gallery, gemini: GeminiParser, debug=False, force=False):
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
        extracted = gemini.extract_exhibition_links(listings_text, url)
        
        if isinstance(extracted, list):
            exhibition_links = extracted
            index_pages = []
        else:
            exhibition_links = extracted.get("exhibition_pages", [])
            index_pages = extracted.get("index_pages", [])
            
        if index_pages and url == gallery.website_url:
            index_url = index_pages[0]
            self.stdout.write(f'   🔀 Знайдено загальну сторінку виставок: {index_url}')
            gallery.monitoring_url = index_url
            gallery.save(update_fields=['monitoring_url'])
            listings_text = self._fetch_text(scraper, index_url, debug)
            if listings_text:
                url = index_url
                self.stdout.write(f'   🔍 Шукаємо виставки на новій сторінці...')
                extracted = gemini.extract_exhibition_links(listings_text, url)
                exhibition_links = extracted.get("exhibition_pages", []) if isinstance(extracted, dict) else extracted

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
        return created_total, updated_total'''

content = re.sub(pattern_website, replacement_website, content, flags=re.DOTALL)

# Update _parse_and_save
pattern_parse = r'    def _parse_and_save\(self, gallery, gemini: GeminiParser,.*?        return created_count, updated_count'
replacement_parse = '''    def _parse_and_save(self, gallery, gemini: GeminiParser,
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
                    'image_url': item.get('image_url', ''),
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
        return created_count, updated_count'''

content = re.sub(pattern_parse, replacement_parse, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
