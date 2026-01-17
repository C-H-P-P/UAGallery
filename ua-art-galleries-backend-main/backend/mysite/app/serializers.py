from rest_framework import serializers
from .models import Gallery
from django.contrib.auth.models import User

class GallerySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=True, required=False) 

    class Meta:
        model = Gallery
        fields = [
            'id', 
            'name_ua', 
            'name_en',
            'image',
            'created_at', 
            'updated_at'
        ]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']