from evaluacion import Evaluacion

class Asignatura:
    def __init__ (self, nombre: str, hora: str, contenido: str, creditos: int):
        self._nombre = nombre
        self._hora = hora
        self._contenido = contenido
        self._creditos = creditos

        #Atributos extras para los métodos
        self._docente = None
        self._cupos_maximos = 0
        self._archivos_material = []

#Aplicamos composición de evaluación y la creamos en una lista
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
def subir_Archivo(self, nombre_archivo: str):
    if nombre_archivo.strip(): #valida que no esté vacío el texto
        self._archivos_material.append(nombre_archivo)
        print (f"Archivo '{nombre_archivo}' subido correctamente")
    else:
        raise ValueError ("El nombre del archivo no puede estar vacío)"

def asignar_Docente(self, nombre_docente: str):
    self._docente = nombre_docente
    print (f"El docente {nombre_docente} ha sido asignado a la asignatura {self._nombre}")

def asignar_Cupos(self, cantidad_cupos: int):
    if cantidad_cupos > 0:
        self._cupos_maximos = cantidad_cupos
        print(f"Se ha asignado {cantidad_cupos} cupos máximos para la asignatura {self._nombre}")
    else:
        raise ValueError("La cantidad de cupos debe ser mayor a cero.")

def obtener_Material(self):
    return self._contenido

#Metodo de composicion con evaluación
def crar_evaluación(self, puntaje_minimo: float, puntaje_maximo: float, tipo: str, fecha_apertura: str, fecha_cierre: str):
    nueva_evaluación = Evaluacion(self, puntaje_minimo, puntaje_maximo, tipo, fecha_apertura, fecha_cierre)
    self._evaluaciones.append(nueva_evaluación)
    return nueva_evaluación
