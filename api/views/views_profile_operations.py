from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..models import Garden, Inventory, User


# Create your views here.
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"health status": "ok"})


# Register view
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):

    # Check if the garden name isn't empty
    garden_name = request.data.get("gardenName")
    if not garden_name:
        return Response({"error": "Garden name is mandatory"}, status=400)

    user = User.objects.create_user(
        username=request.data["username"],
        password=request.data["password"],
        email=request.data["email"],
        city=request.data["city"],
        language=request.data["language"],
        numPlantsCollected=0,
        stationCode=request.data["stationCode"],
    )

    # Create the inventory
    Inventory.objects.create(user=user)

    # Create the garden
    Garden.objects.create(user=user, name=garden_name)

    token, created = Token.objects.get_or_create(user=user)
    return Response(
        {"token": token.key, "message": "User, garden and inventory created"}
    )


# Login view
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data["username"]
    password = request.data["password"]
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "username": user.username, "message": "Login correcte"}
        )
    return Response({"error": "Wrong credentials"}, status=400)


# View profile
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    inventory = Inventory.objects.get(user=user)
    return Response(
        {
            "username": user.username,
            "email": user.email,
            "city": user.city,
            "stationCode": user.stationCode,
            "language": user.language,
            "lastEntry": user.lastEntry,
            "numPlantsCollected": user.numPlantsCollected,
            "numCoins": inventory.coins,
        }
    )


# Edit profile
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_profile(request):
    user = request.user
    data = request.data
    user.email = data.get("email", user.email)
    user.city = data.get("city", user.city)
    user.language = data.get("language", user.language)
    user.numPlantsCollected = data.get("numPlantsCollected", user.numPlantsCollected)
    user.stationCode = data.get("stationCode", user.stationCode)
    if "password" in data:
        user.set_password(data["password"])
    try:
        user.save()
        return Response({"message": "Actualized profile"})
    except Exception as e:
        return Response({"error": str(e)}, status=400)
