from datetime import datetime

class Reporte:
    def __init__(self, tipo_reporte, fecha_generacion = None):
        # ATRIBUTOS PÚBLICOS
        self.tipo_reporte = tipo_reporte
        self.fecha_generacion = fecha_generacion if fecha_generacion else datetime.now()

        self.__contenido: str = ""
        self.__eliminado: bool = False
    
    # Propiedades:
    
    @property
    def contenido(self):
        return self.__contenido
 
    @property
    def eliminado(self):
        return self.__eliminado
        
    # Métodos públicos de la clase 
    
    def visualizar_reporte(self):
        if self.__eliminado:
            print("Este reporte ha sido eliminado y no puede visualizarse.")
            return
        print("===== REPORTE =====")
        print(f"Tipo           : {self.tipo_reporte}")
        print(f"Fecha generado : {self.fecha_generacion.strftime('%Y-%m-%d %H:%M:%S')}")
        if self.__contenido:
            print(f"Contenido      :\n{self.__contenido}")
        else:
            print("(Sin contenido generado aún)")
        print("===================")
        
    def imprimir_reporte(self):
        print("Imprimiendo reporte...")
        
    def generar_contenido(self, contenido):
        if not contenido.strip():
            raise ValueError("El contenido del reporte no puede estar vacío.")
        self.__contenido = contenido
        print(f"Contenido generado para el reporte '{self.tipo_reporte}'.")
        
    def __editar_reporte(self, nuevo_contenido: str):
        if self.__eliminado:
            print("No se puede editar un reporte eliminado.")
            return
        self.__contenido = nuevo_contenido
        print(f"Reporte '{self.tipo_reporte}' editado exitosamente.")
 
    def __eliminar_reporte(self):
        self.__eliminado = True
        print(f"Reporte '{self.tipo_reporte}' eliminado exitosamente.")
        
    # Métodos de acceso controlado a las operaciones privadas
    # (el Administrador llama a estos, no a los privados directamente)
 
    def solicitar_edicion(self, nuevo_contenido: str):
        self.__editar_reporte(nuevo_contenido)
 
    def solicitar_eliminacion(self):
        self.__eliminar_reporte()
 
    def __str__(self):
        estado = "Eliminado" if self.__eliminado else "Activo"
        return (
            f"[Reporte] Tipo: {self.tipo_reporte} | "
            f"Fecha: {self.fecha_generacion.strftime('%Y-%m-%d')} | "
            f"Estado: {estado}"
        )