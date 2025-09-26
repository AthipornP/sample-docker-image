from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('profile/', views.user_profile, name='user_profile'),
    path('weather/bangkok/', views.weather_bangkok, name='weather_bangkok'),
]