from __future__ import annotations
from models.estudiante import Estudiante
from models.docente import Docente
from models.paralelo import Paralelo
from models.asignatura import Asignatura
from models.sede import Sede
from models.administrador import Administrador
from models.Reporte import Reporte, ReporteAcademicoBuilder, DirectorReportes
from models.horario import Horario
from models.modalidad import Modalidad
from models.carrera import Carrera

class SistemaNivelacion:
    def __init__(self, nombre_institucion, nivel_academico):
        # ATRIBUTOS PÚBLICOS 
        self.nombre_institucion = nombre_institucion
        self.nivel_academico = nivel_academico

        # ATRIBUTOS PRIVADOS
        self.__estudiantes_registrados = 0
        self.__profesores_registrados = 0

        # ENLACES / RELACIONES (Listas para la multiplicidad 1..*)
        self._administradores = []
        self._paralelos = []
        self._asignaturas = []
        self._sedes = []
        self._reportes = []
        self._director_reportes = DirectorReportes()
        
    # Propiedades 
    
    @property
    def estudiantes_registrados(self):
        return self.__estudiantes_registrados
 
    @property
    def profesores_registrados(self):
        return self.__profesores_registrados

    # Métodos del diagrama
    
    def asignar_estudiante_a_paralelos(self, estudiante: Estudiante, paralelo: Paralelo):
        # Ejemplo de cómo el sistema manipula internamente su atributo privado:
        paralelo.agregar_estudiante(estudiante)
        self.__estudiantes_registrados += 1
        print(f"Estudiante '{estudiante.nombre}' asignado al paralelo '{paralelo.codigo}' "
              f"en '{self.nombre_institucion}'.")

    def asignar_docentes(self, docente: Docente, asignatura: Asignatura):
        asignatura.asignar_docente(docente)
        self.__profesores_registrados += 1
        print(f"Docente '{docente.nombre}' asignado a '{asignatura.nombre}' en el sistema.")

    def generar_horarios(self, id_horario, dia, hora_inicio, hora_fin, aula):
        from models.horario import Horario
        horario = Horario(
            id_horario=id_horario,
            dia=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            aula=aula,
        )
        if not horario.validar_horas():
            raise ValueError("No se puede crear un horario con horas inválidas.")
        print(f"Horario '{id_horario}' generado: {dia} {hora_inicio}-{hora_fin} - Aula: {aula}")
        return horario

    def ver_docentes_disponibles(self, sede = None):
        docentes = []
        for paralelo in self._paralelos:
            docente = paralelo.docente
            if sede is None or (docente.sede and docente.sede.id_sede == sede.id_sede):
                if docente not in docentes:
                    docentes.append(docente)
        if not docentes:
            print("No hay docentes disponibles registrados.")
        else:
            print(f"Docentes disponibles en '{self.nombre_institucion}':")
            for d in docentes:
                print(f"  - {d.nombre} | Especialidad: {d.especialidad} | "
                      f"Horas: {d.horas_asignadas}")
        return docentes

    def ver_carrera_disponible(self, sede = None):
        carreras = []
        for s in self._sedes:
            if sede is None or s.id_sede == sede.id_sede:
                for carrera in s.listar_carreras():
                    if carrera not in carreras:
                        carreras.append(carrera)
        if not carreras:
            print("No hay carreras disponibles.")
        else:
            print(f"Carreras disponibles en '{self.nombre_institucion}':")
            for c in carreras:
                print(f"  - {c.nombre_carrera} | Cupos: {c.cupos_totales}")
        return carreras
    
    # MÉTODOS DE REGISTRO (registro de entidades en el sistema):
 
    def registrar_sede(self, sede: Sede):
        if sede not in self._sedes:
            self._sedes.append(sede)
            print(f"Sede '{sede.nombre_sede}' registrada en '{self.nombre_institucion}'.")
 
    def registrar_paralelo(self, paralelo: Paralelo):
        if paralelo not in self._paralelos:
            self._paralelos.append(paralelo)
            print(f"Paralelo '{paralelo.codigo}' registrado en el sistema.")
 
    def registrar_asignatura(self, asignatura: Asignatura):
        if asignatura not in self._asignaturas:
            self._asignaturas.append(asignatura)
            print(f"Asignatura '{asignatura.nombre}' registrada en el sistema.")
 
    def registrar_administrador(self, administrador: Administrador):
        if administrador not in self._administradores:
            self._administradores.append(administrador)
            print(f"Administrador '{administrador.nombre}' registrado en el sistema.")
 
    # GENERACIÓN DE REPORTES: 
 
    def generar_reporte(self, solicitante_nombre, datos):
        """
        Genera un reporte usando el patrón Builder:
        DirectorReportes + ReporteAcademicoBuilder (definidos en Reporte.py).
        'datos' debe ser una lista de líneas/registros para el cuerpo del reporte.
        """
        self._director_reportes.builder = ReporteAcademicoBuilder()
        reporte = self._director_reportes.generar_reporte_calificaciones(
            estudiante_nombre=solicitante_nombre,
            notas=datos
        )
        self._reportes.append(reporte)
        print(f"Reporte generado por '{self.nombre_institucion}' para '{solicitante_nombre}'.")
        return reporte
 
    def __str__(self):
        return (
            f"[SistemaNivelacion] {self.nombre_institucion} | "
            f"Nivel: {self.nivel_academico} | "
            f"Estudiantes: {self.__estudiantes_registrados} | "
            f"Docentes: {self.__profesores_registrados} | "
            f"Paralelos: {len(self._paralelos)} | "
            f"Sedes: {len(self._sedes)}"
        )