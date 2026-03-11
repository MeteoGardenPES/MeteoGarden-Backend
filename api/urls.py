"""
URL configuration for api.
"""
from django import views
# from django.contrib import admin
from django.urls import path
from .views import importPlant

from .views import health

urlpatterns = [
    path("health/", health),
    path("plants/import/", importPlant, name="importPlant"),
]
