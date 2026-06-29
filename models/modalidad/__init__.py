from .estrategia import EstrategiaModalidad
from .estrategias_concretas import (
    EstrategiaPresencial,
    EstrategiaVirtual,
    EstrategiaHibrida,
    EstrategiaSemipresencial,
)
from .modalidad import Modalidad

__all__ = [
    "EstrategiaModalidad",
    "EstrategiaPresencial",
    "EstrategiaVirtual",
    "EstrategiaHibrida",
    "EstrategiaSemipresencial",
    "Modalidad",
]
