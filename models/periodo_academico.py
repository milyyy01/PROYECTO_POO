from datetime import date, datetime

class PeriodoAcademico:
    def __init__(self, id_periodo, nombre, fecha_inicio, fecha_fin, estado=True):
        # Convierte cadenas a date automáticamente
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

        if fecha_inicio >= fecha_fin:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin.")

        self._id_periodo = id_periodo
        self._nombre = nombre
        self._fecha_inicio = fecha_inicio
        self._fecha_fin = fecha_fin
        self._estado = estado
        self._oferta = None

    @property
    def id_periodo(self):
        return self._id_periodo

    @property
    def nombre(self):
        return self._nombre

    @property
    def fecha_inicio(self):
        return self._fecha_inicio

    @property
    def fecha_fin(self):
        return self._fecha_fin

    @property
    def estado(self):
        return self._estado

    @property
    def oferta(self):
        return self._oferta

    def set_oferta(self, oferta):
        self._oferta = oferta

    def activar_periodo(self):
        self._estado = True

    def culminar_periodo(self):
        self._estado = False

    def duracion_periodo(self):
        return (self._fecha_fin - self._fecha_inicio).days

    def esta_activo(self):
        hoy = date.today()
        return self._estado and self._fecha_inicio <= hoy <= self._fecha_fin

    def __str__(self):
        estado = "Activo" if self._estado else "Inactivo"
        return f"[PeriodoAcademico] {self._nombre} - {self._fecha_inicio} a {self._fecha_fin} | Estado: {estado}"