from django.core.management.base import BaseCommand
from app.models import Gallery, Exhibition
from app.utils.scraper import WebScraper
from app.utils.gemini_parser import GeminiParser
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Запускає AI-детектор для моніторингу нових виставок'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=None)
        parser.add_argument('--slug', type=str, default=None)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Запуск AI-детектора виставок...'))
        
        # Перевірка наявності ключа
        gemini_key = os.environ.get('GEMINI_API_KEY')
        if not gemini_key:
            self.stdout.write(self.style.WARNING(
                'УВАГА: GEMINI_API_KEY не знайдено в змінних середовища. '
                'AI парсинг не працюватиме.'
            ))
            return
            
        parser = GeminiParser()
        galleries_to_monitor = Gallery.objects.exclude(monitoring_url="")
        slug = options.get('slug')
        if slug:
            galleries_to_monitor = galleries_to_monitor.filter(slug=slug)
        limit = options.get('limit')
        total_count = galleries_to_monitor.count()
        if limit:
            galleries_to_monitor = galleries_to_monitor[:limit]
            count = min(total_count, limit)
        else:
            count = total_count
        
        self.stdout.write(f'Знайдено {count} галерей для моніторингу.')
        
        for gallery in galleries_to_monitor:
            url = gallery.monitoring_url
            self.stdout.write(f'Обробка: {gallery.name_ua} ({url})')
            
            # 1. Скрапінг тексту
            text = WebScraper.fetch_text_from_url(url)
            if not text:
                self.stdout.write(self.style.WARNING(f"  Не вдалося отримати текст з {url}"))
                continue
                
            # 2. Перевірка хешу (чи є зміни з минулого разу)
            current_hash = WebScraper.get_text_hash(text)
            if current_hash == gallery.last_scraped_hash:
                self.stdout.write(f"  Змін на сторінці не знайдено (хеш співпадає). Пропускаємо.")
                continue
                
            # 3. Відправка в AI
            self.stdout.write("  Виявлено зміни! Відправка тексту до Gemini AI...")
            exhibitions_data = parser.extract_exhibitions(text, gallery.name_ua)
            
            if not exhibitions_data:
                self.stdout.write("  Gemini не знайшов нових виставок у тексті.")
                # Все одно оновлюємо хеш, щоб не відправляти цей самий текст завтра
                gallery.last_scraped_hash = current_hash
                gallery.save(update_fields=['last_scraped_hash'])
                continue
                
            # 4. Збереження виставок у базу даних
            self.stdout.write(self.style.SUCCESS(f"  Знайдено виставок: {len(exhibitions_data)}"))
            
            for item in exhibitions_data:
                title = item.get('title', 'Без назви')
                start_date_str = item.get('start_date')
                end_date_str = item.get('end_date')
                
                # Конвертація дат (захист від невалідних форматів AI)
                start_date = None
                end_date = None
                try:
                    if start_date_str: start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    if end_date_str: end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass # Якщо AI повернув криву дату, залишаємо None
                
                # Створюємо або оновлюємо виставку
                exhibition, created = Exhibition.objects.update_or_create(
                    gallery=gallery,
                    title=title,
                    defaults={
                        'description': item.get('description', ''),
                        'start_date': start_date,
                        'end_date': end_date,
                        'artists': item.get('artists', []),
                        'source_text': text[:5000], # Зберігаємо шматок тексту для дебагу
                        'is_active': True
                    }
                )
                action = "Створено" if created else "Оновлено"
                self.stdout.write(f"    - {action}: {title}")
                
            # Оновлюємо хеш після успішної обробки
            gallery.last_scraped_hash = current_hash
            gallery.save(update_fields=['last_scraped_hash'])
            
        self.stdout.write(self.style.SUCCESS('Сканування завершено!'))
