from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.estudiante import Estudiante
    from models.sede import Sede
    from models.carrera import Carrera
    from models.periodo_academico import PeriodoAcademico

class Oferta:
    def __init__(
        self,
        cupos_total,
        cupos_ocupados,
        puntaje_minimo,
        puntaje_maximo,
        fecha_apertura,
        fecha_cierre,
        sede: "Sede" = None,
        carrera: "Carrera" = None,
        periodo_academico: "PeriodoAcademico" =None
    ):

        if cupos_total <= 0:
            raise ValueError("El total de cupos debe ser mayor a cero.")
        if puntaje_minimo > puntaje_maximo:
            raise ValueError("El puntaje mínimo no puede ser mayor al máximo.")
        
        self._cupos_total = cupos_total
        self._cupos_ocupados = cupos_ocupados
        self.puntaje_minimo = puntaje_minimo
        self.puntaje_maximo = puntaje_maximo
        self.fecha_apertura = fecha_apertura
        self.fecha_cierre = fecha_cierre
        self._sede = sede
        self._carrera = carrera
        self.periodo_academico = periodo_academico
        self.abierta = True
        self.__inscripciones_rechazadas = []
        
    # Propiedades:
    
    @property
    def cupos_total(self):
        return self._cupos_total
 
    @property
    def cupos_ocupados(self):
        return self._cupos_ocupados
 
    @property
    def sede(self):
        return self._sede
 
    @property
    def carrera(self):
        return self._carrera
    
    # Métodos: 
     
    def estado(self):
        return "Abierta" if self.abierta else "Cerrada"

    def verificar_cupos(self):
        disponibles = self._cupos_total - self._cupos_ocupados
        if disponibles > 0:
            print(f"Cupos disponibles: {disponibles} de {self._cupos_total}.")
            return True
        print("No hay cupos disponibles en esta oferta.")
        return False

    def aprobar_inscripcion(self, estudiante: "Estudiante", puntaje):
        if not self.abierta:
            return f"Inscripción rechazada: la oferta está cerrada."
        if not self.verificar_cupos():
            return f"Inscripción rechazada: no hay cupos disponibles."
        if not (self.puntaje_minimo <= puntaje <= self.puntaje_maximo):
            return (f"Inscripción rechazada: puntaje {puntaje} no está en el rango "
                    f"[{self.puntaje_minimo} - {self.puntaje_maximo}].")
        self._cupos_ocupados += 1
        # Si hay carrera asociada, inscribe al estudiante en ella
        if self._carrera:
            self._carrera._inscribir_estudiante(estudiante)
        mensaje = f"Inscripción aprobada para '{estudiante.nombre}' en esta oferta."
        print(mensaje)
        return mensaje

    def rechazar_inscripcion(self, estudiante: "Estudiante"):
        self.__inscripciones_rechazadas.append(estudiante.nombre)
        mensaje = f"Inscripción rechazada para '{estudiante.nombre}'."
        print(mensaje)
        return mensaje

    def ver_cupo_sede(self):
        disponibles = self._cupos_total - self._cupos_ocupados
        sede_nombre = self._sede.nombre_sede if self._sede else "Sin sede asignada"
        print(f"Cupos disponibles en sede '{sede_nombre}': {disponibles}")
        return disponibles

    def cerrar_ofertas(self):
        self.abierta = False
        return "Oferta cerrada."
    
    def __str__(self):
        carrera_nombre = self._carrera.nombre_carrera if self._carrera else "Sin carrera"
        sede_nombre = self._sede.nombre_sede if self._sede else "Sin sede"
        return (
            f"[Oferta] Carrera: {carrera_nombre} - Sede: {sede_nombre} - "
            f"Cupos: {self._cupos_ocupados}/{self._cupos_total} - "
            f"Puntaje: {self.puntaje_minimo}-{self.puntaje_maximo} - "
            f"Estado: {self.estado()}"
        )
