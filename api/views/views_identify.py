# from django.shortcuts import render
import os
import urllib

import requests
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..models import GrowthState, Image, Plant, User
from .views_info import importPlant

PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"
ALLOWED_ORGANS = {"leaf", "flower"}


@api_view(["POST"])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def identifyPlant(request):

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

    api_key = os.getenv("PLANTNET_API_KEY")
    if not api_key:
        return Response({"detail": "PLANTNET_API_KEY is not configured."}, status=500)

    files = {
        "images": (
            file_obj.name,
            file_obj,
            file_obj.content_type or "application/octet-stream",
        )
    }

    r = requests.post(
        f"{PLANTNET_URL}?api-key={api_key}",
        files=files,
        data={"organs": organ},
        timeout=30,
    )

    if r.status_code != 200:
        return Response(
            {
                "detail": "PlantNet identification failed.",
                "status_code": r.status_code,
                "body": r.text[:500],
            },
            status=502,
        )

    payload = r.json()

    results = payload.get("results") or []
    if not results:
        return Response({"detail": "No identification results."}, status=422)

    best = results[0]
    species = best.get("species") or {}
    scientificName = species.get("scientificNameWithoutAuthor") or species.get(
        "scientificName"
    )

    if not scientificName:
        return Response(
            {"detail": "PlantNet response missing scientific name."}, status=422
        )

    importPlant(scientificName)
    plant = Plant.objects.get(scientificName=scientificName)

    uploader = None
    if username:
        try:
            uploader = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"username": "User not found."}, status=404)

    img = Image.objects.create(
        uploader=uploader,
        url=file_obj,
        plant=None,
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


POLLINATIONS_URL = "https://gen.pollinations.ai/image"


def createPlantImages(plant_id):
    try:
        plant = Plant.objects.get(id=plant_id)
    except Plant.DoesNotExist:
        return {"error": "Plant not found"}

    scientificName = plant.scientificName
    safe_name = urllib.parse.quote(scientificName)

    api_key = os.getenv("POLLINATIONS_API_KEY")

    style = f"""
        game-ready 2D farming game sprite of a {scientificName} plant,
        recognizable real-world characteristics of {scientificName},
        botanically distinguishable silhouette,
        stem, leaves and flowers only,
        only the plant visible,
        no pot, no flower pot, no planter, no container,
        no soil, no dirt, no ground, no base tile, no surface,
        no shadow underneath, no table,
        floating plant, isolated object cutout, sticker-like sprite,
        clean cut edges,
        transparent background, PNG with alpha channel,
        centered composition,
        bright vibrant colors,
        soft cartoon shading,
        no realistic photo, no background scene, no environment, no decoration,
        no text, no watermark
        """.strip()

    for state_value, state_label in GrowthState.choices:

        prompt = f"{safe_name} plant, {state_label} stage, {style}"
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"{POLLINATIONS_URL}/{encoded_prompt}?model=flux"

        response = requests.get(
            image_url, headers={"Authorization": f"Bearer {api_key}"}, timeout=60
        )

        if response.status_code == 200:
            image_content = ContentFile(response.content)

            new_image = Image(plant=plant)

            filename = f"{safe_name}_{state_value}.png"
            new_image.url.save(filename, image_content, save=True)

    return None
