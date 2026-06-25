from __future__ import annotations
from datetime import date, datetime

class Oferta:
    def __init__(self, id_oferta, carrera, modalidad, cupo_total=30, precio=0,
                 fecha_apertura=None, fecha_cierre=None):
        self._id_oferta = id_oferta
        self._carrera = carrera
        self._modalidad = modalidad
        self._cupo_total = cupo_total
        self._cupo_disponible = cupo_total
        self._precio = precio
        self._fecha_apertura = self._convertir_fecha(fecha_apertura)
        self._fecha_cierre = self._convertir_fecha(fecha_cierre)
        self._sede = None
        self._periodos = []

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

    def aumentar_cupo(self, cantidad=1):
        if self._cupo_disponible + cantidad <= self._cupo_total:
            self._cupo_disponible += cantidad
        else:
            raise ValueError("No se puede superar el cupo total")

    def __str__(self):
        fecha_ap = self._fecha_apertura.strftime("%Y-%m-%d") if self._fecha_apertura else "N/A"
        fecha_cie = self._fecha_cierre.strftime("%Y-%m-%d") if self._fecha_cierre else "N/A"
        return (
            f"Oferta {self._carrera} ({self._modalidad}) - "
            f"Cupo: {self._cupo_disponible}/{self._cupo_total} - "
            f"Precio: ${self._precio} - "
            f"Periodo: {fecha_ap} a {fecha_cie}"
        )