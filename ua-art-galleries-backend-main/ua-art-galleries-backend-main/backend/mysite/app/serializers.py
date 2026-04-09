from rest_framework import serializers
from .models import Gallery
from django.contrib.auth.models import User


class GalleryListSerializer(serializers.ModelSerializer):
    """Серіалізатор для списку галерей (коротка інфо)"""
    city_ua = serializers.CharField(source='city', read_only=True)
    city_en = serializers.CharField(source='city', read_only=True)
    address_ua = serializers.CharField(source='address', read_only=True)
    address_en = serializers.CharField(source='address', read_only=True)
    short_description_ua = serializers.CharField(source='short_description', read_only=True)
    short_description_en = serializers.CharField(source='short_description', read_only=True)

    class Meta:
        model = Gallery
        fields = [
            'id',
            'name_ua',
            'name_en',
            'slug',
            'status',
            'city_ua',
            'city_en',
            'address_ua',
            'address_en',
            'image',
            'short_description_ua',
            'short_description_en',
            'founding_year',
            'social_links',
            'created_at',
            'updated_at',
        ]


class GalleryDetailSerializer(serializers.ModelSerializer):
    """Серіалізатор для деталей галереї (повна інфо)"""
    full_description_ua = serializers.CharField(source='description_ua', read_only=True)
    full_description_en = serializers.CharField(source='description_en', read_only=True)
    specialization_ua = serializers.CharField(source='short_description_ua', read_only=True)
    specialization_en = serializers.CharField(source='short_description_en', read_only=True)
    website_url_ua = serializers.CharField(source='website_url', read_only=True)
    website_url_en = serializers.CharField(source='website_url', read_only=True)

    class Meta:
        model = Gallery
        fields = [
            'id',
            'name_ua',
            'name_en',
            'slug',
            'status',
            'city_ua',
            'city_en',
            'address_ua',
            'address_en',
            'image',
            'short_description_ua',
            'short_description_en',
            'description_ua',
            'description_en',
            'full_description_ua',
            'full_description_en',
            'founders_ua',
            'founders_en',
            'curators_ua',
            'curators_en',
            'artists_ua',
            'artists_en',
            'email',
            'phone',
            'website_url',
            'website_url_ua',
            'website_url_en',
            'specialization_ua',
            'specialization_en',
            'founding_year',
            'social_links',
            'created_at',
            'updated_at',
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
