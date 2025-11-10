"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import (home, campsites_list, campsite_detail, campsite_create, campsite_edit, campsite_delete,
                        campsite_suggest, my_suggestions, pending_campsites, admin_manage_suggestions,
                        toggle_campsite_approval, campsites_map)
from accounts.views import login_view, register_view, logout_view


urlpatterns = [
    # Home page
    path('', home, name='home'),
    
    # Authentication
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    
    # Campsites
    path('campsites/', campsites_list, name='campsites_list'),
    path('campsites/map/', campsites_map, name='campsites_map'),
    path('campsites/create/', campsite_create, name='campsite_create'),
    path('campsites/suggest/', campsite_suggest, name='campsite_suggest'),
    path('campsites/my-suggestions/', my_suggestions, name='my_suggestions'),
    path('campsites/pending/', pending_campsites, name='pending_campsites'),
    path('campsites/admin-manage/', admin_manage_suggestions, name='admin_manage_suggestions'),
    path('campsites/<int:pk>/', campsite_detail, name='campsite_detail'),
    path('campsites/<int:pk>/edit/', campsite_edit, name='campsite_edit'),
    path('campsites/<int:pk>/delete/', campsite_delete, name='campsite_delete'),
    path('campsites/<int:pk>/toggle-approval/', toggle_campsite_approval, name='toggle_campsite_approval'),
    
    path('admin/', admin.site.urls),

    # OpenAPI schema and docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # JWT auth
    path('api/auth/jwt/create/', TokenObtainPairView.as_view(), name='jwt-obtain'),
    path('api/auth/jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),

    # OAuth2 (django-oauth-toolkit)
    path('o/', include(('oauth2_provider.urls', 'oauth2_provider'), namespace='oauth2_provider')),

    # API app
    path('api/', include('api.urls')),
]
