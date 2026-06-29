from .estrategia import EstrategiaModalidad


class EstrategiaPresencial(EstrategiaModalidad):
    def descripcion(self):
        return "Clase dictada en aula fisica."

    def duracion_horas(self):
        return 2


class EstrategiaVirtual(EstrategiaModalidad):
    def descripcion(self):
        return "Clase dictada mediante plataforma virtual."

    def duracion_horas(self):
        return 1


class EstrategiaHibrida(EstrategiaModalidad):
    def descripcion(self):
        return "Clase combinada entre encuentros presenciales y virtuales."

    def duracion_horas(self):
        return 3


class EstrategiaSemipresencial(EstrategiaModalidad):
    def descripcion(self):
        return "Clase semipresencial con actividades presenciales y virtuales."

    def duracion_horas(self):
        return 2
