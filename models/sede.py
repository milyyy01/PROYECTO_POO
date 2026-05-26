class Sede:
    def __init__(self, id_sede, nombre_sede, direccion, ciudad, capacidad_total):
        self.id_sede = id_sede
        self.nombre_sede = nombre_sede
        self.direccion = direccion
        self.ciudad = ciudad
        self.capacidad_total = capacidad_total
        self.paralelos = []
        self.carreras = []
        self.ofertas = []

    def calcular_disponibilidad(self):
        cupos_ocupados = sum(oferta.cupos_ocupados for oferta in self.ofertas)
        return self.capacidad_total - cupos_ocupados

    def listar_paralelos(self):
        return self.paralelos

    def listar_carreras(self):
        return self.carreras

    def obtener_ofertas(self):
        return self.ofertas

    def agregar_paralelo(self, paralelo):
        self.paralelos.append(paralelo)

    def agregar_carrera(self, carrera):
        self.carreras.append(carrera)

    def agregar_oferta(self, oferta):
        self.ofertas.append(oferta)
