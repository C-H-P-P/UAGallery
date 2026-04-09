from rest_framework import serializers
from .models import Gallery
from django.contrib.auth.models import User

class DynamicLocaleMixin:
    """Міксин для динамічного вибору мови на основі ?lang= параметра в запиті"""
    
    def get_lang(self):
        request = self.context.get('request')
        if request and hasattr(request, 'query_params'):
            return request.query_params.get('lang', 'uk')
        return 'uk'

    def resolve_locale(self, obj, field_base):
        lang = self.get_lang()
        val_ua = getattr(obj, f"{field_base}_ua", '')
        val_en = getattr(obj, f"{field_base}_en", '')
        
        if lang == 'en':
            return val_en if val_en else val_ua
        return val_ua if val_ua else val_en

    def get_name(self, obj): return self.resolve_locale(obj, 'name')
    def get_city(self, obj): return self.resolve_locale(obj, 'city')
    def get_address(self, obj): return self.resolve_locale(obj, 'address')
    def get_short_description(self, obj): return self.resolve_locale(obj, 'short_description')
    
class GalleryListSerializer(DynamicLocaleMixin, serializers.ModelSerializer):
    """Серіалізатор для списку галерей (коротка інфо)"""
    name = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()

    class Meta:
        model = Gallery
        fields = [
            'id',
            'slug',
            'status',
            'name',
            'city',
            'address',
            'image',
            'short_description',
            'founding_year',
            'social_links',
            'created_at',
            'updated_at',
            # Залишаємо _ua/_en для повної сумісності
            'name_ua', 'name_en', 'city_ua', 'city_en', 
            'address_ua', 'address_en', 'short_description_ua', 'short_description_en'
        ]


class GalleryDetailSerializer(DynamicLocaleMixin, serializers.ModelSerializer):
    """Серіалізатор для деталей галереї (повна інфо)"""
    name = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    
    description = serializers.SerializerMethodField()
    full_description = serializers.SerializerMethodField()
    founders = serializers.SerializerMethodField()
    curators = serializers.SerializerMethodField()
    artists = serializers.SerializerMethodField()
    specialization = serializers.SerializerMethodField()

    def get_description(self, obj): return self.resolve_locale(obj, 'description')
    def get_full_description(self, obj): return self.resolve_locale(obj, 'description')
    def get_founders(self, obj): return self.resolve_locale(obj, 'founders')
    def get_curators(self, obj): return self.resolve_locale(obj, 'curators')
    def get_artists(self, obj): return self.resolve_locale(obj, 'artists')
    def get_specialization(self, obj): return self.resolve_locale(obj, 'specialization')

    class Meta:
        model = Gallery
        fields = [
            'id',
            'slug',
            'status',
            'name',
            'city',
            'address',
            'image',
            'short_description',
            'description',
            'full_description',
            'founders',
            'curators',
            'artists',
            'specialization',
            'email',
            'phone',
            'website_url',
            'founding_year',
            'social_links',
            'created_at',
            'updated_at',
            # Backwards compat manual fields
            'name_ua', 'name_en', 'city_ua', 'city_en',
            'address_ua', 'address_en', 'short_description_ua', 'short_description_en',
            'description_ua', 'description_en', 'founders_ua', 'founders_en',
            'curators_ua', 'curators_en', 'artists_ua', 'artists_en',
            'specialization_ua', 'specialization_en'
        ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
