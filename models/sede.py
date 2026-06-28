from __future__ import annotations

class Sede:
    def __init__(self, id_sede, nombre_sede, ciudad, direccion, capacidad_total=500):
        self._id_sede = id_sede
        self._nombre_sede = nombre_sede
        self._ciudad = ciudad
        self._direccion = direccion
        self._capacidad_total = capacidad_total
        self._paralelos = []
        self._carreras = []
        self._ofertas = []

    @property
    def id_sede(self):
        return self._id_sede

    @property
    def nombre_sede(self):
        return self._nombre_sede

    @property
    def ciudad(self):
        return self._ciudad

    @property
    def direccion(self):
        return self._direccion

    @property
    def capacidad_total(self):
        return self._capacidad_total

    @property
    def paralelos(self):
        return self._paralelos

    @property
    def carreras(self):
        return self._carreras

    @property
    def ofertas(self):
        return self._ofertas

    def agregar_paralelo(self, paralelo):
        if paralelo not in self._paralelos:
            self._paralelos.append(paralelo)

    def agregar_carrera(self, carrera):
        if carrera not in self._carreras:
            self._carreras.append(carrera)

    def agregar_oferta(self, oferta):
        if oferta not in self._ofertas:
            self._ofertas.append(oferta)
            oferta.set_sede(self)

    def to_dict(self):
        return {
        "id_sede": self._id_sede,
        "nombre_sede": self._nombre_sede,
        "ciudad": self._ciudad,
        "direccion": self._direccion,
        "capacidad_total": self._capacidad_total,
    }

    def __str__(self):
        return (
            f"[Sede] {self._nombre_sede} - Ciudad: {self._ciudad} - "
            f"Dirección: {self._direccion} - "
            f"Capacidad: {self._capacidad_total} - "
            f"Paralelos: {len(self._paralelos)} - Carreras: {len(self._carreras)} - Ofertas: {len(self._ofertas)}"
        )
