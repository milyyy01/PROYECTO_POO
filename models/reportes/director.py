from .builders import IReporteBuilder


class DirectorReportes:
    def __init__(self):
        self._builder = None

    @property
    def builder(self):
        return self._builder

    @builder.setter
    def builder(self, builder: IReporteBuilder):
        self._builder = builder

    def generar(self, tipo, titulo, autor, datos):
        self.builder.reset(tipo)
        self.builder.construir_encabezado(titulo, autor)
        self.builder.construir_cuerpo(datos)
        self.builder.construir_pie_pagina()
        return self.builder.obtener_resultado()
