from models.modalidad import Modalidad

modalidad1 = Modalidad(
    "Virtual",
    "Clases mediante plataforma en línea",
    2
)

modalidad1.mostrar_informacion()

modalidad1.validar_modalidad()

print(modalidad1)
from models.horario import Horario

horario1 = Horario(
    "Lunes",
    7,
    9,
    "Laboratorio A"
)

horario1.mostrar_horario()

horario1.validar_horas()

print(horario1)