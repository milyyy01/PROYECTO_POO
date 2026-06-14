from __future__ import annotations
from typing import TYPE_CHECKING
from models.usuario import Usuario

if TYPE_CHECKING:
    from models.asignatura import Asignatura
    from models.paralelo import Paralelo
    from models.estudiante import Estudiante
    from models.sede import Sede

class Docente(Usuario):
    def __init__(self, id, nombre, correo, contrasena, telefono, titulo, especialidad, nivel):
        super().__init__(id, nombre, correo, contrasena, rol="Docente", telefono=telefono)
        self.titulo = titulo
        self.especialidad = especialidad
        self.nivel = nivel
        self._horas_asignadas = 0
        self.__paralelos = []
        self.__materias_asignadas = []
        self.__calificaciones_registradas = {}
        self._sede = None
        
    @property
    def horas_asignadas(self):
        return self._horas_asignadas
    
    @property
    def sede(self):
        return self._sede
    
    @property
    def materias_asignadas(self):
        return list(self.__materias_asignadas)
    
    @property
    def paralelos(self):
        return list(self.__paralelos)
    
# Métodos abstractos implementados:

    def ver_materias(self):
        if not self.__materias_asignadas:
            print("No tienes materias asignadas por el momento.")
            return
        else: 
            print("Materias asignadas:")
            for materia in self.__materias_asignadas:
                print(f"-- {materia.nombre} ({materia.creditos} créditos)")
    
    def ver_calificaciones(self):
        if not self.__calificaciones_registradas:
            print("No has registrado calificaciones por el momento.")
            return
        else:
            print("Calificaciones registradas:")
            for estudiante, materias in self.__calificaciones_registradas.items():
                for materia, nota in materias.items():
                    estado = "Aprobado" if nota >= 7.0 else "Reprobado"
                    print(f" {estudiante} - {materia}: {nota:.2f} -> {estado}")
                    
# Métodos concretos de Docente:

    def impartir_clase(self, asignatura: "Asignatura", paralelo):
        print(f"{self.nombre} impartiendo clase de {asignatura.nombre} en el paralelo {paralelo.codigo}.")
    
    def asignar_horario(self, dia, hora_entrada, hora_salida):
        print(f"Horario asignado para {self.nombre}: {dia} de {hora_entrada} a {hora_salida}.")
        
    def calificar(self, estudiante: "Estudiante", asignatura: "Asignatura", nota, comentario = None):
        if not (0.0 <= nota <= 10.0):
            raise ValueError("La nota debe estar entre 0.0 y 10.0.")
        if estudiante.nombre not in self.__calificaciones_registradas:
            self.__calificaciones_registradas[estudiante.nombre] = {}
        self.__calificaciones_registradas[estudiante.nombre][asignatura.nombre] = nota
        
        estudiante._registrar_calificacion(asignatura.nombre, nota)
        mensaje = f"Calificación registrada para {estudiante.nombre} en {asignatura.nombre}: {nota:.2f}"
        if comentario:
            mensaje += f". Comentario: {comentario}"
        print(mensaje)
        
    def marcar_asistencia(self, estudiante, presente):
        estado = "Presente" if presente else "Ausente"
        print(f"Asistencia de {estudiante.nombre}: {estado}")
        
    def subir_material(self, asignatura: "Asignatura", archivo):
        asignatura.subir_archivo(archivo)
        
    def ver_paralelos(self):
        if not self.__paralelos:
            print(f"{self.nombre} no tiene paralelos asignados por el momento.")
            return
        else:
            print(f"Paralelos asignados a {self.nombre}:")
            for paralelo in self.__paralelos:
                print(f"- {paralelo.codigo}")
                
# Métodos internos:

    def _establecer_sede(self, sede: "Sede"):
        self._sede = sede

    def _asignar_materia(self, asignatura: "Asignatura"):
        if asignatura not in self.__materias_asignadas:
            self.__materias_asignadas.append(asignatura)

    def _asignar_paralelo(self, paralelo: "Paralelo"):
        if paralelo not in self.__paralelos:
            self.__paralelos.append(paralelo)
            
    def _agregar_horas(self, horas):
        if horas <= 0:
            raise ValueError("Las horas deben ser mayor a cero.")
        self._horas_asignadas += horas

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            "telefono": self.telefono,
            "titulo": self.titulo,
            "especialidad": self.especialidad,
            "nivel": self.nivel,
            "horas_asignadas": self.horas_asignadas,
            "sede": self.sede.nombre_sede if self.sede else None
    }
            
    def __str__(self):
        sede_nombre = self._sede.nombre_sede if self._sede else "Sin sede"
        return (f"[Docente] {self.nombre} - Título: {self.titulo} - "
                    f"Especialidad: {self.especialidad} - Horas Asignadas: {self._horas_asignadas} - Sede: {sede_nombre}")
def to_dict(self):
    return {
        "id": self.id,
        "nombre": self.nombre,
        "correo": self.correo,
        "telefono": self.telefono,
        "titulo": self.titulo,
        "especialidad": self.especialidad,
        "nivel": self.nivel,
        "horas_asignadas": self.horas_asignadas,
        "sede": self.sede.nombre_sede if self.sede else None
    }