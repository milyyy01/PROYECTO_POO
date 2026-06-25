from datetime import date, datetime

class Evaluacion:
    def __init__(self, id_eval, nombre, tipo, fecha, puntaje_max, asignatura=None):
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        self._id_eval = id_eval
        self._nombre = nombre
        self._tipo = tipo
        self._fecha = fecha
        self._puntaje_max = puntaje_max
        self._asignatura = asignatura  # ahora opcional

    @property
    def id_eval(self):
        return self._id_eval

    @property
    def nombre(self):
        return self._nombre

    @property
    def tipo(self):
        return self._tipo

    @property
    def fecha(self):
        return self._fecha

    @property
    def puntaje_max(self):
        return self._puntaje_max

    def __str__(self):
        return f"{self._nombre} ({self._tipo}) - Puntaje Máximo: {self._puntaje_max}"
    
    def set_asignatura(self, asignatura):
      self._asignatura = asignatura 