from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.estudiante import Estudiante
    from models.docente import Docente
    from models.horario import Horario
    from models.modalidad import Modalidad
    from models.asignatura import Asignatura

class Paralelo:
    def __init__(self, codigo, capacidad, docente: "Docente", horario: "Horario", modalidad: "Modalidad", asignatura: "Asignatura" = None):
        self._codigo = codigo
        self.capacidad = capacidad
        self._cupo_disponible = capacidad
        self._docente = docente
        self._horario = horario
        self._modalidad = modalidad
        self._asignatura = asignatura
        self.__lista_estudiantes = []
        self.__estado = "Activo"

# Sincronización automática bidireccional con el docente
        if self._docente:
            self._docente._asignar_paralelo(self)
            
    # Getter

    @property
    def codigo(self):
        return self._codigo
    
    @property
    def estado(self):
        return self.__estado

    @property
    def estudiantes(self):
        return list(self.__lista_estudiantes)

    @property
    def cupo_disponible(self):
        return self._cupo_disponible
    
    @property
    def docente(self):
        return self._docente
 
    @property
    def horario(self):
        return self._horario
 
    @property
    def modalidad(self):
        return self._modalidad

    @property
    def asignatura(self):
        return self._asignatura
    

    # Métodos
    def agregar_estudiante(self, estudiante):
        if self.__estado != "Activo":
            print(f"El paralelo '{self._codigo}' no está activo.")
            return
        if self._cupo_disponible <= 0:
            print(f"No hay cupos disponibles en el paralelo '{self._codigo}'.")
            return
        if estudiante in self.__lista_estudiantes:
            print(f"{estudiante.nombre} ya está en el paralelo '{self._codigo}'.")
            return
        self.__lista_estudiantes.append(estudiante)
        self._cupo_disponible -= 1
        print(f"Estudiante '{estudiante.nombre}' agregado al paralelo '{self._codigo}'. "
              f"Cupos restantes: {self._cupo_disponible}")
        
    def asignar_horario(self, horario: "Horario"):
        self._horario = horario
        print(f"Horario actualizado en el paralelo '{self._codigo}': {horario}")

    def retirar_estudiante(self, estudiante: "Estudiante"):
        if estudiante in self.__lista_estudiantes:
            self.__lista_estudiantes.remove(estudiante)
            self._cupo_disponible += 1
            print(f"Estudiante '{estudiante.nombre}' retirado del paralelo '{self._codigo}'. "
                  f"Cupos disponibles: {self._cupo_disponible}")
        else:
            print(f"'{estudiante.nombre}' no pertenece al paralelo '{self._codigo}'.")

    def activar_paralelo(self):
        self.__estado = "Activo"
        print("Paralelo activado.")

    def desactivar_paralelo(self):
        self.__estado = "Inactivo"
        print("Paralelo desactivado.")

    def mostrar_informacion(self):
        print("===== INFORMACIÓN DEL PARALELO =====")
        print(f"Código: {self._codigo}")
        print(f"Docente: {self.docente.nombre}")
        print(f"Asignatura: {self.asignatura.nombre if self.asignatura else 'Sin asignatura'}")
        print(f"Modalidad: {self.modalidad.tipo}")
        print(f"Horario: {self.horario.dia} | "
              f"{self.horario.hora_inicio} - {self.horario.hora_fin}")
        print(f"Estado: {self.__estado}")
        print(f"Cantidad de estudiantes: {len(self.__lista_estudiantes)}")

    def listar_estudiantes(self):
        if not self.__lista_estudiantes:
            print("No hay estudiantes registrados.")
            return
        else:
            print("===== ESTUDIANTES =====")
            for estudiante in self.__lista_estudiantes:
                print(f"- {estudiante.nombre}")

    def __str__(self):
        return (f"[Paralelo] Código: {self._codigo} | "
                f"Docente: {self.docente.nombre} | "
                f"Asignatura: {self.asignatura.nombre if self.asignatura else 'Sin asignatura'} | "
                f"Estado: {self.__estado}")
