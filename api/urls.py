from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('health/', views.health, name='health'),
    path('campsites/', views.CampsiteListAPIView.as_view(), name='campsite-list'),
    path('campsites/<int:campsite_id>/like/', views.CampsiteLikeToggleView.as_view(), name='campsite-like-toggle'),
    path('campsites/<int:campsite_id>/like-status/', views.CampsiteLikeStatusView.as_view(), name='campsite-like-status'),
    
    # Product API endpoints
    path('products/', views.ProductListAPIView.as_view(), name='api-product-list'),
    path('products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='api-product-detail'),
    path('products/create/', views.ProductCreateAPIView.as_view(), name='api-product-create'),
    path('products/<int:pk>/update/', views.ProductUpdateAPIView.as_view(), name='api-product-update'),
    path('products/<int:pk>/delete/', views.ProductDestroyAPIView.as_view(), name='api-product-delete'),
]
