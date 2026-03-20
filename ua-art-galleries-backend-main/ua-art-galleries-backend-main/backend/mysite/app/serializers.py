from rest_framework import serializers
from .models import Gallery
from django.contrib.auth.models import User


class GalleryListSerializer(serializers.ModelSerializer):
    """Серіалізатор для списку галерей (коротка інфо)"""

    class Meta:
        model = Gallery
        fields = [
            'id',
            'name_ua',
            'name_en',
            'slug',
            'city',
            'address',
            'image',
            'short_description',
            'founding_year',
            'social_links',
            'created_at',
            'updated_at',
        ]


class GalleryDetailSerializer(serializers.ModelSerializer):
    """Серіалізатор для деталей галереї (повна інфо)"""

    class Meta:
        model = Gallery
        fields = [
            'id',
            'name_ua',
            'name_en',
            'slug',
            'city',
            'address',
            'image',
            'short_description',
            'description',
            'founders',
            'curators',
            'artists',
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