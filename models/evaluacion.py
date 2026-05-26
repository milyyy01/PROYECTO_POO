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
def aprobar(self) -> bool:
    pass

def reprobar(self) -> bool:
    pass

def mostrar_nota(self):
    pass

def reintentar_evaluacion(self):
    pass
