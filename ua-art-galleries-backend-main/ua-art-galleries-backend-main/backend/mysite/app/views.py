from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from .models import Gallery
from .serializers import GalleryListSerializer, GalleryDetailSerializer


class GalleryListView(ListAPIView):
    """
    GET /api/galleries/
    Повертає список усіх галерей з бази даних (Neon PostgreSQL).
    """
    queryset = Gallery.objects.all()
    serializer_class = GalleryListSerializer
    permission_classes = [AllowAny]


class GalleryDetailView(RetrieveAPIView):
    """
    GET /api/galleries/<slug>/
    Повертає деталі однієї галереї за її slug.
    """
    queryset = Gallery.objects.all()
    serializer_class = GalleryDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'