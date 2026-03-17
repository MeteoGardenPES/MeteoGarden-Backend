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
    login,
    register,
)

"""
from django.contrib import admin
"""

from api.views.views_visualitzarJardi import (
    plant_status,
    user_products,
    user_seeds,
    water_plant,
)

from .views import current_weather, garden_plants, get_stations, user_gardens

urlpatterns = [
    path("health/", health),
    path("register/", register),
    path("login/", login),
    path("get_profile/", get_profile),
    path("edit_profile/", edit_profile),
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
    path("weather/current/", current_weather),
    path("stations/", get_stations),
    path("plants/identify", identifyPlant, name="identifyPlant"),
    path("album/", getUserAlbum),
    path(
        "users/<str:username>/gardens/<str:garden_name>/pots/<int:pot_number>/water/",
        water_plant,
        name="water_plant",
    ),
    path(
        "users/<str:username>/seeds/",
        user_seeds,
        name="user_seeds",
    ),
    path(
        "users/<str:username>/products/",
        user_products,
        name="user_products",
    ),
]
