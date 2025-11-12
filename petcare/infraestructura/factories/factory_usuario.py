from petcare.infraestructura.models.usuario_model import Cliente, Cuidador

class UserFactory:
    """
    Patrón Factory para crear instancias de Cliente o Cuidador 
    basándose en el tipo de usuario proporcionado.
    """
    @staticmethod
    def create_user(tipo: str, **kwargs):
        tipo = tipo.lower()


        if tipo == "cliente":
            return Cliente(**kwargs)
        elif tipo == "cuidador":
            return Cuidador(**kwargs)
        else:
            raise ValueError(f"Tipo de usuario no válido: {tipo}")

