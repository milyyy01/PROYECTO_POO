from __future__ import annotations
from typing import TYPE_CHECKING
from models.usuario import Usuario

if TYPE_CHECKING:
    from models.asignatura import Asignatura
    from models.sede import Sede
    from models.carrera import Carrera

class Estudiante(Usuario):
    def __init__(self, id, nombre, correo, contrasena, telefono, fecha_matricula, sede: "Sede", carrera: "Carrera", estado_academico = "Activo"):
        super().__init__(id, nombre, correo, contrasena, rol="Estudiante", telefono=telefono)
        self.fecha_matricula = fecha_matricula
        self.__promedio = 0.0
        self.estado_academico = estado_academico
        self.sede = sede
        self.carrera = carrera
        self.__tareas_enviadas = []
        self.__materias = []
        self.__calificaciones = {}
        
    @property
    def promedio(self):
        return self.__promedio
    
    @property
    def tareas_enviadas(self):
        return list(self.__tareas_enviadas)

    @property
    def calificaciones(self):
        return {materia: list(notas) for materia, notas in self.__calificaciones.items()}
    
# Métodos abstractos implementados:

    def ver_materias(self):
        if not self.__materias:
            print("No estás inscrito en ninguna materia.")
            return
        else: 
            print("Materias inscritas:")
            for materia in self.__materias:
                print(f"-- {materia.nombre} ({materia.creditos} créditos)")
                
    def ver_calificaciones(self):
        if not self.__calificaciones:
            print("No tienes calificaciones registradas por el momento.")
            return {}
        else:
            print("Calificaciones:")
            for materia, notas in self.__calificaciones.items():
                for indice, registro in enumerate(notas, start=1):
                    nota = registro["nota"]
                    estado = "Aprobado" if nota >= 7.0 else "Reprobado"
                    print(f"  {materia} #{indice}: {nota:.2f} -> {estado}")
            print(f"  Promedio actual: {self.__promedio:.2f}")
            return self.calificaciones
                
# Métodos concretos de Estudiante:

    def enviar_tarea(self, tarea):
        if not tarea.strip():
            raise ValueError("El nombre de la tarea no puede estar vacío.")
        self.__tareas_enviadas.append(tarea)
        print("Tarea enviada exitosamente.")

    def anular_entrega(self, tarea):
        if tarea in self.__tareas_enviadas:
            self.__tareas_enviadas.remove(tarea)
            print("Entrega anulada exitosamente.")
        else:
            print("No se encontró la tarea en tus entregas.")

    def consultar_asignaturas(self, asignatura: "Asignatura"):
        print(f"Consultando '{asignatura.nombre}': {asignatura.creditos} créditos.")
        contenido = asignatura.obtener_material()
        if contenido:
            print(f"  Contenido: {contenido}")

    def descargar_material(self, asignatura: "Asignatura", archivo):
        materiales = asignatura.obtener_material()
        if archivo in (materiales or ""):
            print(f"'{archivo}' descargado exitosamente de '{asignatura.nombre}'.")
        else:
            print(f"Material '{archivo}' disponible. Descargando desde '{asignatura.nombre}'...")

    def agregar_comentarios(self, comentario):
        if not comentario.strip():
            raise ValueError("El comentario no puede estar vacío.")
        print(f"Comentario agregado por {self.nombre}: '{comentario}'")
    
# Métodos internos:

    def _agregar_materia(self, asignatura: "Asignatura"):
        if asignatura not in self.__materias:
            self.__materias.append(asignatura)
        
    def _registrar_calificacion(self, materia, nota, comentario=None):
        if materia not in self.__calificaciones:
            self.__calificaciones[materia] = []
        self.__calificaciones[materia].append({
            "nota": float(nota),
            "comentario": comentario or "",
        })
        self.__actualizar_promedio()
        
    def __actualizar_promedio(self):
        if self.__calificaciones:
            notas = [
                registro["nota"]
                for registros_materia in self.__calificaciones.values()
                for registro in registros_materia
            ]
            self.__promedio = sum(notas) / len(notas) if notas else 0.0
           
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            "telefono": self.telefono,
            "fecha_matricula": str(self.fecha_matricula),
            "promedio": self.promedio,
            "estado_academico": self.estado_academico,
            "sede": self.sede.nombre_sede if self.sede else None,
            "carrera": self.carrera.nombre_carrera if self.carrera else None,
            "calificaciones": self.calificaciones
    }

    def __str__(self):
        sede_nombre = self.sede.nombre_sede if self.sede else "Sin sede"
        carrera_nombre = self.carrera.nombre_carrera if self.carrera else "Sin carrera"
        return (f"[Estudiante] {self.nombre} - Carrera: {carrera_nombre} - "
                f"Sede: {sede_nombre} - Promedio: {self.__promedio:.2f} - Estado: {self.estado_academico}")

