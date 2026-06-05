from django.core.management.base import BaseCommand
from app.models import Gallery
import time

class Command(BaseCommand):
    help = 'Geocode all galleries that are missing latitude and longitude'

    def handle(self, *args, **options):
        galleries = Gallery.objects.filter(latitude__isnull=True) | Gallery.objects.filter(longitude__isnull=True)
        count = galleries.count()
        self.stdout.write(self.style.WARNING(f'Found {count} galleries missing coordinates.'))
        
        for idx, gallery in enumerate(galleries, 1):
            self.stdout.write(f'Processing {idx}/{count}: {gallery.name_ua} - {gallery.address_ua}')
                                                                                
                                                   
            gallery.save()  
                                                                                       
            time.sleep(1.5) 
            
        self.stdout.write(self.style.SUCCESS(f'Successfully processed {count} galleries.'))
