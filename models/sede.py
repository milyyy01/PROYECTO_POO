class Sede:

    def __init__(self, id_sede, nombre_sede, ciudad, direccion):
        self._id_sede = id_sede
        self._nombre_sede = nombre_sede
        self._ciudad = ciudad
        self._direccion = direccion

        # composición: Sede contiene ofertas
        self._ofertas = []

    #getters 
    def get_id_sede(self):
        return self._id_sede

    def get_nombre_sede(self):
        return self._nombre_sede

    def get_ciudad(self):
        return self._ciudad

    def get_direccion(self):
        return self._direccion

    def get_ofertas(self):
        return self._ofertas

    def agregar_oferta(self, oferta):
        if oferta not in self._ofertas:
            self._ofertas.append(oferta)
            oferta.set_sede(self)

    def eliminar_oferta(self, oferta):
        if oferta in self._ofertas:
            self._ofertas.remove(oferta)
            oferta.set_sede(None)

    def __str__(self):
        return f"Sede: {self._nombre_sede} - {self._ciudad}"
