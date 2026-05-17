import csv
from django.core.management.base import BaseCommand
from app.models import Gallery


class Command(BaseCommand):
    help = 'Відновлює monitoring_url/source_type/last_scraped_hash з CSV, створеного export_monitoring_urls'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        with open(csv_file_path, mode='r', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)
            updated = 0
            not_found = 0

            for row in reader:
                slug = (row.get('slug') or '').strip()
                if not slug:
                    continue

                gallery = Gallery.objects.filter(slug=slug).first()
                if not gallery:
                    not_found += 1
                    continue

                gallery.monitoring_url = (row.get('monitoring_url') or '').strip()
                gallery.source_type = (row.get('source_type') or '').strip()
                gallery.last_scraped_hash = (row.get('last_scraped_hash') or '').strip()
                gallery.save(update_fields=['monitoring_url', 'source_type', 'last_scraped_hash'])
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Готово! Відновлено: {updated}. Не знайдено: {not_found}.'))
