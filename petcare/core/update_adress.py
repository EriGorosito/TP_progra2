from petcare.core.map_services import GeoService


def update_user_address(user_repo, user_id, new_address):
    user = user_repo.get_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    coords = GeoService.geocode(new_address)   # ← llamamos servicio externo
    if coords is None:
        raise ValueError("No se pudo geocodificar la dirección")

    lat, lon = coords
    map_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}"

    user.update_address(
        new_address,
        lat,
        lon,
        map_url
    )

    user_repo.save(user)

    return user