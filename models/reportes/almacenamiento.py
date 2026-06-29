import json
from pathlib import Path
from .reporte import Reporte


class ReporteStorage:
    def __init__(self, ruta):
        self.ruta = Path(ruta)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)

    def cargar(self):
        if not self.ruta.exists():
            return []
        with self.ruta.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return [Reporte.from_dict(item) for item in datos]

    def guardar(self, reportes):
        with self.ruta.open("w", encoding="utf-8") as archivo:
            json.dump([reporte.to_dict() for reporte in reportes], archivo, indent=4, ensure_ascii=False)

    def agregar(self, reporte):
        reportes = self.cargar()
        reportes.append(reporte)
        self.guardar(reportes)
