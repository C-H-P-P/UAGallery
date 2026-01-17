from django.contrib import admin
from .models import Gallery
from django.contrib.auth.models import User



@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):

    list_display = ('name_ua', 'name_en', 'created_at')
    search_fields = ('name_ua', 'name_en')
    readonly_fields = ('created_at', 'updated_at')

