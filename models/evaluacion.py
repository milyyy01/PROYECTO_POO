from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.asignatura import Asignatura
    from models.estudiante import Estudiante

class Evaluacion:
    def __init__ (self, puntaje_minimo, puntaje_maximo, tipo, fecha_apertura, fecha_cierre, asignatura: "Asignatura"):
        if asignatura is None:
            raise ValueError("La evaluación no puede existir sin una asignatura enlazada.")
        self._asignatura = asignatura
        self._puntaje_minimo = puntaje_minimo
        self._puntaje_maximo = puntaje_maximo
        self._tipo = tipo
        self._fecha_apertura = fecha_apertura
        self._fecha_cierre = fecha_cierre
        
        # Estado interno: Se guardan resultados por estudiante {nombre: nota}
        self.__resultados = {}
        self.__intentos = {}



    @property
    def tipo(self):
        return self._tipo

    @property
    def puntaje_minimo(self):
        return self._puntaje_minimo

    @property
    def puntaje_maximo(self):
        return self._puntaje_maximo

    @puntaje_maximo.setter
    def puntaje_maximo(self, valor):
        if valor >= self._puntaje_minimo:
            self._puntaje_maximo = valor
        else:
            raise ValueError ("El puntaje máximo no puede ser menor al puntaje mínimo para aprobar")

    @property
    def asignatura(self):
        return self._asignatura

    @property
    def fecha_apertura(self):
        return self._fecha_apertura
 
    @property
    def fecha_cierre(self):
        return self._fecha_cierre
    
    #Metodos
    def aprobar(self, estudiante: "Estudiante", nota):
        if nota < 0 or nota > self._puntaje_maximo:
            raise ValueError(f"La nota debe estar entre 0 y {self._puntaje_maximo}.")
        self.__resultados[estudiante.nombre] = nota
        self.__intentos[estudiante.nombre] = self.__intentos.get(estudiante.nombre, 0) + 1
        if nota >= self._puntaje_minimo:
            print(f" {estudiante.nombre} Aprobó la evaluación '{self._tipo}' "
                  f"de '{self._asignatura.nombre}' con {nota:.2f} puntos.")
            
            # Notifica al estudiante para que registre la calificación
            estudiante._registrar_calificacion(f"{self._asignatura.nombre} - {self._tipo}", nota)
            return True
        else:
            print(f" {estudiante.nombre} No aprobó la evaluación '{self._tipo}' "
                  f"de '{self._asignatura.nombre}' con {nota:.2f} puntos "
                  f"(mínimo: {self._puntaje_minimo}).")
            return False

    def reprobar(self, estudiante: "Estudiante"):
        self.__resultados[estudiante.nombre] = 0.0
        self.__intentos[estudiante.nombre] = self.__intentos.get(estudiante.nombre, 0) + 1
        print(f" {estudiante.nombre} ha sido marcado como reprobado en "
              f"'{self._tipo}' de '{self._asignatura.nombre}'.")
        estudiante._registrar_calificacion(f"{self._asignatura.nombre} - {self._tipo}", 0.0)
        return True

    def mostrar_nota(self, estudiante: "Estudiante"):
        nota = self.__resultados.get(estudiante.nombre)
        if nota is None:
            print(f"{estudiante.nombre} aún no tiene nota en '{self._tipo}'.")
        else:
            estado = "Aprobado" if nota >= self._puntaje_minimo else "Reprobado"
            intentos = self.__intentos.get(estudiante.nombre, 0)
            print(f"Nota de {estudiante.nombre} en '{self._tipo}' "
                  f"({self._asignatura.nombre}): {nota:.2f} -> {estado} "
                  f"(Intentos: {intentos})")

    def reintentar_evaluacion(self, estudiante: "Estudiante", nueva_nota):
        intentos_actuales = self.__intentos.get(estudiante.nombre, 0)
        print(f"Intento #{intentos_actuales + 1} de {estudiante.nombre} "
              f"en '{self._tipo}' de '{self._asignatura.nombre}'.")
        return self.aprobar(estudiante, nueva_nota)
    
    def obtener_resultados(self):
        return dict(self.__resultados)
    
    def __str__(self):
        return (
            f"[Evaluacion] Tipo: {self._tipo} - "
            f"Asignatura: {self._asignatura.nombre} - "
            f"Puntaje mínimo: {self._puntaje_minimo} - "
            f"Apertura: {self._fecha_apertura} - "
            f"Cierre: {self._fecha_cierre}"
        )
