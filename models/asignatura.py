from evaluacion import Evaluacion

class Asignatura:
    def __init__ (self, nombre: str, hora: str, contenido: str, creditos: int):
        self._nombre = nombre
        self._hora = hora
        self._contenido = contenido
        self._creditos = creditos

#Aplicamos la composición de evaluación y la creamos en una lista
        self._evaluaciones = []

@property
def nombre(self) -> str:
    return self._nombre

@property
def creditos(self) -> int:
    return self._creditos

@creditos.setter
def creditos(self, cantidad: int):
    if cantidad > 0:
        self._creditos = cantidad
    else:
        raise ValueError("Los creditos no pueden ser negativos")
    
#Metodos
def subir_Archivo(self):
    pass

def asignar_Docente(self):
    pass

def asignar_Cupos(self):
    pass

def obtener_Material(self):
    return self._contenido

#Metodo de composicion con evaluación
def crar_evaluación(self, puntaje_minimo: float, puntaje_maximo: float, tipo: str, fecha_apertura: str, fecha_cierre: str):
    nueva_evaluación = Evaluacion(self, puntaje_minimo, puntaje_maximo, tipo, fecha_apertura, fecha_cierre)
    self._evaluaciones.append(nueva_evaluación)
    return nueva_evaluación
