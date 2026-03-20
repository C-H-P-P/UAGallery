from django.contrib import admin
from .models import Gallery


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('name_ua', 'name_en', 'city', 'slug', 'founding_year', 'created_at')
    list_filter = ('city', 'founding_year')
    search_fields = ('name_ua', 'name_en', 'city', 'founders', 'curators')
    prepopulated_fields = {'slug': ('name_en',)}
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Основне', {
            'fields': ('name_ua', 'name_en', 'slug', 'image')
        }),
        ('Локація', {
            'fields': ('city', 'address')
        }),
        ('Описи', {
            'fields': ('short_description', 'description')
        }),
        ('Люди', {
            'fields': ('founders', 'curators', 'artists')
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
