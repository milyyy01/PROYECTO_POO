from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.docente import Docente

class Asignatura:
    def __init__ (self, id_asignatura, nombre, contenido, creditos):
        self._id_asignatura = id_asignatura
        self._nombre = nombre
        self._contenido = contenido
        self._creditos = creditos

        #Atributos extras para los métodos
        self._docente = None
        self._cupos_maximos = 0
        self._archivos_material = []

#Aplicamos composición de evaluación y la creamos en una lista
        self._evaluaciones = []

    @property
    def id_asignatura(self):
        return self._id_asignatura
        
    @property
    def nombre(self):
        return self._nombre

    @property
    def creditos(self):
        return self._creditos

    @creditos.setter
    def creditos(self, cantidad):
        if cantidad > 0:
            self._creditos = cantidad
        else:
            raise ValueError("Los creditos no pueden ser negativos")
        
    @property
    def docente(self):
        return self._docente

    @property
    def cupos_maximos(self):
        return self._cupos_maximos

    @property
    def evaluaciones(self):
        return list(self._evaluaciones)
    
    #Metodos

    def subir_archivo(self, nombre_archivo):
        if nombre_archivo.strip(): #valida que no esté vacío el texto
            self._archivos_material.append(nombre_archivo)
            print (f"Archivo '{nombre_archivo}' subido correctamente")
        else:
            raise ValueError ("El nombre del archivo no puede estar vacío")

    def asignar_docente(self, docente: "Docente"):
        self._docente = docente
        docente._asignar_materia(self)
        print(f"El docente {docente.nombre} ha sido asignado a la asignatura {self._nombre}")

    def asignar_cupos(self, cantidad_cupos):
        if cantidad_cupos > 0:
            self._cupos_maximos = cantidad_cupos
            print(f"Se ha asignado {cantidad_cupos} cupos máximos para la asignatura {self._nombre}")
        else:
            raise ValueError("La cantidad de cupos debe ser mayor a cero.")

    def obtener_material(self):
        info = f"Contenido de '{self._nombre}': {self._contenido}"
        if self._archivos_material:
            archivos = ", ".join(self._archivos_material)
            info += f" | Archivos: {archivos}"
        return info

    #Metodo de composicion con evaluación
    def crear_evaluación(self, puntaje_minimo, puntaje_maximo, tipo, fecha_apertura, fecha_cierre):
        # Importación local para evitar importación circular
        from models.evaluacion import Evaluacion
        nueva_evaluacion = Evaluacion(
            puntaje_minimo=puntaje_minimo,
            puntaje_maximo=puntaje_maximo,
            tipo=tipo,
            fecha_apertura=fecha_apertura,
            fecha_cierre=fecha_cierre,
            asignatura=self,  # COMPOSICIÓN: se pasa self como dueño
            )
        self._evaluaciones.append(nueva_evaluacion)
        print(f"Evaluación '{tipo}' creada para la asignatura '{self._nombre}'.")
        return nueva_evaluacion

    def listar_archivos(self):
            return list(self._archivos_material)
    
    def __str__(self):
        docente_nombre = self._docente.nombre if self._docente else "Sin docente"
        return (
            f"[Asignatura] {self._nombre} - ID: {self._id_asignatura} - "
            f"Créditos: {self._creditos} - Cupos: {self._cupos_maximos} - "
            f"Docente: {docente_nombre} - Evaluaciones: {len(self._evaluaciones)}"
        )
