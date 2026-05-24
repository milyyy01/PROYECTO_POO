class Modalidad:
    def __init__(self, tipo, descripcion, duracion_horas):
        self.tipo = tipo
        self.descripcion = descripcion
        self.duracion_horas = duracion_horas
        self.__estado = "Activa"

    # Getter
    @property
    def estado(self):
        return self.__estado

    # Métodos
    def activar_modalidad(self):
        self.__estado = "Activa"
        print(f"La modalidad {self.tipo} fue activada.")

    def desactivar_modalidad(self):
        self.__estado = "Inactiva"
        print(f"La modalidad {self.tipo} fue desactivada.")

    def actualizar_descripcion(self, nueva_descripcion):
        self.descripcion = nueva_descripcion
        print("Descripción actualizada correctamente.")

    def mostrar_informacion(self):
        print("===== INFORMACIÓN DE MODALIDAD =====")
        print(f"Tipo: {self.tipo}")
        print(f"Descripción: {self.descripcion}")
        print(f"Duración por clase: {self.duracion_horas} horas")
        print(f"Estado: {self.__estado}")

    def validar_modalidad(self):
        modalidades_validas = ["Presencial", "Virtual", "Híbrida"]

        if self.tipo in modalidades_validas:
            print(f"La modalidad {self.tipo} es válida.")
            return True
        else:
            print("Modalidad no válida.")
            return False

    def __str__(self):
        return (f"[Modalidad] Tipo: {self.tipo} | "
                f"Duración: {self.duracion_horas} horas | "
                f"Estado: {self.__estado}")