import csv
import logging
import re
from django.core.management.base import BaseCommand
from app.models import Gallery

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Імпортує посилання на соцмережі/сайти з CSV файлу у базу даних'

    def _normalize_url(self, value):
        if not value:
            return ""
        s = str(value).strip()
        if not s:
            return ""
        m = re.search(r'https?://[^\s\)>\]}",]+', s)
        if m:
            s = m.group(0)
        s = s.strip().strip("`").strip()
        s = s.strip().strip(")").strip("]").strip("}").strip(",").strip(".").strip("`").strip()
        if s and not s.startswith(("http://", "https://")):
            s = f"https://{s}"
        return s
    
    def _extract_urls(self, value):
        if not value:
            return []
        raw = str(value)
        urls = re.findall(r'https?://[^\s\)>\]}",;]+', raw)
        out = []
        for u in urls:
            nu = self._normalize_url(u)
            if nu:
                out.append(nu)
        seen = set()
        dedup = []
        for u in out:
            if u not in seen:
                dedup.append(u)
                seen.add(u)
        return dedup

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Шлях до CSV файлу (наприклад, galleries.csv)')
        parser.add_argument('--quiet', action='store_true')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        quiet = bool(options.get('quiet'))
        
        try:
            file = None
            last_err = None
            for enc in ("utf-8-sig", "utf-8", "cp1251", "latin-1"):
                try:
                    file = open(csv_file_path, mode='r', encoding=enc, newline='')
                    break
                except UnicodeDecodeError as e:
                    last_err = e
                    file = None

            if not file:
                raise last_err or Exception("Cannot decode CSV")

            with file:
                reader = csv.DictReader(file)
                fieldnames = set(reader.fieldnames or [])
                
                updated_count = 0
                not_found_count = 0
                
                for row in reader:
                    slug = ""
                    name = ""
                    primary_link = ""

                    if {'sys_id', 'slug', 'websiteUrl', 'socialLinks'}.issubset(fieldnames):
                        slug = (row.get('slug') or '').strip()
                        name = (row.get('name') or '').strip()
                        website_url = self._normalize_url(row.get('websiteUrl'))
                        social_urls = self._extract_urls(row.get('socialLinks'))
                        primary_link = website_url if website_url and website_url != "-" else (social_urls[0] if social_urls else "")
                    else:
                        name = (row.get('Артгалерея') or '').strip()
                        links_str = (row.get('Вебсайт / Соцмережі') or '').strip()
                        if not name or not links_str:
                            continue
                        links = [link.strip() for link in links_str.split(';')]
                        primary_link = self._normalize_url(links[0] if links else "")
                    
                    if not primary_link:
                        continue
                        
                                    
                    source_type = 'website'
                    if 'instagram.com' in primary_link:
                        source_type = 'instagram'
                    elif 'facebook.com' in primary_link:
                        source_type = 'facebook'
                        
                                                                                    
                                                                                                                       
                    gallery = None
                    if slug:
                        gallery = Gallery.objects.filter(slug=slug).first()
                    if not gallery and name:
                        gallery = Gallery.objects.filter(name_en__icontains=name).first()
                        if not gallery:
                            gallery = Gallery.objects.filter(name_ua__icontains=name).first()
                        
                    if gallery:
                        gallery.monitoring_url = primary_link
                        gallery.source_type = source_type
                        gallery.save(update_fields=['monitoring_url', 'source_type'])
                        if not quiet:
                            self.stdout.write(self.style.SUCCESS(f"Оновлено: {gallery.slug} -> {primary_link}"))
                        updated_count += 1
                    else:
                        if not quiet:
                            self.stdout.write(self.style.WARNING(f"Не знайдено в базі: {slug or name}"))
                        not_found_count += 1
                        
                self.stdout.write(self.style.SUCCESS(f'\nГотово! Оновлено: {updated_count}. Не знайдено: {not_found_count}.'))
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл {csv_file_path} не знайдено.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Помилка: {str(e)}'))
