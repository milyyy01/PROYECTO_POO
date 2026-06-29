from __future__ import annotations
from datetime import date, datetime
from models.modalidad import Modalidad

class Oferta:
    def __init__(self, id_oferta=None, carrera=None, modalidad=None, cupo_total=30, precio=0,
                 fecha_apertura=None, fecha_cierre=None, cupos_total=None,
                 cupos_ocupados=0, puntaje_minimo=0, puntaje_maximo=1000, sede=None):
        self._id_oferta = id_oferta
        self._carrera = carrera
        self._modalidad = self._normalizar_modalidad(modalidad, id_oferta)
        self._cupo_total = cupos_total if cupos_total is not None else cupo_total
        self._cupo_disponible = max(self._cupo_total - cupos_ocupados, 0)
        self.puntaje_minimo = puntaje_minimo
        self.puntaje_maximo = puntaje_maximo
        self._precio = precio
        self._fecha_apertura = self._convertir_fecha(fecha_apertura)
        self._fecha_cierre = self._convertir_fecha(fecha_cierre)
        self._sede = sede
        self._periodos = []

    @staticmethod
    def _normalizar_modalidad(modalidad, id_oferta):
        """
        Acepta un objeto Modalidad (caso normal) o, por compatibilidad con
        datos antiguos guardados como string ("Presencial", "Virtual", ...),
        lo convierte automaticamente usando Modalidad.crear().
        Si no se especifica, se usa "Presencial" por defecto.
        """
        if isinstance(modalidad, Modalidad):
            return modalidad
        tipo = modalidad if isinstance(modalidad, str) else "Presencial"
        return Modalidad.crear(id_modalidad=id_oferta, tipo=tipo)

    def _convertir_fecha(self, fecha):
        if isinstance(fecha, str):
            return datetime.strptime(fecha, "%Y-%m-%d").date()
        return fecha

    @property
    def id_oferta(self):
        return self._id_oferta

    @property
    def carrera(self):
        return self._carrera

    @property
    def modalidad(self):
        return self._modalidad

    @property
    def cupo_disponible(self):
        return self._cupo_disponible

    @property
    def cupos_total(self):
        return self._cupo_total

    @property
    def cupos_ocupados(self):
        return self._cupo_total - self._cupo_disponible

    @property
    def sede(self):
        return self._sede

    @property
    def periodos(self):
        return self._periodos

    @property
    def fecha_apertura(self):
        return self._fecha_apertura

    @property
    def fecha_cierre(self):
        return self._fecha_cierre

    def set_sede(self, sede):
        self._sede = sede

    def agregar_periodo(self, periodo):
        if periodo not in self._periodos:
            self._periodos.append(periodo)
            periodo.set_oferta(self)

    def reducir_cupo(self, cantidad=1):
        if self._cupo_disponible >= cantidad:
            self._cupo_disponible -= cantidad
        else:
            raise ValueError("No hay suficientes cupos disponibles")

    def aprobar_inscripcion(self, estudiante, puntaje):
        if self._cupo_disponible <= 0:
            return "Inscripción rechazada: no hay cupos disponibles."
        if not (self.puntaje_minimo <= puntaje <= self.puntaje_maximo):
            return (
                f"Inscripción rechazada: puntaje {puntaje} no está en el rango "
                f"[{self.puntaje_minimo} - {self.puntaje_maximo}]."
            )
        self.reducir_cupo()
        if self._carrera:
            self._carrera._inscribir_estudiante(estudiante)
            estudiante.carrera = self._carrera
        if self._sede:
            estudiante.sede = self._sede
        return f"Inscripción aprobada para '{estudiante.nombre}'."

    def aumentar_cupo(self, cantidad=1):
        if self._cupo_disponible + cantidad <= self._cupo_total:
            self._cupo_disponible += cantidad
        else:
            raise ValueError("No se puede superar el cupo total")

    def __str__(self):
        fecha_ap = self._fecha_apertura.strftime("%Y-%m-%d") if self._fecha_apertura else "N/A"
        fecha_cie = self._fecha_cierre.strftime("%Y-%m-%d") if self._fecha_cierre else "N/A"
        return (
            f"Oferta {self._carrera} ({self._modalidad.tipo}) - "
            f"Cupo: {self._cupo_disponible}/{self._cupo_total} - "
            f"Precio: ${self._precio} - "
            f"Periodo: {fecha_ap} a {fecha_cie}"
        )
