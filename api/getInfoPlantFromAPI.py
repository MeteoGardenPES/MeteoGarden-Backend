import requests
import os
import django
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import transaction
from .models import Plant

@transaction.atomic
def save_or_update_plant_info(details: dict):
    sci_list = details.get('scientific_name') or []
    sci = sci_list[0] if sci_list else None

    plant, _created = Plant.objects.update_or_create(
        scientificName=sci,
        defaults={
            'commonName': details.get('common_name'),
            'family': details.get('family'),
            'canFlower': details.get('canFlower'),
            'minTemperature': details.get('minTemperature'),
            'maxTemperature': details.get('maxTemperature'),
            'description': details.get('description'),
        },
    )



def translate(text, api_key, lang):
    url = "https://translation.googleapis.com/language/translate/v2"

    params = {
        'q': text,
        'target': lang,
        'format': 'text',
        'key': api_key
    }

    response = requests.post(url, params=params)

    if response.status_code == 200:
        data = response.json()
        translation = (data['data']['translations'][0]['translatedText'])
        return f"{translation}"
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY")

temp = [(-51.1, -45.6), (-45.6, -40), (-40, -34.4), (-34.4, -28.9), (-28.9, -23.3), (-23.3, -17.8), (-17.8, -12.2),
        (-12.2, -6.7), (-6.7, -1.1), (-1.1, 4.4), (4.4, 10), (10, 15.6), (15.6, 21.1)]


def getTemperature(zone_min, zone_max):
    zone_min = int(str(zone_min))
    zone_max = int(str(zone_max))
    return f"Temperatura mínima: {temp[zone_min - 1][0]}, {temp[zone_min - 1][1]} °C\nTemperatura màxima: {temp[zone_max - 1][0]}, {temp[zone_max - 1][1]} °C"


def getPlantInfo(scientific_name, lang):
    url = "https://perenual.com/api/species-list?"
    params = {
        'key': os.getenv("PERENUAL_API_KEY"),
        'q': scientific_name
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if not data['data']:
            print("No s'ha trobat cap planta amb aquest nom científic.")
            return
        else:
            id = data['data'][0]['id']
            print(f"ID de la planta: {id}")
            url_details = "https://perenual.com/api/v2/species/details/" + str(id)
            params_details = {
                'key': os.getenv("PERENUAL_API_KEY")
            }
            response_details = requests.get(url_details, params=params_details)
            if response_details.status_code == 200:
                print(response_details.status_code)
                details = response_details.json()
                print(
                    f"Nom comú: {translate(details.get('common_name', None), api_key, lang).capitalize()}")
                print(f"Nom científic: {details['scientific_name'][0]}")
                print(f"Familia: {details.get('family', None)}")
                print(f"potFlorir: {details.get('flowers', None)}")

                descripció = translate(details.get('description', None), api_key, lang)
                print(f"Descripció: {descripció}")

                if details.get('hardiness') is not None:
                    hardiness1 = (details['hardiness']['min'])
                    hardiness2 = (details['hardiness']['max'])
                    print(getTemperature(hardiness1, hardiness2))
                    temp = getTemperature(hardiness1, hardiness2).split("\n")

                save_details = {
                    "common_name": details.get('common_name', None),
                    "scientific_name": details.get('scientific_name', None),
                    "family": details.get('family', None),
                    "canFlower": details.get('flowers', None),
                    "minTemperature": float(temp[0].split(": ")[1].split(',')[0]),
                    "maxTemperature": float(temp[1].split(":")[1].split(', ')[1].split(' ')[0]),
                    "description": descripció,
                }

                save_or_update_plant_info(save_details)
                return save_details

            else:
                print(f"error: {response_details.status_code}")
                print(response_details.text)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


getPlantInfo("Abies concolor", 'ca')
