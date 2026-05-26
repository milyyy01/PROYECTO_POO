class SistemaNivelacion:
    def __init__(self, nombre_institucion: str, nivel_academico: str):
        # ATRIBUTOS PÚBLICOS 
        self.nombre_institucion = nombre_institucion
        self.nivel_academico = nivel_academico

        # ATRIBUTOS PRIVADOS
        self.__estudiantes_registrados = 0
        self.__profesores_registrados = 0

        # ENLACES / RELACIONES (Listas para la multiplicidad 1..*)
        self.administradores = []
        self.paralelos = []
        self.asignaturas = []
        self.sedes = []

    # Métodos del diagrama
    def asignar_estudiante_a_paralelos(self):
        # Ejemplo de cómo el sistema manipula internamente su atributo privado:
        self.__estudiantes_registrados += 1
        print("Asignando estudiante a su respectivo paralelo...")

    def asignar_docentes(self):
        self.__profesores_registrados += 1
        print("Asignando docentes a las asignaturas...")

    def generar_horarios(self):
        print("Generando cronograma de horarios del periodo...")

    def ver_docentes_disponibles(self):
        print("Consultando lista de docentes activos/disponibles...")

    def ver_carrera_disponible(self):
        print("Mostrando oferta de carreras disponibles...")

    # GETTERS para los atributos privados (para poder leerlos, pero no modificarlos directamente)
    @property
    def estudiantes_registrados(self):
        return self.__estudiantes_registrados

    @property
    def profesores_registrados(self):
        return self.__profesores_registrados
