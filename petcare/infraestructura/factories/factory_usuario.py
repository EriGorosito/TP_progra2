from petcare.infraestructura.models.usuario_model import Cliente, Cuidador

class UsuarioCreator:
    """
    Clase base del patrón Factory Method.

    Define la interfaz para crear usuarios concretos.
    """

    def create(self, **kwargs):
        """Método que deben implementar los creadores concretos."""
        raise NotImplementedError()


class ClienteCreator(UsuarioCreator):
    """Creador concreto encargado de instanciar usuarios del tipo Cliente."""

    def create(self, **kwargs):
        """Crea y retorna un objeto Cliente."""
        return Cliente(tipo="cliente", **kwargs)


class CuidadorCreator(UsuarioCreator):
    """Creador concreto encargado de instanciar usuarios del tipo Cuidador."""

    def create(self, **kwargs):
        """Crea y retorna un objeto Cuidador."""
        return Cuidador(tipo="cuidador", **kwargs)


class UserFactory:
    """Factory que delega la creación de usuarios a su creador correspondiente."""
    
    creators = {
        "cliente": ClienteCreator(),
        "cuidador": CuidadorCreator(),
    }

    @classmethod
    def create_user(cls, tipo: str, **kwargs):
        """
        Crea un usuario según el tipo especificado.
        """
        tipo = tipo.lower()
        if tipo not in cls.creators:
            raise ValueError("Tipo de usuario inválido.")
        return cls.creators[tipo].create(**kwargs)
