def obtener_datos_calificaciones(estudiante):
    datos = []
    calificaciones = estudiante.ver_calificaciones()
    for materia, notas in calificaciones.items():
        if not isinstance(notas, list):
            notas = [{"nota": float(notas), "comentario": ""}]
        for indice, registro in enumerate(notas, start=1):
            nota = float(registro.get("nota", registro) if isinstance(registro, dict) else registro)
            comentario = registro.get("comentario", "") if isinstance(registro, dict) else ""
            estado_nota = "Aprobado" if nota >= 7.0 else "Reprobado"
            linea = f"{materia} - Nota {indice}: {nota:.2f} -> {estado_nota}"
            if comentario:
                linea += f" | {comentario}"
            datos.append(linea)
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
