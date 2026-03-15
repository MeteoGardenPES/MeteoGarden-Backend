"""
URL configuration for api.
"""

# from django.contrib import admin
from django.urls import path

from .views.views import health
from .views.views_info import importPlant

urlpatterns = [
    path("health/", health),
    path("plants/info/", importPlant),
]
