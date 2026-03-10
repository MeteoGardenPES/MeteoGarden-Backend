"""
URL configuration for api.
"""

# from django.contrib import admin
from django.urls import path

from .views import garden_plants, user_gardens
from .views import garden_plants
from .views import current_weather, get_stations, health

urlpatterns = [
    path("users/<str:username>/gardens/", user_gardens, name="user_gardens"),
    path(
        "users/<str:username>/gardens/<str:garden_name>/plants/",
        garden_plants,
        name="garden-plants",
    ),
    path(
        "users/<str:username>/gardens/<str:garden_name>/pots/<int:pot_number>/plant/",
        plant_status,
        name="plant_status",
    ),
    path("health/", health),
    path("weather/current/", current_weather),
    path("stations/", get_stations),
]
