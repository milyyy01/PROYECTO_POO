from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.paralelo import Paralelo
    from models.carrera import Carrera
    from models.oferta import Oferta

class Sede:
    def __init__(self, id_sede, nombre_sede, direccion, ciudad, capacidad_total):
        self._id_sede = id_sede
        self.nombre_sede = nombre_sede
        self.direccion = direccion
        self.ciudad = ciudad
        self._capacidad_total = capacidad_total
        self._paralelos = []
        self._carreras = []
        self._ofertas = []
        
    # Propiedades: 
    @property
    def id_sede(self):
        return self._id_sede
 
    @property
    def capacidad_total(self):
        return self._capacidad_total
    
    # Métodos 

    def calcular_disponibilidad(self):
        cupos_ocupados = sum(oferta.cupos_ocupados for oferta in self._ofertas)
        disponibilidad = self._capacidad_total - cupos_ocupados
        print(f"Sede '{self.nombre_sede}': {disponibilidad} cupos disponibles "
              f"de {self._capacidad_total}.")
        return disponibilidad

    def listar_paralelos(self):
        if not self._paralelos:
            print(f"No hay paralelos registrados en '{self.nombre_sede}'.")
            return []
        print(f"Paralelos en sede '{self.nombre_sede}':")
        for paralelo in self._paralelos:
            print(f"  - {paralelo.codigo} | Docente: {paralelo.docente.nombre} | "
                  f"Estado: {paralelo.estado}")
        return list(self._paralelos)

    def listar_carreras(self):
        if not self._carreras:
            print(f"No hay carreras registradas en '{self.nombre_sede}'.")
            return []
        print(f"Carreras en sede '{self.nombre_sede}':")
        for carrera in self._carreras:
            print(f"  - {carrera.nombre_carrera} | Facultad: {carrera.facultad}")
        return list(self._carreras)
    
    def obtener_ofertas(self):
        if not self._ofertas:
            print(f"No hay ofertas en '{self.nombre_sede}'.")
            return []
        print(f"Ofertas en sede '{self.nombre_sede}':")
        for oferta in self._ofertas:
            print(f"  - {oferta}")
        return list(self._ofertas)

    def agregar_paralelo(self, paralelo: "Paralelo"):
        if paralelo not in self._paralelos:
            self._paralelos.append(paralelo)
            print(f"Paralelo '{paralelo.codigo}' registrado en sede '{self.nombre_sede}'.") 

    def agregar_carrera(self, carrera: "Carrera"):
        if carrera not in self._carreras:
            self._carreras.append(carrera)
            print(f"Carrera '{carrera.nombre_carrera}' registrada en sede '{self.nombre_sede}'.")

    def agregar_oferta(self, oferta: "Oferta"):
        if oferta not in self._ofertas:
            self._ofertas.append(oferta)
            print(f"Oferta registrada en sede '{self.nombre_sede}'.")
            
    def __str__(self):
        return (
            f"[Sede] {self.nombre_sede} - Ciudad: {self.ciudad} - "
            f"Dirección: {self.direccion} - "
            f"Capacidad: {self._capacidad_total} - "
            f"Paralelos: {len(self._paralelos)} - Carreras: {len(self._carreras)}"
        )
