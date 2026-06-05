from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, HttpResponse

from app.views import GalleryListView, GalleryDetailView, contentful_webhook, FavoriteListView, FavoriteToggleView, ReviewListCreateView, run_csv_import_view, run_ai_detector_view
from app.auth_views import MinimalLoginView, MinimalRegisterView, UserDetailView

def health_check(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('admin/', admin.site.urls),

                                                  
    path('api/galleries/', GalleryListView.as_view(), name='gallery-list'),
    path('api/galleries/<slug:slug>/', GalleryDetailView.as_view(), name='gallery-detail'),
    path('api/galleries/<slug:slug>/reviews/', ReviewListCreateView.as_view(), name='gallery-reviews'),

                           
    path('api/favorites/', FavoriteListView.as_view(), name='favorites-list'),
    path('api/favorites/toggle/', FavoriteToggleView.as_view(), name='favorites-toggle'),

                                                            
    path('api/webhooks/contentful/', contentful_webhook, name='contentful-webhook'),

                                       
    path('api/health/', health_check, name='health-check'),

                                 
    path('api/system/import-csv/', run_csv_import_view, name='system-import-csv'),
    path('api/system/run-detector/', run_ai_detector_view, name='system-run-detector'),

                  
    path('api/auth/login/', MinimalLoginView.as_view(), name='login'),
    path('api/auth/register/', MinimalRegisterView.as_view(), name='register'),
    path('api/auth/user/', UserDetailView.as_view(), name='user_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)