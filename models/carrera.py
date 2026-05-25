class Carrera: 
    def __init__(self, nombre_carrera: str, facultad: str, duracion_semestre: int, creditos_totales: int, cupos_totales: int):
        self._nombre_carrera = nombre_carrera
        self._facultad = facultad
        self._duracion_Semestre = duracion_semestre
        self._creditos_totales = creditos_totales
        self._cupos_totales = cupos_totales

#Agregar en una lista las asignaturas
        self.asignaturas = []

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
    pass

def agregar_Asignatura(self, asignatura):
    if asignatura not in self._asignaturas:
        self._asignaturas.append(asignatura)

def listar_Estudiantes(self):
    pass
