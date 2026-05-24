class Horario:
    def __init__(self, dia, hora_inicio, hora_fin, aula):
        self.dia = dia
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.aula = aula
        self.__estado = "Activo"

    # Getter
    @property
    def estado(self):
        return self.__estado

    # Métodos
    def activar_horario(self):
        self.__estado = "Activo"
        print("Horario activado correctamente.")

    def desactivar_horario(self):
        self.__estado = "Inactivo"
        print("Horario desactivado correctamente.")

    def modificar_aula(self, nueva_aula):
        self.aula = nueva_aula
        print(f"Aula actualizada a: {self.aula}")

    def mostrar_horario(self):
        print("===== HORARIO =====")
        print(f"Día: {self.dia}")
        print(f"Hora inicio: {self.hora_inicio}")
        print(f"Hora fin: {self.hora_fin}")
        print(f"Aula: {self.aula}")
        print(f"Estado: {self.__estado}")

    def validar_horas(self):
        if self.hora_inicio < self.hora_fin:
            print("Horario válido.")
            return True
        else:
            print("Error: la hora de inicio debe ser menor.")
            return False

    def __str__(self):
        return (f"[Horario] {self.dia} | "
                f"{self.hora_inicio} - {self.hora_fin} | "
                f"Aula: {self.aula} | "
                f"Estado: {self.__estado}")