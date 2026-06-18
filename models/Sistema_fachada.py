# fachada_sistema.py

from gestor_nivelacion import GestorNivelacion
from sede import Sede
from oferta import Oferta
from periodo_academico import PeriodoAcademico
from evaluacion import Evaluacion

class SistemaFachada:
    """
    Fachada para el sistema de nivelación.
    Centraliza el acceso a sedes, ofertas, periodos y evaluaciones.
    Mantiene la lógica existente del sistema.
    """

    def __init__(self):
        # Mantengo el gestor original tal como está
        self._gestor = GestorNivelacion()
        self._sedes = []
        self._ofertas = []
        self._periodos = []
        self._evaluaciones = []

    # -------------------
    # SEDE
    # -------------------
    def crear_sede(self, id_sede, nombre, ciudad, direccion):
        sede = Sede(id_sede, nombre, ciudad, direccion)
        self._sedes.append(sede)
        return sede

    def listar_sedes(self):
        return self._sedes

    # -------------------
    # OFERTA
    # -------------------
    def crear_oferta(self, sede, id_oferta, carrera, modalidad, cupo, precio):
        oferta = Oferta(id_oferta, carrera, modalidad, cupo, precio)
        sede.agregar_oferta(oferta)
        self._ofertas.append(oferta)
        return oferta

    def listar_ofertas(self):
        return self._ofertas

    # -------------------
    # PERIODO ACADÉMICO
    # -------------------
    def crear_periodo(self, oferta, id_periodo, nombre, inicio, fin):
        periodo = PeriodoAcademico(id_periodo, nombre, inicio, fin)
        oferta.agregar_periodo(periodo)
        self._periodos.append(periodo)
        return periodo

    def listar_periodos(self):
        return self._periodos

    # -------------------
    # EVALUACIONES
    # -------------------
    def crear_evaluacion(self, id_eval, nombre, tipo, fecha, puntaje_max):
        evaluacion = Evaluacion(id_eval, nombre, tipo, fecha, puntaje_max)
        self._evaluaciones.append(evaluacion)
        return evaluacion

    def listar_evaluaciones(self):
        return self._evaluaciones

    # -------------------
    # FUNCIONES DEL GESTOR (sin modificar lógica)
    # -------------------
    def inscribir_estudiante(self, estudiante, oferta):
        self._gestor.inscribir_estudiante(estudiante, oferta)

    def registrar_nota(self, estudiante, evaluacion, nota):
        self._gestor.registrar_nota(estudiante, evaluacion, nota)
