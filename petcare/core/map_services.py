# import requests
# import math
# import os

# # Si tenés una API key de Google Maps (colocala en tu .env)
# GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# def calcular_distancia_km(origen: tuple, destino: tuple) -> float:
#     """
#     Calcula la distancia (en km) entre dos ubicaciones (lat, lon).
#     Si no hay API Key, usa distancia euclidiana como fallback.
#     """
#     if not GOOGLE_MAPS_API_KEY:
#         # Distancia euclidiana simple (fallback)
#         lat1, lon1 = origen
#         lat2, lon2 = destino
#         R = 6371  # radio de la tierra en km
#         dlat = math.radians(lat2 - lat1)
#         dlon = math.radians(lon2 - lon1)
#         a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
#         c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#         return R * c

#     # Si hay API key, usar Google Distance Matrix API
#     url = "https://maps.googleapis.com/maps/api/distancematrix/json"
#     params = {
#         "origins": f"{origen[0]},{origen[1]}",
#         "destinations": f"{destino[0]},{destino[1]}",
#         "key": GOOGLE_MAPS_API_KEY,
#     }

#     response = requests.get(url, params=params)
#     data = response.json()

#     try:
#         distancia_metros = data["rows"][0]["elements"][0]["distance"]["value"]
#         return distancia_metros / 1000.0
#     except Exception:
#         return float("inf")

def calcular_distancia_km(origen, destino):
    """
    Mock temporal de cálculo de distancia.
    En el futuro usará la API real (por ejemplo, Google Maps).
    """
    if not origen or not destino:
        return 9999  # Devuelve una distancia grande si falta info

    # Simula una distancia aleatoria entre 1 y 20 km
    import random
    return round(random.uniform(1, 20), 2)
