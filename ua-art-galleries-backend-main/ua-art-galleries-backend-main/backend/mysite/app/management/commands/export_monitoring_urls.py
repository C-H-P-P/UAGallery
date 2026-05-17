import csv
from django.core.management.base import BaseCommand
from app.models import Gallery


class Command(BaseCommand):
    help = 'Експортує slug/monitoring_url/source_type/last_scraped_hash у CSV (для бекапу перед імпортом)'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, default=None)

    def handle(self, *args, **options):
        output_path = options.get('output')

        rows = Gallery.objects.all().values(
            'slug',
            'monitoring_url',
            'source_type',
            'last_scraped_hash',
        )

        fieldnames = ['slug', 'monitoring_url', 'source_type', 'last_scraped_hash']

        if output_path:
            f = open(output_path, 'w', encoding='utf-8', newline='')
            close_after = True
        else:
            f = self.stdout
            close_after = False

        try:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
        finally:
            if close_after:
                f.close()
