class Modalidad:
    MODALIDADES_VALIDAS = {"Presencial", "Virtual", "Híbrida", "Semipresencial"}
    
    def __init__(self, id_modalidad, tipo, descripcion, duracion_horas):
        self._id_modalidad = id_modalidad
        self.tipo = tipo
        self.descripcion = descripcion
        self.duracion_horas = duracion_horas
        self.__estado = "Activa"

    # Getter
    
    @property
    def id_modalidad(self):
        return self._id_modalidad
    
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
        if not nueva_descripcion.strip():
            raise ValueError("La descripción no puede estar vacía.")
        self.descripcion = nueva_descripcion
        print("Descripción actualizada correctamente.")

    def mostrar_informacion(self):
        print("===== INFORMACIÓN DE MODALIDAD =====")
        print(f"Tipo: {self.tipo}")
        print(f"Descripción: {self.descripcion}")
        print(f"Duración por clase: {self.duracion_horas} horas")
        print(f"Estado: {self.__estado}")

    def validar_modalidad(self):
        if self.tipo in self.MODALIDADES_VALIDAS:
            print(f"La modalidad {self.tipo} es válida.")
            return True
        else:
            print("Modalidad no válida.")
            return False
        
    # Se puede hacer la consulta sin depender de los demás
        
    def es_presencial(self):
        return self.tipo == "Presencial"  # ¿Esta modalidad es presencial?
 
    def es_virtual(self) -> bool:
        return self.tipo == "Virtual" # ¿Esta modalidad es virtual?
 
    def es_semi_presencial(self) -> bool:
        return self.tipo in {"Semipresencial", "Híbrida"} # ¿Esta modalidad es semipresencial o híbrida?

    def __str__(self):
        return (f"[Modalidad] Tipo: {self.tipo} | "
                f"Duración: {self.duracion_horas} horas | "
                f"Estado: {self.__estado}")