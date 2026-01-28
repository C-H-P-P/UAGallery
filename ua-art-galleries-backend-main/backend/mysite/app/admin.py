from django.contrib import admin
from .models import Gallery, FavoriteGallery

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('name_ua', 'name_en', 'city_ua', 'status', 'created_at')
    list_filter = ('status', 'city_ua')
    search_fields = ('name_ua', 'name_en', 'slug')
    prepopulated_fields = {'slug': ('name_ua',)}


@admin.register(FavoriteGallery)
class FavoriteGalleryAdmin(admin.ModelAdmin):
    list_display = ('user', 'gallery', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'gallery__name_ua', 'gallery__name_en')
    raw_id_fields = ('user', 'gallery')
