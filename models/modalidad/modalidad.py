from .estrategias_concretas import (
    EstrategiaPresencial,
    EstrategiaVirtual,
    EstrategiaHibrida,
    EstrategiaSemipresencial,
)


class Modalidad:
    MODALIDADES_VALIDAS = {"Presencial", "Virtual", "Híbrida", "Semipresencial"}
    _ESTRATEGIAS = {
        "Presencial": EstrategiaPresencial,
        "Virtual": EstrategiaVirtual,
        "Híbrida": EstrategiaHibrida,
        "Semipresencial": EstrategiaSemipresencial,
    }

    def __init__(self, id_modalidad, tipo, descripcion=None, duracion_horas=None, estrategia=None):
        self._id_modalidad = id_modalidad
        self.tipo = tipo
        self._estrategia = estrategia or self._crear_estrategia(tipo)
        self.descripcion = descripcion or self._estrategia.descripcion()
        self.duracion_horas = duracion_horas or self._estrategia.duracion_horas()
        self.__estado = "Activa"

    @classmethod
    def crear(cls, id_modalidad, tipo):
        modalidad = cls(id_modalidad=id_modalidad, tipo=tipo)
        if not modalidad.validar_modalidad():
            raise ValueError(f"Modalidad no valida: {tipo}")
        modalidad.aplicar_estrategia()
        return modalidad

    @classmethod
    def _crear_estrategia(cls, tipo):
        estrategia_cls = cls._ESTRATEGIAS.get(tipo)
        if not estrategia_cls:
            raise ValueError(f"Modalidad no valida: {tipo}")
        return estrategia_cls()

    @property
    def id_modalidad(self):
        return self._id_modalidad

    @property
    def estado(self):
        return self.__estado

    def aplicar_estrategia(self):
        self.actualizar_descripcion(self._estrategia.descripcion())
        self.duracion_horas = self._estrategia.duracion_horas()

    def activar_modalidad(self):
        self.__estado = "Activa"
        print(f"La modalidad {self.tipo} fue activada.")

    def desactivar_modalidad(self):
        self.__estado = "Inactiva"
        print(f"La modalidad {self.tipo} fue desactivada.")

    def actualizar_descripcion(self, nueva_descripcion):
        if not nueva_descripcion.strip():
            raise ValueError("La descripcion no puede estar vacia.")
        self.descripcion = nueva_descripcion

    def mostrar_informacion(self):
        print("===== INFORMACION DE MODALIDAD =====")
        print(f"Tipo: {self.tipo}")
        print(f"Descripcion: {self.descripcion}")
        print(f"Duracion por clase: {self.duracion_horas} horas")
        print(f"Estado: {self.__estado}")

    def validar_modalidad(self):
        return self.tipo in self.MODALIDADES_VALIDAS

    def es_presencial(self):
        return self.tipo == "Presencial"

    def es_virtual(self):
        return self.tipo == "Virtual"

    def es_semi_presencial(self):
        return self.tipo in {"Semipresencial", "Híbrida"}

    def __str__(self):
        return (
            f"[Modalidad] Tipo: {self.tipo} | "
            f"Duracion: {self.duracion_horas} horas | "
            f"Estado: {self.__estado}"
        )
