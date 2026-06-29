from abc import ABC, abstractmethod
from .reporte import Reporte


class IReporteBuilder(ABC):
    @abstractmethod
    def reset(self, tipo_reporte):
        pass

    @abstractmethod
    def construir_encabezado(self, titulo, autor):
        pass

    @abstractmethod
    def construir_cuerpo(self, datos):
        pass

    @abstractmethod
    def construir_pie_pagina(self):
        pass

    @abstractmethod
    def obtener_resultado(self):
        pass


class ReporteAcademicoBuilder(IReporteBuilder):
    def __init__(self):
        self._reporte = None

    def reset(self, tipo_reporte):
        self._reporte = Reporte(tipo_reporte)

    def construir_encabezado(self, titulo, autor):
        self._reporte.encabezado = (
            "UNIVERSIDAD LAICA ELOY ALFARO DE MANABI (ULEAM)\n"
            "SISTEMA DE GESTION DE NIVELACION (SIGEN)\n"
            f"TITULO: {titulo}\n"
            f"SOLICITADO POR: {autor}\n"
            f"{'-' * 40}"
        )

    def construir_cuerpo(self, datos):
        cuerpo = "\n".join([f" -> {dato}" for dato in datos])
        self._reporte.cuerpo = f"DETALLE DE REGISTROS:\n{cuerpo}\n"

    def construir_pie_pagina(self):
        self._reporte.pie_pagina = (
            f"{'-' * 40}\n"
            "Documento de uso estrictamente academico.\n"
            "Generado automaticamente. Valido sin firma."
        )

    def obtener_resultado(self):
        reporte = self._reporte
        self._reporte = None
        return reporte


class ReporteDocenteBuilder(ReporteAcademicoBuilder):
    def construir_encabezado(self, titulo, autor):
        self._reporte.encabezado = (
            "UNIVERSIDAD LAICA ELOY ALFARO DE MANABI (ULEAM)\n"
            "SISTEMA DE GESTION DE NIVELACION (SIGEN)\n"
            "REPORTE DE DOCENTE\n"
            f"TITULO  : {titulo}\n"
            f"DOCENTE : {autor}\n"
            f"{'-' * 40}"
        )

    def construir_cuerpo(self, datos):
        cuerpo = "\n".join([f" >> {dato}" for dato in datos])
        self._reporte.cuerpo = f"INFORMACION DEL DOCENTE:\n{cuerpo}\n"


class ReporteSedeBuilder(ReporteAcademicoBuilder):
    def construir_encabezado(self, titulo, autor):
        self._reporte.encabezado = (
            "UNIVERSIDAD LAICA ELOY ALFARO DE MANABI (ULEAM)\n"
            "SISTEMA DE GESTION DE NIVELACION (SIGEN)\n"
            "REPORTE DE SEDE\n"
            f"TITULO : {titulo}\n"
            f"SEDE   : {autor}\n"
            f"{'-' * 40}"
        )

    def construir_cuerpo(self, datos):
        cuerpo = "\n".join([f" >> {dato}" for dato in datos])
        self._reporte.cuerpo = f"DETALLE DE SEDE:\n{cuerpo}\n"
