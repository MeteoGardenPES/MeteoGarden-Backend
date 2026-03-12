from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User


# Create your views here.
@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"health status": "ok"})


# Register view
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    user = User.objects.create_user(
        username=request.data["username"],
        password=request.data["password"],
        email=request.data["email"],
        city=request.data["city"],
        language=request.data["language"],
        numPlantsCollected=0,
    )
    token, created = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "message": "User created"})


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
    return Response({"error": "Credencials incorrectes"}, status=400)


# View profile
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    return Response(
        {
            "username": user.username,
            "email": user.email,
            "city": user.city,
            "codi_estacio": user.codi_estacio,
            "language": user.language,
            "lastEntry": user.lastEntry,
            "numPlantsCollected": user.numPlantsCollected,
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
    if "password" in data:
        user.set_password(data["password"])
    try:
        user.save()
        return Response({"message": "Perfil actualitzat"})
    except Exception as e:
        return Response({"error": str(e)}, status=400)
