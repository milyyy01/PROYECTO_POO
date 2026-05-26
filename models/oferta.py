class Oferta:
    def __init__(
        self,
        cupos_total,
        cupos_ocupados,
        puntaje_minimo,
        puntaje_maximo,
        fecha_apertura,
        fecha_cierre,
        sede=None,
        carrera=None,
        periodo_academico=None
    ):
        self.cupos_total = cupos_total
        self.cupos_ocupados = cupos_ocupados
        self.puntaje_minimo = puntaje_minimo
        self.puntaje_maximo = puntaje_maximo
        self.fecha_apertura = fecha_apertura
        self.fecha_cierre = fecha_cierre
        self.sede = sede
        self.carrera = carrera
        self.periodo_academico = periodo_academico
        self.abierta = True

    def estado(self):
        return "Abierta" if self.abierta else "Cerrada"

    def verificar_cupos(self):
        return self.cupos_ocupados < self.cupos_total

    def aprobar_inscripcion(self, estudiante, puntaje):
        if not self.abierta:
            return "La oferta está cerrada."

        if not self.verificar_cupos():
            return "No hay cupos disponibles."

        if puntaje < self.puntaje_minimo or puntaje > self.puntaje_maximo:
            return "El puntaje no cumple con los requisitos."

        self.cupos_ocupados += 1
        return f"Inscripción aprobada para {estudiante.nombre}."

    def rechazar_inscripcion(self, estudiante):
        return f"Inscripción rechazada para {estudiante.nombre}."

    def ver_cupo_sede(self):
        return self.cupos_total - self.cupos_ocupados

    def cerrar_ofertas(self):
        self.abierta = False
        return "Oferta cerrada."
