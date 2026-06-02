class Carrera: 
    def __init__(self, nombre_carrera: str, facultad: str, duracion_semestre: int, creditos_totales: int, cupos_totales: int):
        self._nombre_carrera = nombre_carrera
        self._facultad = facultad
        self._duracion_semestre = duracion_semestre
        self._creditos_totales = creditos_totales
        self._cupos_totales = cupos_totales

#Agregar en una lista las asignaturas
        self._asignaturas = []
        self._estudiantes_matriculados = []
#agregamos diccionario para simular los cupos
self._cupos_por_sede = {
    "Manta": cupos_totales,
    "Chone": 40,
    "Bahía": 30
}

@property
def nombre_carrera(self) -> str:
    return self._nombre_carrera

@property
def facultad(self) -> str:
    return self._facultad

@property
def duracion_semestre(self) -> int:
    return self._duracion_semestre

@property
def creditos_totales(self) -> int:
    return self._creditos_totales

@property
def cupos_totales(self) -> int:
    return self._cupos_totales

@cupos_totales.setter
def cupos_totales(self, nuevo_cupo: int):
    if nuevo_cupo >= 0:
        self.cupos_totales = nuevo_cupo
    else:
        raise ValueError ("Error, la cantidad no puede ser negativa")
    
#Métodos
def obtener_Asignaturas(self):
    return self.asignaturas

def ver_Cupos_Disponibles(self) -> int:
    return self._cupos_totales

def ver_Cupos_Por_Sede(self):
    print (f"\n Cupos disponibles por sede - Carrera: {self._nombre_carrera.upper()}")
    for sede, cupos in self._cupos_por_sede.items():
        print(f"Sede {sede}: {cupos} cupos.")

def agregar_Asignatura(self, asignatura):
    if asignatura not in self._asignaturas:
        self._asignaturas.append(asignatura)
        print(f"Asignatura '{asignatura.nombre}' agregada al plan de estudios de {self._nombre_carrera}.")

def matricular_Estudiante(self, estudiante):
    if len(self._estudiantes_matriculados) < self._cupos_totales:
        if estudiante not in self._estudiantes_matriculados:
            self._estudiantes_matriculados.append(estudiante)
            return True
    return False

def listar_Estudiantes(self):
    print(f"\n Reporte de los estudiantes matriculados {self._nombre_carrera.upper()}")
    if not self._estudiantes_matriculados:
        print("No hay estudiantes registrados en esta carrera actualmente.")
    else:
        for i, est in enumerate(self._estudiantes_matriculados, 1):
            print(f"  {i}. Cédula: {est.cedula} - Nombre: {est.nombre} - Correo: {est.correo}")
