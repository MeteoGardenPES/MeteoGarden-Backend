# from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Create your views here.
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"health status": "ok"})

from rest_framework import status
from .services.plants import save_or_update_plant_info

@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def importPlant(request):
    if request.method == "GET":
        scientific_name = request.query_params.get("scientificName")
        lang = request.query_params.get("lang", "ca")
    else:
        scientific_name = request.data.get('scientificName')
        lang = request.data.get('lang', 'ca')

    if not scientific_name:
        return Response({"error": "scientificName is required"}, status=400)

    try:
        plant = save_or_update_plant_info(scientific_name, lang=lang)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    if plant is None:
        return Response({"error": "Plant not found"}, status=404)

    return Response(plant, status=200)




