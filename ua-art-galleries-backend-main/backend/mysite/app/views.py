from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .contentful_client import fetch_all_galleries, fetch_gallery_by_slug

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