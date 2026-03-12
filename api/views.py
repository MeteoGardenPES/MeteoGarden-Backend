# from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import os
import requests
from django.db import transaction
from .models import Plant

# Create your views here.
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"health status": "ok"})

TEMPS_RANGES = [
    (-51.1, -45.6),
    (-45.6, -40),
    (-40, -34.4),
    (-34.4, -28.9),
    (-28.9, -23.3),
    (-23.3, -17.8),
    (-17.8, -12.2),
    (-12.2, -6.7),
    (-6.7, -1.1),
    (-1.1, 4.4),
    (4.4, 10),
    (10, 15.6),
    (15.6, 21.1),
]


def translate(text: str | None, lang: str) -> str | None:
    if not text:
        return None

    api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")
    if not api_key:
        # if there's no key, returns the original text
        return text

    url = "https://translation.googleapis.com/language/translate/v2"
    params = {"q": text, "target": lang, "format": "text", "key": api_key}

    response = requests.post(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["data"]["translations"][0]["translatedText"]


def getTemperature(zone_min, zone_max) -> tuple[float | None, float | None]:
    if zone_min is None or zone_max is None:
        return None, None
    zone_min = int(str(zone_min))
    zone_max = int(str(zone_max))
    return float(TEMPS_RANGES[zone_min - 1][0]), float(TEMPS_RANGES[zone_max - 1][1])


def getPlantInfoFromAPI(scientific_name: str) -> dict | None:
    key = os.getenv("PERENUAL_API_KEY")
    if not key:
        raise RuntimeError("There's no API key for Perenual.")

    url = "https://perenual.com/api/species-list?"
    params = {"key": os.getenv("PERENUAL_API_KEY"), "q": scientific_name}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if not data.get("data"):
        return None

    id = data["data"][0]["id"]
    url_details = "https://perenual.com/api/v2/species/details/" + str(id)
    params_details = {"key": os.getenv("PERENUAL_API_KEY")}
    response_details = requests.get(url_details, params=params_details)
    response_details.raise_for_status()
    return response_details.json()


def filterInfo(details: dict, lang: str) -> dict:
    sci_list = details.get("scientific_name") or []
    sci = sci_list[0] if sci_list else None

    hard = details.get("hardiness") or {}
    minTemperature, maxTemperature = getTemperature(hard.get("min"), hard.get("max"))

    description = details.get("description")

    info = {
        "scientificName": sci,
        "commonName": details.get("common_name"),
        "family": details.get("family"),
        "canFlower": details.get("flowers"),
        "minTemperature": minTemperature,
        "maxTemperature": maxTemperature,
        "description": description,
    }

    saveOrUpdatePlant(info)
    return info


@transaction.atomic
def saveOrUpdatePlant(details: dict):
    Plant.objects.update_or_create(
        scientificName=details.get("scientificName"),
        defaults={
            "commonName": details.get("commonName"),
            "family": details.get("family"),
            "canFlower": details.get("canFlower"),
            "minTemperature": details.get("minTemperature"),
            "maxTemperature": details.get("maxTemperature"),
            "description": details.get("description"),
        },
    )


def getInfoPlant(scientific_name: str, lang: str) -> dict | None:
    if Plant.objects.filter(scientificName=scientific_name).exists():
        plant = Plant.objects.get(scientificName=scientific_name)
        return {
            "scientificName": plant.scientificName,
            "commonName": plant.commonName,
            "family": plant.family,
            "canFlower": plant.canFlower,
            "minTemperature": plant.minTemperature,
            "maxTemperature": plant.maxTemperature,
            "description": translate(plant.description, lang),
        }
    else:
        details = getPlantInfoFromAPI(scientific_name)
        return filterInfo(details, lang)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def importPlant(request):
    if request.method == "GET":
        scientific_name = request.query_params.get("scientificName")
        lang = request.query_params.get("lang", "ca")
    else:
        scientific_name = request.data.get("scientificName")
        lang = request.data.get("lang", "ca")

    if not scientific_name:
        return Response({"error": "scientificName is required"}, status=400)

    try:
        plant = getInfoPlant(scientific_name, lang)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    if plant is None:
        return Response({"error": "Plant not found"}, status=404)

    return Response(plant, status=200)
