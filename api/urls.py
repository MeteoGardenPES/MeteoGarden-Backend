"""
URL configuration for api.
"""

# from django.contrib import admin
from django.urls import path

from .views import health, importPlant

urlpatterns = [
    path("health/", health),
    path("plants/info/", importPlant, name="importPlant"),
]
