from petcare.domain.usuario import Cliente, Cuidador, Usuario

class UsuarioFactory:
    @staticmethod
    def crear_usuario(tipo: str, id: int, nombre: str, email: str, contrasena: str, descripcion: str = "") -> Usuario:
        """
        Crea un objeto de tipo Usuario según el parámetro 'tipo'.
        :param tipo: Puede ser 'cliente' o 'cuidador'.
        """
        tipo = tipo.lower()
        if tipo == "cliente":
            return Cliente(id, nombre, email, contrasena)
        elif tipo == "cuidador":
            return Cuidador(id, nombre, email, contrasena, descripcion)
        else:
            raise ValueError(f"Tipo de usuario no válido: {tipo}")
