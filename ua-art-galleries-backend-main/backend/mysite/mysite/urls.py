from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Імпортуємо views з додатка 'app'
# Зверни увагу: Django бачить це як 'mysite.app.views' або просто 'app.views', 
# залежно від налаштувань. Якщо виникне помилка імпорту - скажи.
from app.views import GalleryListView, GalleryDetailView, FavoriteGalleryListView, FavoriteGalleryToggleView
from app.auth_views import MinimalLoginView, MinimalRegisterView, UserDetailView, ChangePasswordView

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- CONTENTFUL API (Нові шляхи) ---
    path('api/galleries/', GalleryListView.as_view(), name='gallery-list'),
    path('api/galleries/<slug:slug>/', GalleryDetailView.as_view(), name='gallery-detail'),

    # --- FAVORITES ---
    path('api/favorites/', FavoriteGalleryListView.as_view(), name='favorites-list'),
    path('api/favorites/toggle/', FavoriteGalleryToggleView.as_view(), name='favorites-toggle'),

    # --- AUTH ---
    path('api/auth/login/', MinimalLoginView.as_view(), name='login'),
    path('api/auth/register/', MinimalRegisterView.as_view(), name='register'),
    path('api/auth/user/', UserDetailView.as_view(), name='user_detail'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)