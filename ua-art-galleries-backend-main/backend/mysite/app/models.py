from django.db import models

class Gallery(models.Model):
    # Основна інформація
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug", null=True, blank=True)
    status = models.BooleanField(default=True, verbose_name="Активна")
    
    # Назви (обов'язкові)
    name_ua = models.CharField(max_length=200, verbose_name="Назва (UA)")
    name_en = models.CharField(max_length=200, verbose_name="Name (EN)")
    
    # Зображення
    image = models.ImageField(
        upload_to='gallery/', 
        verbose_name="Зображення", 
        null=True, 
        blank=True
    )
    cover_image = models.URLField(max_length=500, verbose_name="Cover Image URL", null=True, blank=True)
    
    # Описи
    short_description_ua = models.TextField(verbose_name="Короткий опис (UA)", null=True, blank=True)
    short_description_en = models.TextField(verbose_name="Short Description (EN)", null=True, blank=True)
    full_description_ua = models.TextField(verbose_name="Повний опис (UA)", null=True, blank=True)
    full_description_en = models.TextField(verbose_name="Full Description (EN)", null=True, blank=True)
    
    # Спеціалізація
    specialization_ua = models.CharField(max_length=200, verbose_name="Спеціалізація (UA)", null=True, blank=True)
    specialization_en = models.CharField(max_length=200, verbose_name="Specialization (EN)", null=True, blank=True)
    
    # Локація
    city_ua = models.CharField(max_length=100, verbose_name="Місто (UA)", null=True, blank=True)
    city_en = models.CharField(max_length=100, verbose_name="City (EN)", null=True, blank=True)
    address_ua = models.CharField(max_length=300, verbose_name="Адреса (UA)", null=True, blank=True)
    address_en = models.CharField(max_length=300, verbose_name="Address (EN)", null=True, blank=True)
    
    # Люди
    founders_ua = models.TextField(verbose_name="Засновники (UA)", null=True, blank=True)
    founders_en = models.TextField(verbose_name="Founders (EN)", null=True, blank=True)
    curators_ua = models.TextField(verbose_name="Куратори (UA)", null=True, blank=True)
    curators_en = models.TextField(verbose_name="Curators (EN)", null=True, blank=True)
    artists_ua = models.TextField(verbose_name="Художники (UA)", null=True, blank=True)
    artists_en = models.TextField(verbose_name="Artists (EN)", null=True, blank=True)
    
    # Контакти
    email = models.EmailField(max_length=200, verbose_name="Email", null=True, blank=True)
    phone = models.CharField(max_length=50, verbose_name="Телефон", null=True, blank=True)
    website = models.URLField(max_length=500, verbose_name="Веб-сайт", null=True, blank=True)
    social_links = models.JSONField(verbose_name="Соціальні мережі", null=True, blank=True)
    
    # Метадані
    founding_year = models.CharField(max_length=4, verbose_name="Рік заснування", null=True, blank=True)
    
    # Системні поля
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_ua or self.name_en

    class Meta:
        db_table = 'public_gallery'
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"