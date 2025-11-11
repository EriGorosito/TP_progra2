from enum import Enum

class Especie(Enum):
    PERRO = "perro"
    GATO = "gato"
    PAJARO = "pajaro"
    TORTUGA = "tortuga"
    CONEJO = "conejo"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member