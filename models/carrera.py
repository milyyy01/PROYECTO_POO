from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.asignatura import Asignatura
    from models.estudiante import Estudiante
    from models.sede import Sede

class Carrera: 
    def __init__(self, id_carrera, nombre_carrera, facultad, duracion_semestre, creditos_totales, cupos_totales):
        self._id_carrera = id_carrera
        self._nombre_carrera = nombre_carrera
        self._facultad = facultad
        self._duracion_semestre = duracion_semestre
        self._creditos_totales = creditos_totales
        self._cupos_totales = cupos_totales

#Agregar en una lista las asignaturas
        self._asignaturas = []
#Agregación con Estudiante
        self._estudiantes = []

    @property
    def id_carrera(self):
        return self._id_carrera
    
    @property
    def nombre_carrera(self):
        return self._nombre_carrera

    @property
    def facultad(self):
        return self._facultad

    @property
    def duracion_semestre(self):
        return self._duracion_semestre

    @property
    def creditos_totales(self):
        return self._creditos_totales

    @property
    def cupos_totales(self):
        return self._cupos_totales

    @cupos_totales.setter
    def cupos_totales(self, nuevo_cupo):
        if nuevo_cupo >= 0:
            self._cupos_totales = nuevo_cupo
        else:
            raise ValueError ("Error, la cantidad no puede ser negativa")
        
    #Métodos
    def obtener_asignaturas(self):
        return self._asignaturas

    def ver_cupos_disponibles(self):
        cupos_usados = len(self._estudiantes)
        disponibles = self._cupos_totales - cupos_usados
        print(f"Carrera '{self._nombre_carrera}': {disponibles} cupos disponibles de {self._cupos_totales}.")
        return disponibles

    def ver_cupos_por_sede(self, sede: "Sede"):
        estudiantes_en_sede = [
            e for e in self._estudiantes if e.sede and e.sede.id_sede == sede.id_sede
        ]
        cupos_usados = len(estudiantes_en_sede)
        disponibles = self._cupos_totales - cupos_usados
        print(f"Cupos en sede '{sede.nombre_sede}' para '{self._nombre_carrera}': "
              f"{disponibles} disponibles.")
        return disponibles

    def agregar_asignatura(self, asignatura: "Asignatura"):
        if asignatura not in self._asignaturas:
            self._asignaturas.append(asignatura)
            print(f"Asignatura '{asignatura.nombre}' agregada a la carrera '{self._nombre_carrera}'.")
        else:
            print(f"La asignatura '{asignatura.nombre}' ya está en la carrera.")

    def listar_estudiantes(self):
        if not self._estudiantes:
            print(f"No hay estudiantes inscritos en '{self._nombre_carrera}'.")
            return []
        print(f"Estudiantes inscritos en '{self._nombre_carrera}':")
        for estudiante in self._estudiantes:
            print(f"  - {estudiante.nombre} | Estado: {estudiante.estado_academico}")
        return list(self._estudiantes)
    
    def _inscribir_estudiante(self, estudiante: "Estudiante"):
        if self.ver_cupos_disponibles() <= 0:
            raise ValueError(f"No hay cupos disponibles en '{self._nombre_carrera}'.")
        if estudiante not in self._estudiantes:
            self._estudiantes.append(estudiante)
            
    def __str__(self):
        return (
            f"[Carrera] {self._nombre_carrera} - Facultad: {self._facultad} - "
            f"Duración: {self._duracion_semestre} semestres - "
            f"Créditos: {self._creditos_totales} - Cupos: {self._cupos_totales}"
        )
