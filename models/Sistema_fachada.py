from logic.gestor_nivelacion import GestorNivelacion
from models.sede import Sede
from models.oferta import Oferta
from models.periodo_academico import PeriodoAcademico
from models.evaluacion import Evaluacion

class SistemaFachada:
    """
    Fachada para el sistema de nivelación.
    Centraliza el acceso a sedes, ofertas, periodos y evaluaciones.
    """

    def __init__(self, nombre_institucion, admin):
        self._gestor = GestorNivelacion(nombre_institucion, admin)
        self._sedes = []
        self._ofertas = []
        self._periodos = []
        self._evaluaciones = []

    
    # SEDE
    def crear_sede(self, id_sede, nombre, ciudad, direccion):
        sede = Sede(id_sede, nombre, ciudad, direccion)
        self._sedes.append(sede)
        return sede

    def listar_sedes(self):
        return self._sedes
    

    # OFERTA
    def crear_oferta(self, sede, id_oferta, carrera, modalidad,
                 cupo=30, precio=0, fecha_apertura=None, fecha_cierre=None):
     oferta = Oferta(id_oferta, carrera, modalidad, cupo, precio,
                    fecha_apertura, fecha_cierre)
     sede.agregar_oferta(oferta)
     self._ofertas.append(oferta)
     return oferta

    def listar_ofertas(self):
        return self._ofertas


    # PERIODO ACADÉMICO
    def crear_periodo(self, oferta, id_periodo, nombre, inicio, fin):
        periodo = PeriodoAcademico(id_periodo, nombre, inicio, fin)
        oferta.agregar_periodo(periodo)
        self._periodos.append(periodo)
        return periodo

    def listar_periodos(self):
        return self._periodos


    # EVALUACIONES
    def crear_evaluacion(self, id_eval, nombre, tipo, fecha, puntaje_max):
        evaluacion = Evaluacion(id_eval, nombre, tipo, fecha, puntaje_max)
        self._evaluaciones.append(evaluacion)
        return evaluacion

    def listar_evaluaciones(self):
        return self._evaluaciones


    # FUNCIONES DEL GESTOR 
    def inscribir_estudiante(self, estudiante, oferta):
        self._gestor.inscribir_estudiante(estudiante, oferta)

    def registrar_nota(self, estudiante, evaluacion, nota):
        self._gestor.registrar_nota(estudiante, evaluacion, nota)
