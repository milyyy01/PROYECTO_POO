from logic.gestor_nivelacion import GestorNivelacion
from models.sede import Sede
from models.oferta import Oferta
from models.periodo_academico import PeriodoAcademico

class SistemaFachada:
    """
    Fachada (patron estructural Facade) del sistema de nivelacion.

    Unifica el acceso a GestorNivelacion (que a su vez coordina
    repositorios y servicios internos: matricula, calificaciones,
    asignacion, reportes) junto con la gestion propia de sedes, ofertas y
    periodos.

    La interfaz grafica (app_gui.py) solo deberia interactuar con esta
    clase, sin necesidad de conocer GestorNivelacion ni los subsistemas
    que hay detras.
    """

    def __init__(self, nombre_institucion, admin, ruta_reportes=None):
        self._gestor = GestorNivelacion(nombre_institucion, admin, ruta_reportes=ruta_reportes)
        self._sedes = []
        self._ofertas = []
        self._periodos = []


    @property
    def nombre_institucion(self):
        return self._gestor.nombre_institucion

    @property
    def gestor(self):
        """Acceso directo al gestor interno, por si se requiere algo muy puntual."""
        return self._gestor

    # ── SEDES ────────────────────────────────────────────────────────────────

    def crear_sede(self, id_sede, nombre, ciudad, direccion):
        sede = Sede(id_sede, nombre, ciudad, direccion)
        self.registrar_sede(sede)
        return sede

    def registrar_sede(self, sede: Sede) -> None:
        if sede not in self._sedes:
            self._sedes.append(sede)
        self._gestor.registrar_sede(sede)

    def listar_sedes(self):
        return self._sedes

    # ── OFERTAS ──────────────────────────────────────────────────────────────

    def crear_oferta(self, sede, id_oferta, carrera, modalidad,
                      cupo=30, precio=0, fecha_apertura=None, fecha_cierre=None):
        oferta = Oferta(id_oferta, carrera, modalidad, cupo, precio,
                         fecha_apertura, fecha_cierre)
        if sede:
            sede.agregar_oferta(oferta)
        self._ofertas.append(oferta)
        return oferta

    def registrar_oferta(self, oferta: Oferta) -> None:
        if oferta not in self._ofertas:
            self._ofertas.append(oferta)

    def listar_ofertas(self):
        return self._ofertas

    # ── PERIODOS ACADÉMICOS ──────────────────────────────────────────────────

    def crear_periodo(self, oferta, id_periodo, nombre, inicio, fin):
        periodo = PeriodoAcademico(id_periodo, nombre, inicio, fin)
        oferta.agregar_periodo(periodo)
        self._periodos.append(periodo)
        return periodo

    def listar_periodos(self):
        return self._periodos

    def activar_periodo(self, periodo: PeriodoAcademico) -> None:
        self._gestor.activar_periodo(periodo)

    def cerrar_periodo(self, periodo: PeriodoAcademico) -> None:
        self._gestor.cerrar_periodo(periodo)


    # ── ESTUDIANTES ──────────────────────────────────────────────────────────

    def registrar_estudiante(self, estudiante) -> None:
        self._gestor.registrar_estudiante(estudiante)

    def buscar_estudiante(self, nombre: str):
        return self._gestor.buscar_estudiante(nombre)

    def listar_estudiantes(self):
        return self._gestor.listar_estudiantes()

    # ── DOCENTES ─────────────────────────────────────────────────────────────

    def registrar_docente(self, docente) -> None:
        self._gestor.registrar_docente(docente)

    def buscar_docente(self, nombre: str):
        return self._gestor.buscar_docente(nombre)

    def listar_docentes(self):
        return self._gestor.listar_docentes()

    def asignar_sede_a_docente(self, docente, sede) -> None:
        self._gestor.asignar_sede_a_docente(docente, sede)

    def asignar_carga_horaria(self, docente, horas: int) -> None:
        self._gestor.asignar_carga_horaria(docente, horas)

    def asignar_docente_a_asignatura(self, docente, asignatura) -> None:
        self._gestor.asignar_docente_a_asignatura(docente, asignatura)

    # ── ASIGNATURAS Y PARALELOS ──────────────────────────────────────────────

    def registrar_asignatura(self, asignatura) -> None:
        self._gestor.registrar_asignatura(asignatura)

    def registrar_paralelo(self, paralelo) -> None:
        self._gestor.registrar_paralelo(paralelo)

    def asignar_estudiante_a_paralelo(self, estudiante, paralelo) -> None:
        self._gestor.asignar_estudiante_a_paralelo(estudiante, paralelo)

    def retirar_estudiante_de_paralelo(self, estudiante, paralelo) -> None:
        self._gestor.retirar_estudiante_de_paralelo(estudiante, paralelo)

    def aumentar_cupos_paralelo(self, paralelo, cantidad: int) -> None:
        self._gestor.aumentar_cupos_paralelo(paralelo, cantidad)

    def reasignar_docente_paralelo(self, paralelo, docente) -> None:
        self._gestor.reasignar_docente_paralelo(paralelo, docente)

    # ── MATRÍCULA Y CALIFICACIONES ───────────────────────────────────────────

    def matricular_en_carrera(self, estudiante, oferta, puntaje: float) -> None:
        self._gestor.matricular_en_carrera(estudiante, oferta, puntaje)

    def calificar_estudiante(self, docente, estudiante, asignatura, nota: float, comentario: str = None) -> None:
        self._gestor.calificar_estudiante(docente, estudiante, asignatura, nota, comentario)

    # ── REPORTES ─────────────────────────────────────────────────────────────

    def generar_reporte_calificaciones(self, estudiante):
        return self._gestor.generar_reporte_calificaciones(estudiante)

    def generar_reporte_docente(self, docente):
        return self._gestor.generar_reporte_docente(docente)

    def generar_reporte_sede(self, sede):
        return self._gestor.generar_reporte_sede(sede)

    def listar_todos_reportes(self):
        return self._gestor.listar_todos_reportes()

    # ── RESUMEN GENERAL ──────────────────────────────────────────────────────

    def resumen_sistema(self) -> None:
        self._gestor.resumen_sistema()
