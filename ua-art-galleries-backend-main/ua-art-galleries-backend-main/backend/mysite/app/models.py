import logging
import requests
import urllib.parse
from django.db import models
from django.conf import settings
logger = logging.getLogger(__name__)
class Gallery(models.Model):
    name_ua = models.CharField(max_length=200, verbose_name="Назва (UA)")
    name_en = models.CharField(max_length=200, verbose_name="Name (EN)")
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name="URL-slug",
        help_text="Унікальний ідентифікатор для URL (наприклад: mystetskyi-arsenal)"
    )
    status = models.BooleanField(default=True, verbose_name="Статус (активна?)")
    city_ua = models.CharField(max_length=100, blank=True, default="", verbose_name="Місто (UA)")
    city_en = models.CharField(max_length=100, blank=True, default="", verbose_name="Місто (EN)")
    address_ua = models.CharField(max_length=300, blank=True, default="", verbose_name="Адреса (UA)")
    address_en = models.CharField(max_length=300, blank=True, default="", verbose_name="Адреса (EN)")
    short_description_ua = models.TextField(blank=True, default="", verbose_name="Короткий опис (UA)")
    short_description_en = models.TextField(blank=True, default="", verbose_name="Короткий опис (EN)")
    description_ua = models.TextField(blank=True, default="", verbose_name="Повний опис (UA)")
    description_en = models.TextField(blank=True, default="", verbose_name="Повний опис (EN)")
    specialization_ua = models.CharField(max_length=255, blank=True, default="", verbose_name="Спеціалізація (UA)")
    specialization_en = models.CharField(max_length=255, blank=True, default="", verbose_name="Спеціалізація (EN)")
    image = models.ImageField(
        upload_to='gallery/',
        verbose_name="Зображення",
        null=True,
        blank=True
    )
    founders_ua = models.TextField(blank=True, default="", verbose_name="Засновники (UA)")
    founders_en = models.TextField(blank=True, default="", verbose_name="Засновники (EN)")
    curators_ua = models.TextField(blank=True, default="", verbose_name="Куратори (UA)")
    curators_en = models.TextField(blank=True, default="", verbose_name="Куратори (EN)")
    artists_ua = models.TextField(
        blank=True, default="",
        verbose_name="Митці (UA)",
        help_text="Список митців (кожен з нового рядка)"
    )
    artists_en = models.TextField(
        blank=True, default="",
        verbose_name="Митці (EN)",
        help_text="Список митців (кожен з нового рядка)"
    )
    email = models.EmailField(blank=True, default="", verbose_name="Email")
    phone = models.CharField(max_length=50, blank=True, default="", verbose_name="Телефон")
    website_url = models.URLField(blank=True, default="", verbose_name="Вебсайт")
    founding_year = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Рік заснування"
    )
    social_links = models.JSONField(
        default=list, blank=True, verbose_name="Соціальні мережі",
        help_text='Список посилань, наприклад: [{"name": "Instagram", "url": "https://..."}]'
    )
    latitude = models.FloatField(null=True, blank=True, verbose_name="Широта")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Довгота")
    monitoring_url = models.URLField(
        blank=True, default="", verbose_name="URL для моніторингу",
        help_text="Посилання на головну сторінку сайту, Instagram або Facebook для парсингу подій"
    )
    contentful_id = models.CharField(max_length=255, blank=True, default="", null=True)
    source_type = models.CharField(
        max_length=50, blank=True, default="website", verbose_name="Тип джерела",
        help_text="website | instagram | facebook | telegram"
    )
    last_scraped_hash = models.CharField(
        max_length=255, blank=True, default="", verbose_name="Хеш останнього сканування",
        help_text="Хеш головної сторінки. Для підсторінок виставок — див. ExhibitionPage"
    )
    needs_js = models.BooleanField(
        default=False, verbose_name="Потребує JS-рендерингу",
        help_text="Увімкни для SPA-сайтів (React/Vue без SSR), де звичайний requests повертає порожню сторінку"
    )
    instagram_username = models.CharField(
        max_length=100, blank=True, default="", verbose_name="Instagram username",
        help_text="Наприклад: zag.gallery (без @). Якщо порожньо — витягується з monitoring_url"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            address_fields = {'address_ua', 'city_ua', 'address_en', 'city_en', 'latitude', 'longitude'}
            if not any(f in update_fields for f in address_fields):
                super().save(*args, **kwargs)
                return
        geocode_needed = False
        if self.pk:
            try:
                orig = Gallery.objects.get(pk=self.pk)
                if orig.address_ua != self.address_ua or orig.city_ua != self.city_ua:
                    geocode_needed = True
            except Gallery.DoesNotExist:
                geocode_needed = True
        else:
            if self.address_ua or self.city_ua:
                geocode_needed = True
        if self.latitude is None or self.longitude is None:
            if self.address_ua or self.city_ua:
                geocode_needed = True
        if geocode_needed:
            self._geocode_address()
        super().save(*args, **kwargs)
    def _geocode_address(self):
        addr = self.address_ua or self.address_en or ""
        city = self.city_ua or self.city_en or ""
        if not addr and not city:
            return
        import time
        def fetch_osm(q):
            url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(q)}&format=json&limit=1"
            try:
                headers = {'User-Agent': 'UAGalleriesApp/3.0'}
                req = requests.get(url, headers=headers, timeout=10)
                res = req.json()
                if isinstance(res, list) and len(res) > 0:
                    self.latitude = float(res[0]['lat'])
                    self.longitude = float(res[0]['lon'])
                    return True
            except Exception as e:
                logger.error(f"OSM error for {q}: {e}")
            return False
        queries_to_try = []
        full_q = f"{addr}, {city}, Ukraine".strip(", ")
        queries_to_try.append(full_q)
        parts = [p.strip() for p in addr.split(',') if p.strip()]
        if len(parts) > 1:
            queries_to_try.append(f"{parts[0]}, {parts[1]}, {city}, Ukraine".strip(", "))
            if len(parts) > 2:
                queries_to_try.append(f"{parts[-2]}, {parts[-1]}, {city}, Ukraine".strip(", "))
            queries_to_try.append(f"{parts[0]}, {city}, Ukraine".strip(", "))
        seen = set()
        unique_queries = [x for x in queries_to_try if not (x in seen or seen.add(x))]
        for q in unique_queries:
            if fetch_osm(q):
                logger.info(f"OSM successfully found: {q}")
                return
            time.sleep(1.2)
        logger.warning(f"OSM completely failed to find address '{addr}' after multiple attempts")
    def __str__(self):
        return f"{self.name_ua} ({self.slug})"
    class Meta:
        db_table = 'public_gallery'
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"
        ordering = ['-created_at']
class FavoriteGallery(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='favorite_galleries',
        verbose_name="Користувач"
    )
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name="Галерея"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Час додавання")
    class Meta:
        db_table = 'favorite_gallery'
        unique_together = ('user', 'gallery')
        verbose_name = "Улюблена галерея"
        verbose_name_plural = "Улюблені галереї"
    def __str__(self):
        return f"{self.user.username} -> {self.gallery.slug}"
class Review(models.Model):
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Користувач"
    )
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Галерея"
    )
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name="Оцінка"
    )
    text = models.TextField(
        verbose_name="Текст відгуку",
        help_text="Коментар користувача про галерею"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Час створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Час оновлення")
    class Meta:
        db_table = 'gallery_review'
        unique_together = ('user', 'gallery')
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        ordering = ['-created_at']
    def __str__(self):
        return f"Відгук {self.user.username} на {self.gallery.name_ua} ({self.rating}/5)"
class Exhibition(models.Model):
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.CASCADE,
        related_name='exhibitions',
        verbose_name="Галерея"
    )
    title = models.CharField(max_length=300, verbose_name="Назва виставки")
    description = models.TextField(blank=True, default="", verbose_name="Опис")
    start_date = models.DateField(null=True, blank=True, verbose_name="Дата початку")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата завершення")
    artists = models.JSONField(
        default=list, blank=True, verbose_name="Художники",
        help_text='Список художників у форматі масиву рядків'
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна?")
    image_url = models.URLField(
        blank=True, default="", verbose_name="URL головного фото",
        help_text="Пряме посилання на зображення постера або роботи з виставки"
    )
    source_url = models.URLField(
        blank=True, default="", verbose_name="URL сторінки виставки",
        help_text="Пряме посилання на підсторінку виставки (якщо є)"
    )
    source_text = models.TextField(
        blank=True, default="", verbose_name="Оригінальний текст (з парсера)",
        help_text="Сирий текст, з якого AI згенерував цю виставку (для дебагу)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'exhibition'
        verbose_name = "Виставка"
        verbose_name_plural = "Виставки"
        ordering = ['-start_date']
    def __str__(self):
        return f"{self.title} ({self.gallery.name_ua})"
class ExhibitionPage(models.Model):
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.CASCADE,
        related_name='exhibition_pages',
        verbose_name="Галерея"
    )
    url = models.URLField(
        unique=True, verbose_name="URL підсторінки виставки"
    )
    last_hash = models.CharField(
        max_length=32, blank=True, default="", verbose_name="MD5 хеш останнього сканування"
    )
    last_seen = models.DateTimeField(
        auto_now=True, verbose_name="Час останнього сканування"
    )
    class Meta:
        db_table = 'exhibition_page'
        verbose_name = "Сторінка виставки"
        verbose_name_plural = "Сторінки виставок"
    def __str__(self):
        return f"{self.gallery.slug} → {self.url}"
