from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('health/', views.health, name='health'),
    path('campsites/<int:campsite_id>/like/', views.CampsiteLikeToggleView.as_view(), name='campsite-like-toggle'),
    path('campsites/<int:campsite_id>/like-status/', views.CampsiteLikeStatusView.as_view(), name='campsite-like-status'),
]
