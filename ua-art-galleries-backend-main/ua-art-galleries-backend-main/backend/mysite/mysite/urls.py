from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from app.views import GalleryListView, GalleryDetailView, contentful_webhook, FavoriteListView, FavoriteToggleView
from app.auth_views import MinimalLoginView, MinimalRegisterView, UserDetailView

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- GALLERY API (дані з Neon PostgreSQL) ---
    path('api/galleries/', GalleryListView.as_view(), name='gallery-list'),
    path('api/galleries/<slug:slug>/', GalleryDetailView.as_view(), name='gallery-detail'),

    # --- FAVORITES API ---
    path('api/favorites/', FavoriteListView.as_view(), name='favorites-list'),
    path('api/favorites/toggle/', FavoriteToggleView.as_view(), name='favorites-toggle'),

    # --- CONTENTFUL WEBHOOK (автоматична синхронізація) ---
    path('api/webhooks/contentful/', contentful_webhook, name='contentful-webhook'),

    # --- AUTH ---
    path('api/auth/login/', MinimalLoginView.as_view(), name='login'),
    path('api/auth/register/', MinimalRegisterView.as_view(), name='register'),
    path('api/auth/user/', UserDetailView.as_view(), name='user_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)