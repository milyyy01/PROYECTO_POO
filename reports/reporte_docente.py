def obtener_datos_docente(docente):
    datos = [
        f"Título       : {docente.titulo}",
        f"Especialidad : {docente.especialidad}",
        f"Nivel        : {docente.nivel}",
        f"Horas asign. : {docente.horas_asignadas}",
        f"Sede         : {docente.sede.nombre_sede if docente.sede else 'Sin sede'}",
        f"Materias     : {len(docente.materias_asignadas)}",
        f"Paralelos    : {len(docente.paralelos)}",
    ]

    return datos