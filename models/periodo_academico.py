from datetime import date


class PeriodoAcademico:
    def __init__(self, fecha_inicio, fecha_fin, anio, semestre):
        if fecha_inicio >= fecha_fin:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin.")
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.anio = anio
        self.semestre = semestre
        self.activo = False

# Métodos:

    def activar_periodo(self):
        if self.activo:
            return f"El período '{self.semestre}' ya está activo."
        self.activo = True
        print(f"Periodo académico '{self.semestre} - {self.anio}' activado.")
        return f"Período '{self.semestre}' activado exitosamente."

    def culminar_periodo(self):
        if not self.activo:
            return f"El período '{self.semestre}' ya estaba inactivo."
        self.activo = False
        print(f"Periodo académico '{self.semestre} - {self.anio}' culminado.")
        return f"Período '{self.semestre}' culminado exitosamente."

    def duracion_periodo(self):
        dias = (self.fecha_fin - self.fecha_inicio).days
        print(f"Duración del período '{self.semestre}': {dias} días.")
        return dias

    def esta_activo(self):
        hoy = date.today()
        rango = self.fecha_inicio <= hoy <= self.fecha_fin
        return self.activo and rango
    
    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return (
            f"[PeriodoAcademico] {self.semestre} {self.anio} - "
            f"{self.fecha_inicio} -> {self.fecha_fin} | Estado: {estado}"
        )
