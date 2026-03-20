from django.db import models


class Gallery(models.Model):
    # === ОСНОВНІ ПОЛЯ ===
    name_ua = models.CharField(max_length=200, verbose_name="Назва (UA)")
    name_en = models.CharField(max_length=200, verbose_name="Name (EN)")
    slug = models.SlugField(
        max_length=200, unique=True, verbose_name="URL-slug",
        help_text="Унікальний ідентифікатор для URL (наприклад: mystetskyi-arsenal)"
    )

    # === ЛОКАЦІЯ ===
    city = models.CharField(max_length=100, blank=True, default="", verbose_name="Місто")
    address = models.CharField(max_length=300, blank=True, default="", verbose_name="Адреса")

    # === ОПИСИ ===
    short_description = models.TextField(blank=True, default="", verbose_name="Короткий опис")
    description = models.TextField(blank=True, default="", verbose_name="Повний опис")

    # === ЗОБРАЖЕННЯ ===
    image = models.ImageField(
        upload_to='gallery/',
        verbose_name="Зображення",
        null=True,
        blank=True
    )

    # === ЛЮДИ ===
    founders = models.TextField(blank=True, default="", verbose_name="Засновники")
    curators = models.TextField(blank=True, default="", verbose_name="Куратори")
    artists = models.TextField(
        blank=True, default="",
        verbose_name="Митці",
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
        return self.name_ua or self.name_en

    class Meta:
        db_table = 'public_gallery'
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"
        ordering = ['-created_at']