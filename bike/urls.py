# bike/urls.py

from django.contrib import admin
from django.urls import path, include  # Import include
from bikeapp import views 
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel
    path('', include('bikeapp.urls')),  # Include bikeapp urls
    path('admin_home/', views.admin_home, name='admin_home'),  # Admin home view
    path('user_home/', views.user_home, name='user_home'),    # User home view
    path('accounts/', include('django.contrib.auth.urls')),  # Add this line


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)