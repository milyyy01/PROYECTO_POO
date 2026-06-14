"""
gestor_nivelacion.py
Sistema funcional SIGEN - Gestión de Nivelación
Principios SOLID aplicados + Patrón Builder
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

# IMPORTACIONES DEL DOMINIO

from models.usuario import Usuario
from models.estudiante import Estudiante
from models.docente import Docente
from models.administrador import Administrador
from models.asignatura import Asignatura
from models.carrera import Carrera
from models.sede import Sede
from models.paralelo import Paralelo
from models.horario import Horario
from models.modalidad import Modalidad
from models.periodo_academico import PeriodoAcademico
from models.oferta import Oferta
from models.Reporte import (
    Reporte,
    IReporteBuilder,
    ReporteAcademicoBuilder,
    DirectorReportes,
)


# I — INTERFACES ESPECÍFICAS (Interface Segregation)
# Cada interfaz cubre una única área de responsabilidad.

class IGestorEstudiantes(ABC):
    """Contrato para operaciones sobre estudiantes."""

    @abstractmethod
    def registrar_estudiante(self, estudiante: Estudiante) -> None: ...

    @abstractmethod
    def buscar_estudiante(self, nombre: str) -> Optional[Estudiante]: ...

    @abstractmethod
    def listar_estudiantes(self) -> List[Estudiante]: ...


class IGestorDocentes(ABC):
    """Contrato para operaciones sobre docentes."""

    @abstractmethod
    def registrar_docente(self, docente: Docente) -> None: ...

    @abstractmethod
    def buscar_docente(self, nombre: str) -> Optional[Docente]: ...

    @abstractmethod
    def listar_docentes(self) -> List[Docente]: ...


class IGestorAcademico(ABC):
    """Contrato para operaciones académicas (paralelos, asignaturas)."""

    @abstractmethod
    def registrar_asignatura(self, asignatura: Asignatura) -> None: ...

    @abstractmethod
    def registrar_paralelo(self, paralelo: Paralelo) -> None: ...

    @abstractmethod
    def asignar_estudiante_a_paralelo(
        self, estudiante: Estudiante, paralelo: Paralelo
    ) -> None: ...


class IGestorReportes(ABC):
    """Contrato para generación de reportes."""

    @abstractmethod
    def generar_reporte_calificaciones(self, estudiante: Estudiante) -> Reporte: ...

    @abstractmethod
    def generar_reporte_docente(self, docente: Docente) -> Reporte: ...


# O + L — NUEVOS BUILDERS (Open/Closed + Liskov)
# Se extiende el sistema de reportes SIN modificar IReporteBuilder ni
# ReporteAcademicoBuilder. Cada builder concreto es sustituible.
class ReporteDocenteBuilder(IReporteBuilder):
    """
    Builder concreto para reportes de docentes.
    Abierto para uso sin tocar el builder académico existente.
    """

    def __init__(self):
        self._reporte: Optional[Reporte] = None

    def reset(self, tipo_reporte: str) -> None:
        self._reporte = Reporte(tipo_reporte)

    def construir_encabezado(self, titulo: str, autor: str) -> None:
        self._reporte.encabezado = (
            f"UNIVERSIDAD LAICA ELOY ALFARO DE MANABÍ (ULEAM)\n"
            f"SISTEMA DE GESTIÓN DE NIVELACIÓN (SIGEN)\n"
            f"REPORTE DE DOCENTE\n"
            f"TÍTULO   : {titulo}\n"
            f"DOCENTE  : {autor}\n"
            f"{'-' * 40}"
        )

    def construir_cuerpo(self, datos: list) -> None:
        cuerpo_str = "\n".join([f"  >> {dato}" for dato in datos])
        self._reporte.cuerpo = f"INFORMACIÓN DEL DOCENTE:\n{cuerpo_str}\n"

    def construir_pie_pagina(self) -> None:
        self._reporte.pie_pagina = (
            f"{'-' * 40}\n"
            f"Reporte generado automáticamente por SIGEN.\n"
            f"Uso interno del departamento académico."
        )

    def obtener_resultado(self) -> Reporte:
        producto = self._reporte
        self._reporte = None
        return producto


class ReporteSedeBuilder(IReporteBuilder):
    """Builder concreto para reportes de sede."""

    def __init__(self):
        self._reporte: Optional[Reporte] = None

    def reset(self, tipo_reporte: str) -> None:
        self._reporte = Reporte(tipo_reporte)

    def construir_encabezado(self, titulo: str, autor: str) -> None:
        self._reporte.encabezado = (
            f"UNIVERSIDAD LAICA ELOY ALFARO DE MANABÍ (ULEAM)\n"
            f"SISTEMA DE GESTIÓN DE NIVELACIÓN (SIGEN)\n"
            f"REPORTE DE SEDE\n"
            f"TÍTULO : {titulo}\n"
            f"SEDE   : {autor}\n"
            f"{'-' * 40}"
        )

    def construir_cuerpo(self, datos: list) -> None:
        cuerpo_str = "\n".join([f"  >> {dato}" for dato in datos])
        self._reporte.cuerpo = f"DETALLE DE SEDE:\n{cuerpo_str}\n"

    def construir_pie_pagina(self) -> None:
        self._reporte.pie_pagina = (
            f"{'-' * 40}\n"
            f"Reporte de sede generado por SIGEN."
        )

    def obtener_resultado(self) -> Reporte:
        producto = self._reporte
        self._reporte = None
        return producto


# S — REPOSITORIOS (Single Responsibility)
# Cada repositorio gestiona solo una entidad del dominio.

class RepositorioEstudiantes:
    """Responsabilidad única: almacenar y recuperar estudiantes."""

    def __init__(self):
        self._estudiantes: List[Estudiante] = []

    def agregar(self, estudiante: Estudiante) -> None:
        if not self._existe(estudiante.id):
            self._estudiantes.append(estudiante)

    def buscar_por_nombre(self, nombre: str) -> Optional[Estudiante]:
        nombre_lower = nombre.lower()
        for e in self._estudiantes:
            if nombre_lower in e.nombre.lower():
                return e
        return None

    def buscar_por_id(self, id_estudiante) -> Optional[Estudiante]:
        for e in self._estudiantes:
            if e.id == id_estudiante:
                return e
        return None

    def todos(self) -> List[Estudiante]:
        return list(self._estudiantes)

    def _existe(self, id_estudiante) -> bool:
        return any(e.id == id_estudiante for e in self._estudiantes)


class RepositorioDocentes:
    """Responsabilidad única: almacenar y recuperar docentes."""

    def __init__(self):
        self._docentes: List[Docente] = []

    def agregar(self, docente: Docente) -> None:
        if not self._existe(docente.id):
            self._docentes.append(docente)

    def buscar_por_nombre(self, nombre: str) -> Optional[Docente]:
        nombre_lower = nombre.lower()
        for d in self._docentes:
            if nombre_lower in d.nombre.lower():
                return d
        return None

    def todos(self) -> List[Docente]:
        return list(self._docentes)

    def _existe(self, id_docente) -> bool:
        return any(d.id == id_docente for d in self._docentes)


class RepositorioAsignaturas:
    """Responsabilidad única: almacenar y recuperar asignaturas."""

    def __init__(self):
        self._asignaturas: List[Asignatura] = []

    def agregar(self, asignatura: Asignatura) -> None:
        if not self._existe(asignatura.id_asignatura):
            self._asignaturas.append(asignatura)

    def buscar_por_nombre(self, nombre: str) -> Optional[Asignatura]:
        nombre_lower = nombre.lower()
        for a in self._asignaturas:
            if nombre_lower in a.nombre.lower():
                return a
        return None

    def todas(self) -> List[Asignatura]:
        return list(self._asignaturas)

    def _existe(self, id_asignatura) -> bool:
        return any(a.id_asignatura == id_asignatura for a in self._asignaturas)


class RepositorioParalelos:
    """Responsabilidad única: almacenar y recuperar paralelos."""

    def __init__(self):
        self._paralelos: List[Paralelo] = []

    def agregar(self, paralelo: Paralelo) -> None:
        if paralelo not in self._paralelos:
            self._paralelos.append(paralelo)

    def buscar_por_codigo(self, codigo: str) -> Optional[Paralelo]:
        for p in self._paralelos:
            if p.codigo == codigo:
                return p
        return None

    def todos(self) -> List[Paralelo]:
        return list(self._paralelos)


# S — SERVICIOS ESPECIALIZADOS (Single Responsibility)
# Cada servicio orquesta la lógica de un área específica.

class ServicioMatricula:
    """
    Responsabilidad única: gestionar la matriculación de estudiantes
    en paralelos y carreras.
    """

    def __init__(
        self,
        repo_estudiantes: RepositorioEstudiantes,
        repo_paralelos: RepositorioParalelos,
    ):
        self._repo_est = repo_estudiantes
        self._repo_par = repo_paralelos

    def matricular_en_paralelo(
        self, estudiante: Estudiante, paralelo: Paralelo
    ) -> bool:
        if paralelo.cupo_disponible <= 0:
            print(f"[Matrícula] Sin cupos en paralelo '{paralelo.codigo}'.")
            return False
        paralelo.agregar_estudiante(estudiante)
        print(
            f"[Matrícula] '{estudiante.nombre}' matriculado en '{paralelo.codigo}'."
        )
        return True

    def matricular_en_carrera(
        self, estudiante: Estudiante, oferta: Oferta, puntaje: float
    ) -> str:
        return oferta.aprobar_inscripcion(estudiante, puntaje)


class ServicioCalificaciones:
    """
    Responsabilidad única: gestionar el registro de calificaciones
    y la consulta del rendimiento académico.
    """

    def calificar_estudiante(
        self,
        docente: Docente,
        estudiante: Estudiante,
        asignatura: Asignatura,
        nota: float,
        comentario: str = None,
    ) -> None:
        docente.calificar(estudiante, asignatura, nota, comentario)

    def ver_calificaciones(self, estudiante: Estudiante) -> None:
        estudiante.ver_calificaciones()

    def obtener_promedio(self, estudiante: Estudiante) -> float:
        return estudiante.promedio


class ServicioAsignacion:
    """
    Responsabilidad única: gestionar asignaciones de docentes,
    sedes, horarios y cargas horarias.
    """

    def __init__(self, admin: Administrador):
        self._admin = admin

    def asignar_docente_a_asignatura(
        self, docente: Docente, asignatura: Asignatura
    ) -> None:
        asignatura.asignar_docente(docente)

    def asignar_sede_a_docente(self, docente: Docente, sede: Sede) -> None:
        self._admin.asignar_sede_a_docente(docente, sede)

    def asignar_carga_horaria(self, docente: Docente, horas: int) -> None:
        self._admin.asignar_carga_horaria(docente, horas)

    def asignar_horario_a_paralelo(
        self, paralelo: Paralelo, horario: Horario
    ) -> None:
        paralelo.asignar_horario(horario)


# D — GESTOR DE REPORTES (Dependency Inversion)
# Depende de IReporteBuilder, no de builders concretos.

class GestorReportes(IGestorReportes):
    """
    Responsabilidad única: coordinar la construcción de reportes.
    Depende de la abstracción IReporteBuilder (D de SOLID).
    """

    def __init__(self):
        self._director = DirectorReportes()
        self._reportes_generados: List[Reporte] = []

    def _construir(
        self,
        builder: IReporteBuilder,
        tipo: str,
        titulo: str,
        autor: str,
        datos: list,
    ) -> Reporte:
        """Método interno reutilizable para cualquier builder."""
        self._director.builder = builder
        builder.reset(tipo)
        builder.construir_encabezado(titulo, autor)
        builder.construir_cuerpo(datos)
        builder.construir_pie_pagina()
        reporte = builder.obtener_resultado()
        self._reportes_generados.append(reporte)
        return reporte

    def generar_reporte_calificaciones(self, estudiante: Estudiante) -> Reporte:
        """Usa el builder académico para calificaciones del estudiante."""
        datos = []
        for materia, nota in estudiante.ver_calificaciones().items():
            estado = "Aprobado" if nota >= 7.0 else "Reprobado"
            datos.append(f"{materia}: {nota:.2f} -> {estado}")
        if not datos:
            datos = ["Sin calificaciones registradas."]
        datos.append(f"Promedio general: {estudiante.promedio:.2f}")

        return self._construir(
            builder=ReporteAcademicoBuilder(),
            tipo="Académico - Calificaciones",
            titulo="Historial de Calificaciones",
            autor=estudiante.nombre,
            datos=datos,
        )

    def generar_reporte_docente(self, docente: Docente) -> Reporte:
        """Usa el builder de docente."""
        datos = [
            f"Título       : {docente.titulo}",
            f"Especialidad : {docente.especialidad}",
            f"Nivel        : {docente.nivel}",
            f"Horas asign. : {docente.horas_asignadas}",
            f"Sede         : {docente.sede.nombre_sede if docente.sede else 'Sin sede'}",
            f"Materias     : {len(docente.materias_asignadas)}",
            f"Paralelos    : {len(docente.paralelos)}",
        ]
        return self._construir(
            builder=ReporteDocenteBuilder(),
            tipo="Docente - Perfil",
            titulo="Perfil del Docente",
            autor=docente.nombre,
            datos=datos,
        )

    def generar_reporte_sede(self, sede: Sede) -> Reporte:
        """Usa el builder de sede."""
        datos = [
            f"Ciudad       : {sede.ciudad}",
            f"Dirección    : {sede.direccion}",
            f"Capacidad    : {sede.capacidad_total}",
            f"Paralelos    : {len(sede._paralelos)}",
            f"Carreras     : {len(sede._carreras)}",
        ]
        return self._construir(
            builder=ReporteSedeBuilder(),
            tipo="Sede - Resumen",
            titulo="Resumen de Sede",
            autor=sede.nombre_sede,
            datos=datos,
        )

    def listar_reportes(self) -> None:
        if not self._reportes_generados:
            print("[Reportes] No hay reportes generados.")
            return
        print(f"\n{'=' * 40}")
        print(f"  REPORTES GENERADOS ({len(self._reportes_generados)})")
        print(f"{'=' * 40}")
        for i, r in enumerate(self._reportes_generados, 1):
            print(f"  {i}. {r}")


# FACHADA PRINCIPAL — GestorNivelacion
# Implementa las interfaces IGestorEstudiantes, IGestorDocentes,
# IGestorAcademico, IGestorReportes.
# Depende de abstracciones (D de SOLID).

class GestorNivelacion(IGestorEstudiantes, IGestorDocentes, IGestorAcademico, IGestorReportes):
    """
    Punto de entrada principal del sistema SIGEN.

    Principios aplicados:
      S - Delega responsabilidades a servicios y repositorios especializados.
      O - Nuevos builders/servicios se añaden sin modificar esta clase.
      L - Implementa correctamente todas las interfaces que hereda.
      I - Las interfaces que implementa son pequeñas y específicas.
      D - Depende de IGestorReportes, no de GestorReportes directamente.
    """

    def __init__(self, nombre_institucion: str, admin: Administrador):
        self.nombre_institucion = nombre_institucion
        self._admin = admin

        # Repositorios (S: cada uno con su responsabilidad)
        self._repo_estudiantes = RepositorioEstudiantes()
        self._repo_docentes = RepositorioDocentes()
        self._repo_asignaturas = RepositorioAsignaturas()
        self._repo_paralelos = RepositorioParalelos()

        # Servicios especializados (D: inyectados, no instanciados internamente)
        self._svc_matricula = ServicioMatricula(
            self._repo_estudiantes, self._repo_paralelos
        )
        self._svc_calificaciones = ServicioCalificaciones()
        self._svc_asignacion = ServicioAsignacion(admin)
        self._gestor_reportes: IGestorReportes = GestorReportes()

        # Sedes y periodos
        self._sedes: List[Sede] = []
        self._periodos: List[PeriodoAcademico] = []

        print(f"\n{'=' * 50}")
        print(f"  SIGEN — {self.nombre_institucion}")
        print(f"  Administrador: {admin.nombre}")
        print(f"{'=' * 50}\n")

    # ── IGestorEstudiantes ────────────────────────────────────────────────────

    def registrar_estudiante(self, estudiante: Estudiante) -> None:
        self._repo_estudiantes.agregar(estudiante)
        print(f"[Sistema] Estudiante '{estudiante.nombre}' registrado.")

    def buscar_estudiante(self, nombre: str) -> Optional[Estudiante]:
        resultado = self._repo_estudiantes.buscar_por_nombre(nombre)
        if resultado:
            print(f"[Sistema] Encontrado: {resultado}")
        else:
            print(f"[Sistema] No se encontró estudiante con nombre '{nombre}'.")
        return resultado

    def listar_estudiantes(self) -> List[Estudiante]:
        estudiantes = self._repo_estudiantes.todos()
        print(f"\n[Estudiantes registrados — {len(estudiantes)}]")
        for e in estudiantes:
            print(f"  • {e}")
        return estudiantes

    # ── IGestorDocentes ───────────────────────────────────────────────────────

    def registrar_docente(self, docente: Docente) -> None:
        self._repo_docentes.agregar(docente)
        self._admin.validar_registro_docente(docente.nombre)
        print(f"[Sistema] Docente '{docente.nombre}' registrado.")

    def buscar_docente(self, nombre: str) -> Optional[Docente]:
        resultado = self._repo_docentes.buscar_por_nombre(nombre)
        if resultado:
            print(f"[Sistema] Encontrado: {resultado}")
        else:
            print(f"[Sistema] No se encontró docente con nombre '{nombre}'.")
        return resultado

    def listar_docentes(self) -> List[Docente]:
        docentes = self._repo_docentes.todos()
        print(f"\n[Docentes registrados — {len(docentes)}]")
        for d in docentes:
            print(f"  • {d}")
        return docentes

    # ── IGestorAcademico ──────────────────────────────────────────────────────

    def registrar_asignatura(self, asignatura: Asignatura) -> None:
        self._repo_asignaturas.agregar(asignatura)
        print(f"[Sistema] Asignatura '{asignatura.nombre}' registrada.")

    def registrar_paralelo(self, paralelo: Paralelo) -> None:
        self._repo_paralelos.agregar(paralelo)
        print(f"[Sistema] Paralelo '{paralelo.codigo}' registrado.")

    def asignar_estudiante_a_paralelo(
        self, estudiante: Estudiante, paralelo: Paralelo
    ) -> None:
        self._svc_matricula.matricular_en_paralelo(estudiante, paralelo)

    # ── IGestorReportes ───────────────────────────────────────────────────────

    def generar_reporte_calificaciones(self, estudiante: Estudiante) -> Reporte:
        reporte = self._gestor_reportes.generar_reporte_calificaciones(estudiante)
        reporte.visualizar_reporte()
        return reporte

    def generar_reporte_docente(self, docente: Docente) -> Reporte:
        reporte = self._gestor_reportes.generar_reporte_docente(docente)
        reporte.visualizar_reporte()
        return reporte

    # ── Métodos adicionales del sistema ──────────────────────────────────────

    def registrar_sede(self, sede: Sede) -> None:
        if sede not in self._sedes:
            self._sedes.append(sede)
            print(f"[Sistema] Sede '{sede.nombre_sede}' registrada.")

    def asignar_docente_a_asignatura(
        self, docente: Docente, asignatura: Asignatura
    ) -> None:
        self._svc_asignacion.asignar_docente_a_asignatura(docente, asignatura)

    def asignar_sede_a_docente(self, docente: Docente, sede: Sede) -> None:
        self._svc_asignacion.asignar_sede_a_docente(docente, sede)

    def asignar_carga_horaria(self, docente: Docente, horas: int) -> None:
        self._svc_asignacion.asignar_carga_horaria(docente, horas)

    def calificar_estudiante(
        self,
        docente: Docente,
        estudiante: Estudiante,
        asignatura: Asignatura,
        nota: float,
        comentario: str = None,
    ) -> None:
        self._svc_calificaciones.calificar_estudiante(
            docente, estudiante, asignatura, nota, comentario
        )

    def matricular_en_carrera(
        self, estudiante: Estudiante, oferta: Oferta, puntaje: float
    ) -> None:
        self._svc_matricula.matricular_en_carrera(estudiante, oferta, puntaje)

    def activar_periodo(self, periodo: PeriodoAcademico) -> None:
        resultado = periodo.activar_periodo()
        self._periodos.append(periodo)
        print(f"[Sistema] {resultado}")

    def cerrar_periodo(self, periodo: PeriodoAcademico) -> None:
        self._admin.cerrar_periodo_academico(periodo)

    def generar_reporte_sede(self, sede: Sede) -> Reporte:
        reporte = self._gestor_reportes.generar_reporte_sede(sede)
        reporte.visualizar_reporte()
        return reporte

    def listar_todos_reportes(self) -> None:
        self._gestor_reportes.listar_reportes()

    def resumen_sistema(self) -> None:
        print(f"\n{'=' * 50}")
        print(f"  RESUMEN — {self.nombre_institucion}")
        print(f"{'=' * 50}")
        print(f"  Estudiantes : {len(self._repo_estudiantes.todos())}")
        print(f"  Docentes    : {len(self._repo_docentes.todos())}")
        print(f"  Asignaturas : {len(self._repo_asignaturas.todas())}")
        print(f"  Paralelos   : {len(self._repo_paralelos.todos())}")
        print(f"  Sedes       : {len(self._sedes)}")
        print(f"  Periodos    : {len(self._periodos)}")
        print(f"{'=' * 50}\n")
