from abc import ABC, abstractmethod


class EstrategiaModalidad(ABC):
    """
    Interfaz del patron Strategy. Cada modalidad concreta (Presencial,
    Virtual, Hibrida, Semipresencial) implementa su propia variante de
    descripcion() y duracion_horas().
    """

    @abstractmethod
    def descripcion(self):
        pass

    def duracion_horas(self):
        return 2
