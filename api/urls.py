"""
URL configuration for api.
"""

from django.urls import path

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
]
