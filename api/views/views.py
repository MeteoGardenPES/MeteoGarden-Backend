from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Garden, Pot


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