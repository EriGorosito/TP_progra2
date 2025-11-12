from petcare.core.map_services import GeoService


def update_user_address(user_repo, user_id, new_address):
    """
    Actualiza la dirección de un usuario, geocodifica la nueva dirección
    y guarda la información resultante (coordenadas y URL del mapa).
    """
    user = user_repo.get_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    # Llama al servicio externo para obtener coordenadas
    coords = GeoService.geocode(new_address)
    if coords is None:
        raise ValueError("No se pudo geocodificar la dirección")

    lat, lon = coords
    # Aquí se mantiene la línea para la URL, ya que es una cadena continua.
    map_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}"

    # Llama al método de dominio para actualizar los datos
    user.update_address(
        new_address,
        lat,
        lon,
        map_url
    )

    user_repo.save(user)

    return user