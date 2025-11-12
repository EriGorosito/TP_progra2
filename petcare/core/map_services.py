import requests
import math

class GeoService:
    @staticmethod
    def geocode(address: str):
        """
        Usar Nominatim (OpenStreetMap) para convertir address → lat/lon
        """
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }

        headers = {
            "User-Agent": "PetCare/1.0"
        }

        resp = requests.get(url, params=params, headers=headers)

        if resp.status_code != 200:
            raise Exception("Error al consultar OSM")

        data = resp.json()

        if not data:
            return None

        return float(data[0]["lat"]), float(data[0]["lon"])
    

def distancia_geodesica(origen, destino):
    lat1, lon1 = origen
    lat2, lon2 = destino

    R = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


