import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from app.models import Gallery

qs = Gallery.objects.filter(monitoring_url__in=['', '-', 'https://-'])
count = 0
for g in qs:
    new_url = ''
    if g.social_links:
        if isinstance(g.social_links, str):
            links = [l.strip(' []"\'') for l in g.social_links.split(',')]
            if links and links[0]:
                new_url = links[0]
        elif isinstance(g.social_links, list) and len(g.social_links) > 0:
            new_url = str(g.social_links[0]).strip(' []"\'')
            
    if new_url and new_url != '-' and new_url != 'https://-':
        if not new_url.startswith('http'):
            new_url = 'https://' + new_url
        g.monitoring_url = new_url
        if 'instagram.com' in new_url:
            g.source_type = 'instagram'
        elif 'facebook.com' in new_url:
            g.source_type = 'facebook'
        g.save(update_fields=['monitoring_url', 'source_type'])
        count += 1
print(f'Completely fixed {count} broken galleries!')
