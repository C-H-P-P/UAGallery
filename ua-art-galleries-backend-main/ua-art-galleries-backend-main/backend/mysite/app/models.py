import logging
import requests
import urllib.parse
from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)

class Gallery(models.Model):
    # === ОСНОВНІ ПОЛЯ ===
    name_ua = models.CharField(max_length=200, verbose_name="Назва (UA)")
    name_en = models.CharField(max_length=200, verbose_name="Name (EN)")
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name="URL-slug",
        help_text="Унікальний ідентифікатор для URL (наприклад: mystetskyi-arsenal)"
    )

    # === СТАТУС ===
    status = models.BooleanField(default=True, verbose_name="Статус (активна?)")

    # === ЛОКАЦІЯ ===
    city_ua = models.CharField(max_length=100, blank=True, default="", verbose_name="Місто (UA)")
    city_en = models.CharField(max_length=100, blank=True, default="", verbose_name="Місто (EN)")
    address_ua = models.CharField(max_length=300, blank=True, default="", verbose_name="Адреса (UA)")
    address_en = models.CharField(max_length=300, blank=True, default="", verbose_name="Адреса (EN)")

    # === ОПИСИ ===
    short_description_ua = models.TextField(blank=True, default="", verbose_name="Короткий опис (UA)")
    short_description_en = models.TextField(blank=True, default="", verbose_name="Короткий опис (EN)")
    description_ua = models.TextField(blank=True, default="", verbose_name="Повний опис (UA)")
    description_en = models.TextField(blank=True, default="", verbose_name="Повний опис (EN)")
    specialization_ua = models.CharField(max_length=255, blank=True, default="", verbose_name="Спеціалізація (UA)")
    specialization_en = models.CharField(max_length=255, blank=True, default="", verbose_name="Спеціалізація (EN)")

    # === ЗОБРАЖЕННЯ ===
    image = models.ImageField(
        upload_to='gallery/',
        verbose_name="Зображення",
        null=True,
        blank=True
    )

    # === ЛЮДИ ===
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

    # === КОНТАКТИ ===
    email = models.EmailField(blank=True, default="", verbose_name="Email")
    phone = models.CharField(max_length=50, blank=True, default="", verbose_name="Телефон")
    website_url = models.URLField(blank=True, default="", verbose_name="Вебсайт")

    # === ДОДАТКОВО ===
    founding_year = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Рік заснування"
    )
    social_links = models.JSONField(
        default=list, blank=True, verbose_name="Соціальні мережі",
        help_text='Список посилань, наприклад: [{"name": "Instagram", "url": "https://..."}]'
    )
    
    # === КООРДИНАТИ ===
    latitude = models.FloatField(null=True, blank=True, verbose_name="Широта")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Довгота")

    # === ЧАСОВІ МІТКИ ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Перевіряємо, чи потрібно геокодування
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
                
        # Також перевіряємо, якщо координати порожні, то варто спробувати отримати їх
        if self.latitude is None or self.longitude is None:
            if self.address_ua or self.city_ua:
                geocode_needed = True

        if geocode_needed:
            self._geocode_address()

        super().save(*args, **kwargs)

    def _geocode_address(self):
        # Намагаємося геокодувати за українською адресою, якщо є, інакше за англійською
        addr = self.address_ua or self.address_en or ""
        city = self.city_ua or self.city_en or ""
        
        if not addr and not city:
            return
            
        query = f"{addr}, {city}, Ukraine".strip(", ")
        # OpenStreetMap Nominatim API
        url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=1"
        
        try:
            # Nominatim вимагає валідний User-Agent
            headers = {'User-Agent': 'UAGalleriesApp/1.0'}
            req = requests.get(url, headers=headers, timeout=10)
            res = req.json()
            if isinstance(res, list) and len(res) > 0:
                location = res[0]
                self.latitude = float(location['lat'])
                self.longitude = float(location['lon'])
            else:
                logger.warning(f"OSM Geocoding zero results for query '{query}'")
        except Exception as e:
            logger.error(f"OSM Geocoding exception for query '{query}': {e}")

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