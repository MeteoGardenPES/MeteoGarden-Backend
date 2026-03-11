# from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Plant, Image, User
from django.conf import settings
import requests

# Create your views here.
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"health status": "ok"})


PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"
ALLOWED_ORGANS = {"leaf", "flower", "fruit"}


@api_view(["POST"])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def identifyAndSavePlant(request):

    username = request.data.get("username")
    file_obj = request.FILES.get("image")
    organ = request.data.get("organs", "leaf")

    if not file_obj:
        return Response({"image": "Image file is required."}, status=400)

    if organ not in ALLOWED_ORGANS:
        return Response(
            {"organs": f"Invalid value. Must be one of: {sorted(ALLOWED_ORGANS)}"},
            status=400,
        )

    api_key = getattr(settings, "PLANTNET_API_KEY", None)
    if not api_key:
        return Response({"detail": "PLANTNET_API_KEY is not configured."}, status=500)

    files = {
        "images": (file_obj.name, file_obj, file_obj.content_type or "application/octet-stream")
    }

    r = requests.post(
        f"{PLANTNET_URL}?api-key={api_key}",
        files=files,
        data={"organs": organ},
        timeout=30,
    )

    if r.status_code != 200:
        return Response(
            {"detail": "PlantNet identification failed.", "status_code": r.status_code, "body": r.text[:500]},
            status=502,
        )

    payload = r.json()

    results = payload.get("results") or []
    if not results:
        return Response({"detail": "No identification results."}, status=422)

    best = results[0]
    species = (best.get("species") or {})
    scientificName = species.get("scientificNameWithoutAuthor") or species.get("scientificName")
    commonNames = species.get("commonNames") or []

    if not scientificName:
        return Response({"detail": "PlantNet response missing scientific name."}, status=422)

    common_name = commonNames[0] if commonNames else scientificName


    plant, created = Plant.objects.get_or_create(
        scientificName=scientificName,
        defaults={
            "commonName": common_name,
            "family": (species.get("family") or {}).get("scientificName", "") if isinstance(species.get("family"), dict) else "",
            "canFlower": False,
            "minTemperature": 0.0,
            "maxTemperature": 50.0,
        },
    )

    if not created:
        changed = False
        if not plant.commonName and common_name:
            plant.commonName = common_name
            changed = True
        if not plant.family:
            fam = (species.get("family") or {})
            if isinstance(fam, dict) and fam.get("scientificName"):
                plant.family = fam["scientificName"]
                changed = True
        if changed:
            plant.save()

    uploader = None
    if username:
        try:
            uploader = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"username": "User not found."}, status=404)

    img = Image.objects.create(
        uploader=uploader,
        url=file_obj,
        plant= plant,
    )

    return Response(
        {
            "plant": {
                "scientificName": plant.scientificName,
                "commonName": plant.commonName,
                "family": plant.family,
            },
            "image": {
                "id": img.id,
                "url": img.url.url if img.url else None,
                "width": img.width,
                "height": img.height,
            },
            "plantnet": {
                "score": best.get("score"),
            },
        },
        status=201,
    )