import csv
import logging
from django.core.management.base import BaseCommand
from app.models import Gallery

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Імпортує посилання на соцмережі/сайти з CSV файлу у базу даних'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Шлях до CSV файлу (наприклад, galleries.csv)')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                updated_count = 0
                not_found_count = 0
                
                for row in reader:
                    name = row.get('Артгалерея', '').strip()
                    links_str = row.get('Вебсайт / Соцмережі', '').strip()
                    
                    if not name or not links_str:
                        continue
                        
                    # Беремо перше посилання, якщо їх декілька (розділені ;)
                    links = [link.strip() for link in links_str.split(';')]
                    primary_link = links[0] if links else ""
                    
                    if not primary_link:
                        continue
                        
                    # Визначаємо тип
                    source_type = 'website'
                    if 'instagram.com' in primary_link:
                        source_type = 'instagram'
                    elif 'facebook.com' in primary_link:
                        source_type = 'facebook'
                        
                    # Шукаємо галерею в базі (за англійською або українською назвою)
                    # Використовуємо icontains для неточного пошуку, оскільки назви в таблиці можуть трохи відрізнятись
                    gallery = Gallery.objects.filter(name_en__icontains=name).first()
                    if not gallery:
                        gallery = Gallery.objects.filter(name_ua__icontains=name).first()
                        
                    if gallery:
                        gallery.monitoring_url = primary_link
                        gallery.source_type = source_type
                        gallery.save(update_fields=['monitoring_url', 'source_type'])
                        self.stdout.write(self.style.SUCCESS(f"Оновлено: {name} -> {primary_link}"))
                        updated_count += 1
                    else:
                        self.stdout.write(self.style.WARNING(f"Не знайдено в базі: {name}"))
                        not_found_count += 1
                        
                self.stdout.write(self.style.SUCCESS(f'\nГотово! Оновлено: {updated_count}. Не знайдено: {not_found_count}.'))
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл {csv_file_path} не знайдено.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Помилка: {str(e)}'))