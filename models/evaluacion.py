from asignatura import Evaluacion

class Evaluacion:
    def __init__ (self, puntaje_minimo: float, puntaje_maximo: float, tipo: str, fecha_apertura: str, fecha_cierre: str, asignatura: "Asignatura"):
        self._puntaje_minimo = puntaje_minimo
        self._puntaje_maximo = puntaje_maximo
        self._tipo = tipo
        self._fecha_apertura = fecha_apertura
        self._fecha_cierre = fecha_cierre

        if asignatura is None:
            raise ValueError("La evaluación no puede existir sin una asignatura enlazada")
        self._asignatura = asignatura
        self._registro_notas = {}

@property
def tipo(self) -> str:
    return self._tipo

@property
def puntaje_minimo(self) -> float:
    return self._puntaje_minimo

@property
def puntaje_maximo(self) -> float:
    return self._puntaje_maximo

@puntaje_maximo.setter
def puntaje_maximo(self, valor: float):
    if valor >= self._puntaje_minimo:
        self._puntaje_maximo = valor
    else:
        raise ValueError ("El puntaje máximo no puede ser menor al puntaje mínimo para aprobar")

@property
def asignatura(self):
    return self._asignatura

#Metodos
def aprobar(self, nota_obtenida: float) -> bool:
    if nota_obtenida < 0 or nota_obtenida > self._puntaje_maximo:
        raise ValueError(f"La nota debe estar entre 0 y {self._puntaje_maximo}")
    return nota_obtenida >= self._puntaje_minimo

def reprobar(self, nota_obtenida: float) -> bool:
    return not self.aprobar(nota_obtenida)

def mostrar_nota(self, nombre_estudiante: str):
    if nombre_estudiante in self._registro_notas:
        nota = self._registro_notas[nombre_estudiante]
        estado = "Aprobado" if self.aprobar(nota) else "Reprobado"
        print(f"El estudiante {nombre_estudiante}" - {self._tipo} ({self._asignatura.nombre}) - Nota: {nota}/{self._puntaje_maximo} -> {estado}")

def reintentar_evaluacion(self, nombre_estudiante: str, nueva_nota: float):
    print(f"Procesando el reintento de {self._tipo} para el estudiante {nombre_estudiante}")
    if 0 <= nueva_nota <= self._puntaje_maximo:
        self._registro_notas[nombre_estudiante] = nueva_nota
        print (f"Nueva nota registrada correctamente")
        self.mostrar_nota(nombre_estudiante)
    else:
        raise ValueError(f"La nota para reintentar no es válida. Máximo permitido: {self._puntaje_maximo}")
    
