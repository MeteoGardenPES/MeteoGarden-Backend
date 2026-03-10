import requests
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# funció reutilitzable per obtenir un valor meteorològic
def get_meteo_value(station_code, variable_code):

    url = (
        "https://analisi.transparenciacatalunya.cat/resource/nzvn-apee.json"
        f"?codi_estacio={station_code}"
        f"&codi_variable={variable_code}"
        "&$order=data_lectura desc"
        "&$limit=1"
    )

    response = requests.get(url, headers={}).json()

    if not response:
        return None

    return response[0]["valor_lectura"]


@api_view(["GET"])
def current_weather(request):
    #stationName = "Prades"
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
def get_stations(request):

    try:
        url = (
            "https://analisi.transparenciacatalunya.cat/resource/yqwd-vj5e.json"
            "?$select=nom_estacio, codi_estacio"
            "&nom_estat=Operativa"
            "&$order=nom_estacio"
        )

        response = requests.get(url).json()

        stations = []

        for station in response:
            stations.append({
                "name": station["nom_estacio"],
                "code": station["codi_estacio"]
            })

        return Response(stations)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
