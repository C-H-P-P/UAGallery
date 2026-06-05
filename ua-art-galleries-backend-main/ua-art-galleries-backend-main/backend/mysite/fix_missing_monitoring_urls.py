import os
import django
import sys

                           
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from app.models import Gallery

def fix_urls():
    galleries = Gallery.objects.all()
    updated_count = 0
    
    for gallery in galleries:
                                                                                          
        is_empty = not gallery.monitoring_url or gallery.monitoring_url.strip() in ['-', 'https://-', '']
        
        if is_empty and gallery.social_links:
                                                           
            social_links = gallery.social_links
                                                                                        
            if isinstance(social_links, str):
                import json
                try:
                    social_links = json.loads(social_links)
                except:
                    social_links = [social_links]
                    
            if not isinstance(social_links, list):
                continue
                
                                             
            found_url = None
            found_type = ''
            
            for link in social_links:
                if not isinstance(link, str):
                    continue
                link_lower = link.lower()
                if 'instagram.com' in link_lower:
                    found_url = link
                    found_type = 'instagram'
                    break                    
                elif 'facebook.com' in link_lower and not found_url:
                    found_url = link
                    found_type = 'facebook'
                elif not found_url and link.startswith('http'):
                                                            
                    found_url = link
                    if 't.me' in link_lower:
                        found_type = 'telegram'
                    else:
                        found_type = 'website'
                    
            if found_url:
                gallery.monitoring_url = found_url
                gallery.source_type = found_type
                gallery.save(update_fields=['monitoring_url', 'source_type'])
                print(f"Updated {gallery.slug}: {found_url} ({found_type})")
                updated_count += 1
            elif gallery.website_url and gallery.website_url.strip() and gallery.website_url.strip() != '-':
                                         
                gallery.monitoring_url = gallery.website_url.strip()
                gallery.source_type = 'website'
                gallery.save(update_fields=['monitoring_url', 'source_type'])
                print(f"Updated {gallery.slug} from website_url: {gallery.monitoring_url} (website)")
                updated_count += 1
        elif is_empty and gallery.website_url and gallery.website_url.strip() and gallery.website_url.strip() != '-':
                                                        
            gallery.monitoring_url = gallery.website_url.strip()
            gallery.source_type = 'website'
            gallery.save(update_fields=['monitoring_url', 'source_type'])
            print(f"Updated {gallery.slug} from website_url: {gallery.monitoring_url} (website)")
            updated_count += 1

    print(f"\nDone! Successfully filled monitoring_url for {updated_count} galleries.")

if __name__ == '__main__':
    fix_urls()
