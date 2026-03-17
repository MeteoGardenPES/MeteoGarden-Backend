import os
import requests

from dotenv import load_dotenv
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

load_dotenv()

XEMA_METEO_TOKEN = os.getenv("XEMA_METEO_TOKEN")


# funció reutilitzable per obtenir un valor meteorològic
def get_meteo_value(station_code, variable_code):

    url = (
        "https://analisi.transparenciacatalunya.cat/resource/nzvn-apee.json"
        f"?codi_estacio={station_code}"
        f"&codi_variable={variable_code}"
        "&$order=data_lectura desc"
        "&$limit=1"
    )

    response = requests.get(url, headers={"X-App-Token": XEMA_METEO_TOKEN}).json()

    if not response:
        return None

    return response[0]["valor_lectura"]


# s'ha de canviar pq ja tindrem el codi
@api_view(["GET"])
@permission_classes([AllowAny])
def current_weather(request):
    # stationName = "Òdena"
    stationName = request.GET.get("stationName")
    try:
        # trobar codi de l'estació de la ciutat que volem
        station_url = f"https://analisi.transparenciacatalunya.cat/resource/yqwd-vj5e.json?nom_estacio={stationName}"
        station_response = requests.get(station_url).json()

        if not station_response:
            return Response({"error": "Station not found"}, status=404)

        station_code = station_response[0]["codi_estacio"]

        # Codis dels valors
        TEMP_CODE = "32"
        PREC_CODE = "35"
        WIND_CODE = "30"

        # obtenir dades amb la funció
        temperature = get_meteo_value(station_code, TEMP_CODE)
        precipitation = get_meteo_value(station_code, PREC_CODE)
        wind = get_meteo_value(station_code, WIND_CODE)

        return Response(
            {
                "stationName": stationName,
                "temperature": temperature,
                "precipitation": precipitation,
                "wind": wind,
            }
        )

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_stations(request):

    try:
        url = (
            "https://analisi.transparenciacatalunya.cat/resource/yqwd-vj5e.json"
            "?$select=nom_estacio,codi_estacio"
            "&$where=nom_estat_ema='Operativa'"
            "&$order=nom_estacio"
        )

        response = requests.get(url).json()

        if not isinstance(response, list):
            return Response(
                {"error": "Invalid response from API", "data": response}, status=500
            )

        stations = []

        for station in response:
            stations.append(
                {"name": station["nom_estacio"], "code": station["codi_estacio"]}
            )

        return Response(stations)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
