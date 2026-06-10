from datetime import datetime
from abc import ABC, abstractmethod

# Producto: 

class Reporte:

    def __init__(self, tipo_reporte, fecha_generacion=None):
        self.tipo_reporte = tipo_reporte
        self.fecha_generacion = fecha_generacion if fecha_generacion else datetime.now()

        self.encabezado = ""
        self.cuerpo = ""
        self.pie_pagina = ""
        self.__eliminado = False

    @property
    def eliminado(self):
        return self.__eliminado

    @property
    def contenido_completo(self):
        return f"{self.encabezado}\n{self.cuerpo}\n{self.pie_pagina}"

    def visualizar_reporte(self):
        if self.__eliminado:
            print("Este reporte ha sido eliminado y no puede visualizarse.")
            return

        print("===== REPORTE =====")
        print(f"Tipo           : {self.tipo_reporte}")
        print(f"Fecha generado : {self.fecha_generacion.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 25)

        if self.encabezado or self.cuerpo or self.pie_pagina:
            print(self.contenido_completo)
        else:
            print("(Sin contenido generado aún)")

        print("===================")

    def imprimir_reporte(self):
        if self.__eliminado:
            print("No se puede imprimir un reporte eliminado.")
            return

        print(f"Enviando '{self.tipo_reporte}' a la cola de impresión...")

    def solicitar_eliminacion(self):
        self.__eliminado = True
        print(f"Reporte '{self.tipo_reporte}' eliminado exitosamente.")

    def __str__(self):
        estado = "Eliminado" if self.__eliminado else "Activo"
        return (
            f"[Reporte] Tipo: {self.tipo_reporte} | "
            f"Fecha: {self.fecha_generacion.strftime('%Y-%m-%d')} | "
            f"Estado: {estado}"
        )


# Interfaces y builders específicos:

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

    def reset(self, tipo_reporte: str):
        self._reporte = Reporte(tipo_reporte)

    def construir_encabezado(self, titulo, autor):
        self._reporte.encabezado = (
            f"UNIVERSIDAD LAICA ELOY ALFARO DE MANABÍ (ULEAM)\n"
            f"SISTEMA DE GESTIÓN DE NIVELACIÓN (SIGEN)\n"
            f"TÍTULO: {titulo}\n"
            f"SOLICITADO POR: {autor}\n"
            f"{'-'*40}"
        )

    def construir_cuerpo(self, datos):
        cuerpo_str = "\n".join([f" -> {dato}" for dato in datos])
        self._reporte.cuerpo = f"DETALLE DE REGISTROS:\n{cuerpo_str}\n"

    def construir_pie_pagina(self):
        self._reporte.pie_pagina = (
            f"{'-'*40}\n"
            f"Documento de uso estrictamente académico.\n"
            f"Generado automáticamente. Válido sin firma."
        )

    def obtener_resultado(self):
        producto_final = self._reporte
        self._reporte = None
        return producto_final


# Director: 

class DirectorReportes:

    def __init__(self):
        self._builder = None

    @property
    def builder(self):
        return self._builder

    @builder.setter
    def builder(self, builder: IReporteBuilder):
        self._builder = builder

    def generar_reporte_calificaciones(
        self,
        estudiante_nombre,
        notas
    ):

        self.builder.reset("Académico - Calificaciones")

        self.builder.construir_encabezado(
            "Historial de Calificaciones",
            estudiante_nombre
        )

        self.builder.construir_cuerpo(notas)

        self.builder.construir_pie_pagina()

        return self.builder.obtener_resultado()