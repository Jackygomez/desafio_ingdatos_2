#manejará la lógica para obtener y actualizar los códigos postales desde la API

import requests
from data_access import fetch_coordinates, update_postcode
import logging

def get_and_update_postcodes():
    coordinates = fetch_coordinates()
    postcodes = []
    errors = []

    for id, latitude, longitude in coordinates:
        url = f"https://api.postcodes.io/postcodes?lon={longitude}&lat={latitude}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                postcode = data['result'][0]['postcode'] if data['result'] else None
                if postcode:
                    update_postcode(id, postcode)
                    postcodes.append(postcode)
                else:
                    errors.append(f"No postcode found for coordinates ({latitude}, {longitude}).")
            else:
                errors.append(f"API request failed for coordinates ({latitude}, {longitude}) with status code {response.status_code}.")
        except requests.exceptions.RequestException as e:
            errors.append(f"Network error when attempting to fetch postcode: {e}")
        except Exception as e:
            errors.append(f"Error processing coordinates ({latitude}, {longitude}): {str(e)}")

    return postcodes, errors
