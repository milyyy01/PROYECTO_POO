def obtener_datos_calificaciones(estudiante):
    datos = []
    calificaciones = estudiante.ver_calificaciones()
    for materia, nota in calificaciones.items():
        estado_nota = "Aprobado" if nota >= 7.0 else "Reprobado"
        datos.append(f"{materia}: {nota:.2f} -> {estado_nota}")
    if not datos:
        datos = ["Sin calificaciones registradas."]
    datos.append(f"Promedio general: {estudiante.promedio:.2f}")
    return datos


def obtener_datos_docente(docente):
    return [
        f"Titulo       : {docente.titulo}",
        f"Especialidad : {docente.especialidad}",
        f"Nivel        : {docente.nivel}",
        f"Horas asign. : {docente.horas_asignadas}",
        f"Sede         : {docente.sede.nombre_sede if docente.sede else 'Sin sede'}",
        f"Materias     : {len(docente.materias_asignadas)}",
        f"Paralelos    : {len(docente.paralelos)}",
    ]


def obtener_datos_sede(sede):
    return [
        f"Ciudad       : {sede.ciudad}",
        f"Direccion    : {sede.direccion}",
        f"Capacidad    : {sede.capacidad_total}",
        f"Paralelos    : {len(sede._paralelos)}",
        f"Carreras     : {len(sede._carreras)}",
    ]
