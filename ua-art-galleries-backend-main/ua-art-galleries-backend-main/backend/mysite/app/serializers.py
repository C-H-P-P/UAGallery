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
            'city',
            'city_ua',
            'city_en',
            'address',
            'address_ua',
            'address_en',
            'image',
            'short_description',
            'short_description_ua',
            'short_description_en',
            'founding_year',
            'social_links',
            'created_at',
            'updated_at',
        ]


class GalleryDetailSerializer(serializers.ModelSerializer):
    """Серіалізатор для деталей галереї (повна інфо)"""
    city_ua = serializers.CharField(source='city', read_only=True)
    city_en = serializers.CharField(source='city', read_only=True)
    address_ua = serializers.CharField(source='address', read_only=True)
    address_en = serializers.CharField(source='address', read_only=True)
    short_description_ua = serializers.CharField(source='short_description', read_only=True)
    short_description_en = serializers.CharField(source='short_description', read_only=True)
    full_description_ua = serializers.CharField(source='description', read_only=True)
    full_description_en = serializers.CharField(source='description', read_only=True)
    founders_ua = serializers.CharField(source='founders', read_only=True)
    founders_en = serializers.CharField(source='founders', read_only=True)
    curators_ua = serializers.CharField(source='curators', read_only=True)
    curators_en = serializers.CharField(source='curators', read_only=True)
    artists_ua = serializers.CharField(source='artists', read_only=True)
    artists_en = serializers.CharField(source='artists', read_only=True)

    class Meta:
        model = Gallery
        fields = [
            'id',
            'name_ua',
            'name_en',
            'slug',
            'city',
            'city_ua',
            'city_en',
            'address',
            'address_ua',
            'address_en',
            'image',
            'short_description',
            'short_description_ua',
            'short_description_en',
            'description',
            'full_description_ua',
            'full_description_en',
            'founders',
            'founders_ua',
            'founders_en',
            'curators',
            'curators_ua',
            'curators_en',
            'artists',
            'artists_ua',
            'artists_en',
            'email',
            'phone',
            'website_url',
            'founding_year',
            'social_links',
            'created_at',
            'updated_at',
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
