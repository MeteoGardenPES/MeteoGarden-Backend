"""
URL configuration for api.
"""

# from django.contrib import admin
from django.urls import path

from .views import current_weather, get_stations, health
from .views import edit_profile, get_profile, health, login, register

"""
from django.contrib import admin
"""


urlpatterns = [
    path("health/", health),
    path("register/", register),
    path("login/", login),
    path("get_profile/", get_profile),
    path("edit_profile/", edit_profile),
    path("weather/current/", current_weather),
    path("stations/", get_stations),
]
