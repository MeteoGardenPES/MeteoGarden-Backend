"""
URL configuration for api.
"""

# from django.contrib import admin
from django.urls import path

from .views import health, current_weather, get_stations

urlpatterns = [
    path("health/", health),
    path("weather/current/", current_weather),
    path("stations/", get_stations),
]
