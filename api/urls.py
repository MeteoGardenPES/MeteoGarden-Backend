"""
URL configuration for api.
"""

# from django.contrib import admin
from django.urls import path

from .views import (
    current_weather,
    edit_profile,
    get_profile,
    get_stations,
    getUserAlbum,
    health,
    identifyPlant,
    importPlant,
    login,
    register,
)

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
    path("plants/info/", importPlant),
    path("plants/identify", identifyPlant, name="identifyPlant"),
    path("album/", getUserAlbum),
]
