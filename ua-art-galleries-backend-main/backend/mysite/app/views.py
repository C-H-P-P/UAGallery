from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .contentful_client import fetch_all_galleries, fetch_gallery_by_slug
from .models import FavoriteGallery, Gallery

class GalleryListView(APIView):
    """
    GET /api/galleries/
    """
    def get(self, request):
        data = fetch_all_galleries()

        # Якщо користувач залогінений, додаємо інформацію про улюблені
        favorite_slugs = set()
        if request.user.is_authenticated:
            favorite_slugs = set(
                FavoriteGallery.objects.filter(user=request.user)
                .values_list('gallery__slug', flat=True)
            )

        # Проходимося по всім галереям і додаємо прапорець
        for gallery in data:
            gallery['is_favorite'] = gallery['slug'] in favorite_slugs

        return Response(data, status=status.HTTP_200_OK)

class GalleryDetailView(APIView):
    """
    GET /api/galleries/<slug>/
    """
    def get(self, request, slug):
        data = fetch_gallery_by_slug(slug)
        if data:
            # Check for favorite status
            if request.user.is_authenticated:
                is_fav = FavoriteGallery.objects.filter(
                    user=request.user, 
                    gallery__slug=slug
                ).exists()
                data['is_favorite'] = is_fav
            else:
                data['is_favorite'] = False
                
            return Response(data, status=status.HTTP_200_OK)
        return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)


class FavoriteGalleryListView(APIView):
    """
    GET /api/favorites/ - Отримати список улюблених галерей користувача
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = FavoriteGallery.objects.filter(user=request.user).select_related('gallery')
        gallery_slugs = [fav.gallery.slug for fav in favorites if fav.gallery.slug]
        return Response({"favorites": gallery_slugs}, status=status.HTTP_200_OK)


class FavoriteGalleryToggleView(APIView):
    """
    POST /api/favorites/toggle/ - Додати або видалити галерею з улюблених
    Body: { "slug": "gallery-slug" }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        slug = request.data.get("slug")
        
        if not slug:
            return Response(
                {"detail": "Slug is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Знайти галерею за slug
        try:
            gallery = Gallery.objects.get(slug=slug)
        except Gallery.DoesNotExist:
            # Якщо галерея не існує, створюємо запис
            gallery = Gallery.objects.create(
                slug=slug,
                name_ua=slug,
                name_en=slug,
                status=True
            )

        # Перевірити чи вже є в улюблених
        favorite = FavoriteGallery.objects.filter(user=request.user, gallery=gallery).first()
        
        if favorite:
            # Видалити з улюблених
            favorite.delete()
            return Response(
                {"detail": "Removed from favorites", "is_favorite": False},
                status=status.HTTP_200_OK
            )
        else:
            # Додати до улюблених
            FavoriteGallery.objects.create(user=request.user, gallery=gallery)
            return Response(
                {"detail": "Added to favorites", "is_favorite": True},
                status=status.HTTP_201_CREATED
            )