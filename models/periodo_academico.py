from datetime import date


class PeriodoAcademico:
    def __init__(self, fecha_inicio, fecha_fin, anio, semestre):
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.anio = anio
        self.semestre = semestre
        self.activo = False

    def activar_periodo(self):
        self.activo = True
        return "Periodo académico activado."

    def culminar_periodo(self):
        self.activo = False
        return "Periodo académico culminado."

    def duracion_periodo(self):
        return (self.fecha_fin - self.fecha_inicio).days

    def esta_activo(self):
        hoy = date.today()
        return self.activo and self.fecha_inicio <= hoy <= self.fecha_fin
