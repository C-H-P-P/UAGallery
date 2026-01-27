from rest_framework import serializers
from .models import Gallery
from django.contrib.auth.models import User

class GallerySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=True, required=False) 

    class Meta:
        model = Gallery
        fields = [
            'id',
            'slug',
            'status',
            'name_ua', 
            'name_en',
            'image',
            'cover_image',
            'short_description_ua',
            'short_description_en',
            'full_description_ua',
            'full_description_en',
            'specialization_ua',
            'specialization_en',
            'city_ua',
            'city_en',
            'address_ua',
            'address_en',
            'founders_ua',
            'founders_en',
            'curators_ua',
            'curators_en',
            'artists_ua',
            'artists_en',
            'email',
            'phone',
            'website',
            'social_links',
            'founding_year',
            'created_at', 
            'updated_at'
        ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']