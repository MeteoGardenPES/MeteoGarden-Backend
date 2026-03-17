import random

from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import Garden, GrowthState, Inventory, Plant, PlantInGarden, Pot, User


@api_view(["POST"])
def collect_plant(request):

    username = request.data.get("username")
    garden_name = request.data.get("garden")
    pot_num = request.data.get("pot")
    scientificName = request.data.get("plant")

    if not all([username, garden_name, pot_num, scientificName]):
        return Response({"error": "Missing required fields"}, status=400)

    try:
        user = User.objects.get(username=username)
        garden = Garden.objects.get(user=user, name=garden_name)
        pot = Pot.objects.get(garden=garden, number=pot_num)
        plant = Plant.objects.get(scientificName=scientificName)
        plantGarden = PlantInGarden.objects.get(pot=pot, plant=plant)

    except (
        User.DoesNotExist,
        Garden.DoesNotExist,
        Pot.DoesNotExist,
        Plant.DoesNotExist,
        PlantInGarden.DoesNotExist,
    ) as e:
        return Response({"error": f"Resource not found: {str(e)}"}, status=404)

    if plantGarden.growthPhase != GrowthState.MATURE:
        return Response({"error": "Growth phase must be mature"}, status=404)

    plantGarden.delete()

    pot.occupied = False
    pot.save()

    inventory = Inventory.objects.get(user=user)
    inventory.coins += 2
    p = random.randint(1, 100)
    if p < 30:
        inventory.addSeed(scientificName, 1)
    inventory.save()

    return Response(
        {"message": "Plant collected successfully", "new_balance": inventory.coins},
        status=200,
    )
