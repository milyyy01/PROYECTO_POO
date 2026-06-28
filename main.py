"""
main.py — Demo funcional de SIGEN
Ejercita todos los flujos usando GestorNivelacion (SOLID + Builder)
"""

from datetime import date
from models.administrador import Administrador
from models.estudiante import Estudiante
from models.docente import Docente
from models.asignatura import Asignatura
from models.carrera import Carrera
from models.sede import Sede
from models.paralelo import Paralelo
from models.horario import Horario
from models.modalidad import Modalidad
from models.periodo_academico import PeriodoAcademico
from models.oferta import Oferta
from logic.gestor_nivelacion import GestorNivelacion

# 1. ADMINISTRADOR Y SISTEMA

admin = Administrador(
    id=1,
    nombre="Carlos Mendoza",
    correo="cmendoza@uleam.edu.ec",
    contrasena="Admin123",
    telefono="0991234567",
    nivel_autoridad="Alto",
    departamento_asignado="Nivelación",
)

gestor = GestorNivelacion("ULEAM - Campus Manta", admin)

# 2. SEDE

sede_manta = Sede(
    id_sede=1,
    nombre_sede="Sede Manta",
    direccion="Av. Universitaria s/n",
    ciudad="Manta",
    capacidad_total=500,
)
gestor.registrar_sede(sede_manta)

# 3. PERIODO ACADÉMICO

periodo = PeriodoAcademico(
    fecha_inicio=date(2025, 5, 1),
    fecha_fin=date(2025, 10, 31),
    anio=2025,
    semestre="2025-I",
)
gestor.activar_periodo(periodo)

# 4. CARRERA Y OFERTA

carrera_sistemas = Carrera(
    id_carrera=1,
    nombre_carrera="Ingeniería en Sistemas",
    facultad="Ciencias Informáticas",
    duracion_semestre=8,
    creditos_totales=240,
    cupos_totales=40,
)
sede_manta.agregar_carrera(carrera_sistemas)

oferta = Oferta(
    cupos_total=40,
    cupos_ocupados=0,
    puntaje_minimo=600,
    puntaje_maximo=1000,
    fecha_apertura=date(2025, 4, 1),
    fecha_cierre=date(2025, 4, 30),
    sede=sede_manta,
    carrera=carrera_sistemas,
    periodo_academico=periodo,
)
sede_manta.agregar_oferta(oferta)

# 5. MODALIDAD Y HORARIO

modalidad_presencial = Modalidad(
    id_modalidad=1,
    tipo="Presencial",
    descripcion="Clases en aula física",
    duracion_horas=2,
)

horario_lunes = Horario(
    id_horario="H001",
    dia="Lunes",
    hora_inicio="07:00",
    hora_fin="09:00",
    aula="Aula 101",
)

# 6. DOCENTES

docente1 = Docente(
    id=10,
    nombre="Ana Torres",
    correo="atorres@uleam.edu.ec",
    contrasena="Docente1",
    telefono="0987654321",
    titulo="PhD en Computación",
    especialidad="Programación Orientada a Objetos",
    nivel="Senior",
)
docente2 = Docente(
    id=11,
    nombre="Luis Ponce",
    correo="lponce@uleam.edu.ec",
    contrasena="Docente2",
    telefono="0976543210",
    titulo="MSc en Redes",
    especialidad="Redes y Telecomunicaciones",
    nivel="Junior",
)

gestor.registrar_docente(docente1)
gestor.registrar_docente(docente2)
gestor.asignar_sede_a_docente(docente1, sede_manta)
gestor.asignar_sede_a_docente(docente2, sede_manta)
gestor.asignar_carga_horaria(docente1, 20)
gestor.asignar_carga_horaria(docente2, 16)

# 7. ASIGNATURAS

asig_poo = Asignatura(
    id_asignatura="A001",
    nombre="Programación Orientada a Objetos",
    contenido="Clases, objetos, herencia, polimorfismo",
    creditos=4,
)
asig_mat = Asignatura(
    id_asignatura="A002",
    nombre="Matemáticas Discretas",
    contenido="Lógica, conjuntos, grafos",
    creditos=3,
)

gestor.registrar_asignatura(asig_poo)
gestor.registrar_asignatura(asig_mat)
gestor.asignar_docente_a_asignatura(docente1, asig_poo)
gestor.asignar_docente_a_asignatura(docente2, asig_mat)

carrera_sistemas.agregar_asignatura(asig_poo)
carrera_sistemas.agregar_asignatura(asig_mat)

# 8. PARALELOS

paralelo_a = Paralelo(
    codigo="SIS-A",
    capacidad=30,
    docente=docente1,
    horario=horario_lunes,
    modalidad=modalidad_presencial,
)
gestor.registrar_paralelo(paralelo_a)
sede_manta.agregar_paralelo(paralelo_a)

# 9. ESTUDIANTES

est1 = Estudiante(
    id=100,
    nombre="María García",
    correo="mgarcia@est.uleam.edu.ec",
    contrasena="Est1234",
    telefono="0961234567",
    fecha_matricula=date(2025, 5, 1),
    sede=sede_manta,
    carrera=carrera_sistemas,
)
est2 = Estudiante(
    id=101,
    nombre="Pedro Vera",
    correo="pvera@est.uleam.edu.ec",
    contrasena="Est5678",
    telefono="0952345678",
    fecha_matricula=date(2025, 5, 1),
    sede=sede_manta,
    carrera=carrera_sistemas,
)

gestor.registrar_estudiante(est1)
gestor.registrar_estudiante(est2)

# Matrícula en carrera vía oferta

print("\n--- MATRÍCULAS EN CARRERA ---")
gestor.matricular_en_carrera(est1, oferta, puntaje=750)
gestor.matricular_en_carrera(est2, oferta, puntaje=820)

# Matrícula en paralelo

print("\n--- MATRÍCULAS EN PARALELO ---")
gestor.asignar_estudiante_a_paralelo(est1, paralelo_a)
gestor.asignar_estudiante_a_paralelo(est2, paralelo_a)

# 10. CALIFICACIONES

print("\n--- CALIFICACIONES ---")
gestor.calificar_estudiante(docente1, est1, asig_poo, 8.5, "Excelente trabajo")
gestor.calificar_estudiante(docente1, est2, asig_poo, 6.5)
gestor.calificar_estudiante(docente2, est1, asig_mat, 9.0)
gestor.calificar_estudiante(docente2, est2, asig_mat, 5.0, "Necesita mejorar")

print("\n--- VER CALIFICACIONES ---")
est1.ver_calificaciones()
est2.ver_calificaciones()

# 11. LISTADOS

print()
gestor.listar_estudiantes()
gestor.listar_docentes()

print("\n--- BÚSQUEDAS ---")
gestor.buscar_estudiante("María")
gestor.buscar_docente("Torres")

# 12. REPORTES (Builder pattern)

print("\n--- REPORTES CON BUILDER ---")
gestor.generar_reporte_calificaciones(est1)
gestor.generar_reporte_calificaciones(est2)
gestor.generar_reporte_docente(docente1)
gestor.generar_reporte_sede(sede_manta)

gestor.listar_todos_reportes()

# 13. CIERRE DE PERIODO

print("\n--- CIERRE DE PERIODO ---")
gestor.cerrar_periodo(periodo)

# 14. RESUMEN FINAL

gestor.resumen_sistema()
