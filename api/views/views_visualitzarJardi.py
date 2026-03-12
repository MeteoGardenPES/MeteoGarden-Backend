from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from api.models import Garden, Pot, User


def garden_plants(request, username, garden_name):
    garden = get_object_or_404(
        Garden.objects.select_related("user"),
        user__username=username,
        name=garden_name,
    )

    pots = (
        Pot.objects.filter(garden=garden)
        .order_by("number")
        .select_related("plantingarden", "plantingarden__plant")
    )

    data = []

    for pot in pots:
        planting = getattr(pot, "plantingarden", None)

        if planting is None:
            data.append(
                {
                    "pot_number": pot.number,
                    "occupied": pot.occupied,
                    "plant": None,
                    "growth_phase": None,
                    "health_level": None,
                    "water_level": None,
                    "planted_at": None,
                    "last_watered_at": None,
                }
            )
        else:
            data.append(
                {
                    "pot_number": pot.number,
                    "occupied": pot.occupied,
                    "plant": {
                        "scientific_name": planting.plant.scientificName,
                        "common_name": planting.plant.commonName,
                        "family": planting.plant.family,
                        "can_flower": planting.plant.canFlower,
                        "min_temperature": planting.plant.minTemperature,
                        "max_temperature": planting.plant.maxTemperature,
                    },
                    "growth_phase": planting.growthPhase,
                    "health_level": planting.healthLevel,
                    "water_level": planting.waterLevel,
                    "planted_at": planting.plantedAt.isoformat(),
                    "last_watered_at": planting.lastWateredAt.isoformat(),
                }
            )

    return JsonResponse(data, safe=False)


def user_gardens(request, username):
    user = get_object_or_404(User, username=username)

    gardens = Garden.objects.filter(user=user).order_by("name")

    data = [
        {
            "name": garden.name,
        }
        for garden in gardens
    ]

    return JsonResponse(data, safe=False)


def plant_status(request, username, garden_name, pot_number):
    garden = get_object_or_404(Garden, user__username=username, name=garden_name)

    pot = get_object_or_404(Pot, garden=garden, number=pot_number)

    planting = getattr(pot, "plantingarden", None)

    if planting is None:
        data = {"pot_number": pot.number, "plant": None}
    else:
        data = {
            "pot_number": pot.number,
            "plant": {
                "scientific_name": planting.plant.scientificName,
                "common_name": planting.plant.commonName,
                "family": planting.plant.family,
            },
            "growth_phase": planting.growthPhase,
            "health_level": planting.healthLevel,
            "water_level": planting.waterLevel,
            "planted_at": planting.plantedAt.isoformat(),
            "last_watered_at": planting.lastWateredAt.isoformat(),
        }

    return JsonResponse(data)


@csrf_exempt
def water_plant(request, username, garden_name, pot_number):
    if request.method != "PATCH":
        return HttpResponseNotAllowed(["PATCH"])

    garden = get_object_or_404(
        Garden,
        user__username=username,
        name=garden_name,
    )

    pot = get_object_or_404(
        Pot,
        garden=garden,
        number=pot_number,
    )

    planting = getattr(pot, "plantingarden", None)

    if planting is None:
        return JsonResponse(
            {"error": "There is no plant in this pot."},
            status=404,
        )

    planting.waterLevel = 100.0
    planting.healthLevel = min(100.0, planting.healthLevel + 5.0)
    planting.lastWateredAt = timezone.now()
    planting.save()

    data = {
        "message": "Plant watered successfully.",
        "pot_number": pot.number,
        "plant": {
            "scientific_name": planting.plant.scientificName,
            "common_name": planting.plant.commonName,
        },
        "water_level": planting.waterLevel,
        "health_level": planting.healthLevel,
        "last_watered_at": planting.lastWateredAt.isoformat(),
    }

    return JsonResponse(data, status=200)
