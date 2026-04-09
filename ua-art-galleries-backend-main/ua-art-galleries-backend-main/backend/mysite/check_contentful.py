import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
django.setup()
from django.conf import settings
import contentful
client = contentful.Client(settings.CONTENTFUL_SPACE_ID, settings.CONTENTFUL_ACCESS_TOKEN)
entries = client.entries({'content_type': 'project', 'locale': '*'})
g39 = [e for e in entries if '39.9' in str(e.raw.get('fields', {}).get('name', {}))]
import json
print(json.dumps(g39[0].raw.get('fields') if g39 else 'not found', indent=2))
