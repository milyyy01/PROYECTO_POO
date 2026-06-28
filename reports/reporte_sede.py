def obtener_datos_sede(sede):
    datos = [
        f"Ciudad       : {sede.ciudad}",
        f"Dirección    : {sede.direccion}",
        f"Capacidad    : {sede.capacidad_total}",
        f"Paralelos    : {len(sede._paralelos)}",
        f"Carreras     : {len(sede._carreras)}",
    ]

    return datos
