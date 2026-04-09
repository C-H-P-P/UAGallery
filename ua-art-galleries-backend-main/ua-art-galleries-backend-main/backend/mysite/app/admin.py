from django.contrib import admin
from .models import Gallery


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('name_ua', 'name_en', 'status', 'city_ua', 'slug', 'founding_year', 'created_at')
    list_filter = ('status', 'city_ua', 'founding_year')
    search_fields = ('name_ua', 'name_en', 'city_ua', 'city_en', 'founders_ua', 'curators_ua')
    prepopulated_fields = {'slug': ('name_en',)}
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Основне', {
            'fields': ('status', 'name_ua', 'name_en', 'slug', 'image')
        }),
        ('Локація', {
            'fields': ('city_ua', 'city_en', 'address_ua', 'address_en')
        }),
        ('Описи', {
            'fields': ('short_description_ua', 'short_description_en', 'description_ua', 'description_en')
        }),
        ('Люди', {
            'fields': ('founders_ua', 'founders_en', 'curators_ua', 'curators_en', 'artists_ua', 'artists_en')
        }),
        ('Контакти', {
            'fields': ('email', 'phone', 'website_url')
        }),
        ('Додатково', {
            'fields': ('founding_year', 'social_links')
        }),
        ('Системне', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
