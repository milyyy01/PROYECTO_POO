from datetime import datetime


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
        print(self.contenido_completo if self.contenido_completo.strip() else "(Sin contenido generado aun)")
        print("===================")

    def imprimir_reporte(self):
        if self.__eliminado:
            print("No se puede imprimir un reporte eliminado.")
            return
        print(f"Enviando '{self.tipo_reporte}' a la cola de impresion...")

    def solicitar_eliminacion(self):
        self.__eliminado = True
        print(f"Reporte '{self.tipo_reporte}' eliminado exitosamente.")

    def to_dict(self):
        return {
            "tipo_reporte": self.tipo_reporte,
            "fecha_generacion": self.fecha_generacion.isoformat(),
            "encabezado": self.encabezado,
            "cuerpo": self.cuerpo,
            "pie_pagina": self.pie_pagina,
            "eliminado": self.__eliminado,
        }

    @classmethod
    def from_dict(cls, datos):
        fecha = datetime.fromisoformat(datos["fecha_generacion"])
        reporte = cls(datos["tipo_reporte"], fecha)
        reporte.encabezado = datos.get("encabezado", "")
        reporte.cuerpo = datos.get("cuerpo", "")
        reporte.pie_pagina = datos.get("pie_pagina", "")
        if datos.get("eliminado", False):
            reporte.solicitar_eliminacion()
        return reporte

    def __str__(self):
        estado = "Eliminado" if self.__eliminado else "Activo"
        return (
            f"[Reporte] Tipo: {self.tipo_reporte} | "
            f"Fecha: {self.fecha_generacion.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Estado: {estado}"
        )
