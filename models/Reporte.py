from datetime import datetime
class Reporte:
    def __init__(self, tipo_reporte: str, fecha_generacion: datetime = None):
        # ATRIBUTOS PÚBLICOS
        self.tipo_reporte = tipo_reporte
        self.fecha_generacion = fecha_generacion if fecha_generacion else datetime.now()

    # Métodos públicos de la clase 
    def visualizar_reporte(self):
        print(f"Visualizando reporte de tipo: {self.tipo_reporte}")
    def editar_reporte(self):
        print("Editando el reporte...")
    def eliminar_reporte(self):
        print("Reporte eliminado.")
    def imprimir_reporte(self):
        print("Imprimiendo reporte...")
