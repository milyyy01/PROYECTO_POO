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