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
        return Response(data, status=status.HTTP_200_OK)

class GalleryDetailView(APIView):
    """
    GET /api/galleries/<slug>/
    """
    def get(self, request, slug):
        data = fetch_gallery_by_slug(slug)
        if data:
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

        # Знайти або створити галерею
        gallery, created = Gallery.objects.get_or_create(
            slug=slug,
            defaults={
                'name_ua': slug,  # Тимчасово, поки не отримаємо дані з Contentful
                'name_en': slug,
                'status': True
            }
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