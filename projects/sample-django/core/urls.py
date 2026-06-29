from django.urls import path
from core import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('api/info/', views.get_info, name='get_info'),
]
