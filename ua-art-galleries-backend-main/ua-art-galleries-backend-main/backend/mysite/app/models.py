from django.db import models


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

    # === ЧАСОВІ МІТКИ ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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