class Paralelo:
    def __init__(self, codigo, docente, horario, modalidad):
        self.codigo = codigo
        self.docente = docente
        self.horario = horario
        self.modalidad = modalidad
        self.__estudiantes = []
        self.__estado = "Activo"

    # Getter
    @property
    def estado(self):
        return self.__estado

    @property
    def estudiantes(self):
        return self.__estudiantes

    # Métodos
    def agregar_estudiante(self, estudiante):
        self.__estudiantes.append(estudiante)
        print(f"Estudiante {estudiante.nombre} agregado al paralelo {self.codigo}.")

    def eliminar_estudiante(self, estudiante):
        if estudiante in self.__estudiantes:
            self.__estudiantes.remove(estudiante)
            print(f"Estudiante eliminado del paralelo {self.codigo}.")
        else:
            print("El estudiante no pertenece al paralelo.")

    def activar_paralelo(self):
        self.__estado = "Activo"
        print("Paralelo activado.")

    def desactivar_paralelo(self):
        self.__estado = "Inactivo"
        print("Paralelo desactivado.")

    def mostrar_informacion(self):
        print("===== INFORMACIÓN DEL PARALELO =====")
        print(f"Código: {self.codigo}")
        print(f"Docente: {self.docente.nombre}")
        print(f"Modalidad: {self.modalidad.tipo}")
        print(f"Horario: {self.horario.dia} | "
              f"{self.horario.hora_inicio} - {self.horario.hora_fin}")
        print(f"Estado: {self.__estado}")
        print(f"Cantidad de estudiantes: {len(self.__estudiantes)}")

    def listar_estudiantes(self):
        if not self.__estudiantes:
            print("No hay estudiantes registrados.")
        else:
            print("===== ESTUDIANTES =====")
            for estudiante in self.__estudiantes:
                print(f"- {estudiante.nombre}")

    def __str__(self):
        return (f"[Paralelo] Código: {self.codigo} | "
                f"Docente: {self.docente.nombre} | "
                f"Estado: {self.__estado}")