"""
app_gui.py — Interfaz gráfica SIGEN con Tkinter
Ejecutar desde la raíz del proyecto: python app_gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import date
from io import StringIO
import sys
import json
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATOS_PATH = DATA_DIR / "datos.json"
REPORTES_PATH = DATA_DIR / "reportes.json"

# Modelos:
from models import usuario
from models import docente
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
from models.administrador import Administrador
from models.Sistema_fachada import SistemaFachada


def password_repetida(contrasena):
    usuarios = [*estado.admins, *estado.docentes, *estado.estudiantes]
    return any(usuario.verificar_contrasena(contrasena) for usuario in usuarios)


def validar_password_nueva(contrasena):
    usuario.Usuario.validar_contrasena(contrasena)
    if password_repetida(contrasena):
        raise ValueError("La contraseña ya está en uso por otro usuario.")


# UTILIDAD: capturar prints del sistema en la consola de la GUI

class ConsolaGUI:
    """Redirige stdout a un widget ScrolledText."""

    def __init__(self, widget: scrolledtext.ScrolledText):
        self._widget = widget
        self._original = sys.stdout

    def write(self, text):
        self._widget.configure(state="normal")
        self._widget.insert(tk.END, text)
        self._widget.see(tk.END)
        self._widget.configure(state="disabled")

    def flush(self):
        pass

    def activar(self):
        sys.stdout = self

    def desactivar(self):
        sys.stdout = self._original


# ESTADO GLOBAL DEL SISTEMA (compartido entre todas las pestañas)

class EstadoSistema:
    def __init__(self):
        self.gestor: GestorNivelacion = None
        self.sistema: SistemaFachada = None
        self.admin: Administrador = None
        self.admins: list = []
        self.usuario_actual = None
        self.sedes: list = []
        self.carreras: list = []
        self.docentes: list = []
        self.estudiantes: list = []
        self.asignaturas: list = []
        self.paralelos: list = []
        self.periodos: list = []
        self.ofertas: list = []
        self.modalidades: list = []
        self.horarios: list = []

estado = EstadoSistema()
def guardar_datos():
    datos = {
        "sedes": [s.to_dict() for s in estado.sedes],
        "carreras": [
            {
                "id_carrera": c.id_carrera,
                "nombre_carrera": c.nombre_carrera,
                "facultad": c.facultad,
                "duracion_semestre": c.duracion_semestre,
                "creditos_totales": c.creditos_totales,
                "cupos_totales": c.cupos_totales,
                "sede_id": next((s.id_sede for s in estado.sedes if c in s._carreras), None),
            }
            for c in estado.carreras
        ],
        "docentes": [d.to_dict() for d in estado.docentes],
        "estudiantes": [e.to_dict() for e in estado.estudiantes],
        "asignaturas": [
            {
                "id_asignatura": a.id_asignatura,
                "nombre": a.nombre,
                "contenido": getattr(a, "_contenido", ""),
                "creditos": a.creditos,
                "cupos_maximos": a.cupos_maximos,
                "docente_id": a.docente.id if a.docente else None,
                "carrera_id": next((c.id_carrera for c in estado.carreras if a in c.obtener_asignaturas()), None),
            }
            for a in estado.asignaturas
        ],
        "paralelos": [
            {
                "codigo": p.codigo,
                "capacidad": p.capacidad,
                "docente_id": p.docente.id if p.docente else None,
                "asignatura_id": p.asignatura.id_asignatura if p.asignatura else None,
                "sede_id": next((s.id_sede for s in estado.sedes if p in s._paralelos), None),
                "estudiante_ids": [e.id for e in p.estudiantes],
                "modalidad": {
                    "id_modalidad": p.modalidad.id_modalidad,
                    "tipo": p.modalidad.tipo,
                    "descripcion": p.modalidad.descripcion,
                    "duracion_horas": p.modalidad.duracion_horas,
                },
                "horario": {
                    "id_horario": p.horario.id_horario,
                    "dia": p.horario.dia,
                    "hora_inicio": p.horario.hora_inicio,
                    "hora_fin": p.horario.hora_fin,
                    "aula": p.horario.aula,
                },
            }
            for p in estado.paralelos
        ],
        "ofertas": [
            {
                "id_oferta": o.id_oferta,
                "carrera_id": o.carrera.id_carrera if o.carrera else None,
                "modalidad": {
                    "id_modalidad": o.modalidad.id_modalidad,
                    "tipo": o.modalidad.tipo,
                    "descripcion": o.modalidad.descripcion,
                    "duracion_horas": o.modalidad.duracion_horas,
                },
                "cupos_total": o.cupos_total,
                "cupos_ocupados": o.cupos_ocupados,
                "puntaje_minimo": o.puntaje_minimo,
                "puntaje_maximo": o.puntaje_maximo,
                "fecha_apertura": str(o.fecha_apertura) if o.fecha_apertura else None,
                "fecha_cierre": str(o.fecha_cierre) if o.fecha_cierre else None,
                "sede_id": o.sede.id_sede if o.sede else None,
            }
            for o in estado.ofertas
        ],
    }

    with DATOS_PATH.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

def cargar_datos():
    try:
        ruta_datos = DATOS_PATH if DATOS_PATH.exists() else BASE_DIR / "datos.json"
        with ruta_datos.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        # --- SEDES ---
        for s in datos.get("sedes", []):
            if not any(sede.id_sede == s["id_sede"] for sede in estado.sedes):
                estado.sedes.append(
                    Sede(
                        id_sede=s["id_sede"],
                        nombre_sede=s["nombre_sede"],
                        direccion=s["direccion"],
                        ciudad=s["ciudad"],
                        capacidad_total=s["capacidad_total"]
                    )
                )

        # --- CARRERAS (reconstruye y enlaza con su sede) ---
        for c in datos.get("carreras", []):
            if any(car.id_carrera == c["id_carrera"] for car in estado.carreras):
                continue
            carrera = Carrera(
                id_carrera=c["id_carrera"],
                nombre_carrera=c["nombre_carrera"],
                facultad=c["facultad"],
                duracion_semestre=c["duracion_semestre"],
                creditos_totales=c["creditos_totales"],
                cupos_totales=c["cupos_totales"],
            )
            estado.carreras.append(carrera)

            sede_id = c.get("sede_id")
            if sede_id is not None:
                sede = next((s for s in estado.sedes if s.id_sede == sede_id), None)
                if sede:
                    sede.agregar_carrera(carrera)

        # --- OFERTAS ---
        for o in datos.get("ofertas", []):
            if any(of.id_oferta == o.get("id_oferta") for of in estado.ofertas):
                continue
            carrera = next((c for c in estado.carreras if c.id_carrera == o.get("carrera_id")), None)
            sede = next((s for s in estado.sedes if s.id_sede == o.get("sede_id")), None)
            modalidad_data = o.get("modalidad", "Presencial")
            if isinstance(modalidad_data, dict):
                modalidad = Modalidad.crear(
                    id_modalidad=modalidad_data.get("id_modalidad", o.get("id_oferta")),
                    tipo=modalidad_data.get("tipo", "Presencial"),
                )
            else:
                modalidad = Modalidad.crear(
                    id_modalidad=o.get("id_oferta"),
                    tipo=modalidad_data or "Presencial",
                )
            oferta = Oferta(
                id_oferta=o.get("id_oferta"),
                carrera=carrera,
                modalidad=modalidad,
                cupos_total=int(o.get("cupos_total", 30)),
                cupos_ocupados=int(o.get("cupos_ocupados", 0)),
                puntaje_minimo=float(o.get("puntaje_minimo", 0)),
                puntaje_maximo=float(o.get("puntaje_maximo", 1000)),
                fecha_apertura=o.get("fecha_apertura"),
                fecha_cierre=o.get("fecha_cierre"),
                sede=sede,
            )
            if sede:
                sede.agregar_oferta(oferta)
            estado.ofertas.append(oferta)

        if not datos.get("ofertas") and not estado.ofertas:
            for indice, carrera in enumerate(estado.carreras, start=1):
                sede = next((s for s in estado.sedes if carrera in s._carreras), None)
                oferta = Oferta(
                    id_oferta=indice,
                    carrera=carrera,
                    modalidad=Modalidad.crear(id_modalidad=indice, tipo="Presencial"),
                    cupos_total=max(int(carrera.cupos_totales), 1),
                    cupos_ocupados=0,
                    puntaje_minimo=600,
                    puntaje_maximo=1000,
                    fecha_apertura=date.today(),
                    fecha_cierre=date(date.today().year, 12, 31),
                    sede=sede,
                )
                if sede:
                    sede.agregar_oferta(oferta)
                estado.ofertas.append(oferta)

        # --- DOCENTES (reconstruye y enlaza con su sede) ---
        for d in datos.get("docentes", []):
            if any(doc.id == d["id"] for doc in estado.docentes):
                continue
            docente = Docente(
                id=d["id"],
                nombre=d["nombre"],
                correo=d["correo"],
                contrasena="1234",
                telefono=d["telefono"],
                titulo=d["titulo"],
                especialidad=d["especialidad"],
                nivel=d["nivel"]
            )

            sede_nombre = d.get("sede")
            if sede_nombre:
                sede = next((s for s in estado.sedes if s.nombre_sede == sede_nombre), None)
                if sede:
                    docente._establecer_sede(sede)

            horas = d.get("horas_asignadas", 0)
            if horas:
                docente._agregar_horas(horas)

            estado.docentes.append(docente)

        # --- ESTUDIANTES (reconstruye y enlaza con sede y carrera) ---
        for e in datos.get("estudiantes", []):
            if any(est.id == e["id"] for est in estado.estudiantes):
                continue

            sede = None
            carrera = None

            sede_id = e.get("sede_id")
            if sede_id is not None:
                sede = next((s for s in estado.sedes if s.id_sede == sede_id), None)
            elif e.get("sede"):
                sede = next((s for s in estado.sedes if s.nombre_sede == e["sede"]), None)

            carrera_id = e.get("carrera_id")
            if carrera_id is not None:
                carrera = next((c for c in estado.carreras if c.id_carrera == carrera_id), None)
            elif e.get("carrera"):
                carrera = next((c for c in estado.carreras if c.nombre_carrera == e["carrera"]), None)

            estudiante = Estudiante(
                id=e["id"],
                nombre=e["nombre"],
                correo=e["correo"],
                contrasena="1234",
                telefono=e["telefono"],
                fecha_matricula=date.today(),
                sede=sede,
                carrera=carrera,
                estado_academico=e.get("estado_academico", "Activo"),
            )

            for materia, notas in e.get("calificaciones", {}).items():
                if isinstance(notas, list):
                    for registro in notas:
                        if isinstance(registro, dict):
                            estudiante._registrar_calificacion(
                                materia,
                                float(registro.get("nota", 0)),
                                registro.get("comentario", ""),
                            )
                        else:
                            estudiante._registrar_calificacion(materia, float(registro))
                else:
                    estudiante._registrar_calificacion(materia, float(notas))

            estado.estudiantes.append(estudiante)

        # --- ASIGNATURAS (reconstruye y enlaza con docente y carrera) ---
        for a in datos.get("asignaturas", []):
            if any(asig.id_asignatura == a["id_asignatura"] for asig in estado.asignaturas):
                continue

            asignatura = Asignatura(
                id_asignatura=a["id_asignatura"],
                nombre=a["nombre"],
                contenido=a.get("contenido", ""),
                creditos=int(a.get("creditos", 0)),
            )

            cupos = int(a.get("cupos_maximos", 0) or 0)
            if cupos > 0:
                asignatura.asignar_cupos(cupos)

            docente_id = a.get("docente_id")
            docente = next((d for d in estado.docentes if d.id == docente_id), None)
            if docente:
                asignatura.asignar_docente(docente)

            carrera_id = a.get("carrera_id")
            carrera = next((c for c in estado.carreras if c.id_carrera == carrera_id), None)
            if carrera:
                carrera.agregar_asignatura(asignatura)

            estado.asignaturas.append(asignatura)

        # --- PARALELOS (reconstruye horario, modalidad y asignatura) ---
        for p in datos.get("paralelos", []):
            if any(par.codigo == p["codigo"] for par in estado.paralelos):
                continue

            docente = next((d for d in estado.docentes if d.id == p.get("docente_id")), None)
            asignatura = next((a for a in estado.asignaturas if a.id_asignatura == p.get("asignatura_id")), None)
            if not docente or not asignatura:
                continue

            modalidad_data = p.get("modalidad", {})
            modalidad = Modalidad.crear(
                id_modalidad=modalidad_data.get("id_modalidad", len(estado.modalidades) + 1),
                tipo=modalidad_data.get("tipo", "Presencial"),
            )

            horario_data = p.get("horario", {})
            horario = Horario(
                id_horario=horario_data.get("id_horario", f"H{len(estado.horarios) + 1:03d}"),
                dia=horario_data.get("dia", "Lunes"),
                hora_inicio=horario_data.get("hora_inicio", "07:00"),
                hora_fin=horario_data.get("hora_fin", "09:00"),
                aula=horario_data.get("aula", ""),
            )

            paralelo = Paralelo(
                codigo=p["codigo"],
                capacidad=int(p.get("capacidad", 0)),
                docente=docente,
                horario=horario,
                modalidad=modalidad,
                asignatura=asignatura,
            )

            sede = next((s for s in estado.sedes if s.id_sede == p.get("sede_id")), None)
            if sede:
                sede.agregar_paralelo(paralelo)

            for estudiante_id in p.get("estudiante_ids", []):
                estudiante = next((e for e in estado.estudiantes if e.id == estudiante_id), None)
                if estudiante:
                    paralelo.agregar_estudiante(estudiante)

            estado.paralelos.append(paralelo)
            estado.modalidades.append(modalidad)
            estado.horarios.append(horario)

        print("Datos cargados correctamente.")

    except FileNotFoundError:
        print("No existe datos.json todavía.")

def iniciar_sistema_automatico():
    admins_defecto = [
        {
            "id": 1,
            "nombre": "ADONIS SOLORZANO",
            "correo": "ADONIS@uleam.edu.ec",
            "contrasena": "Admin123",
            "telefono": "0991234567",
            "nivel_autoridad": "Alto",
            "departamento_asignado": "Nivelación"
        },
        {
            "id": 2,
            "nombre": "Anthony Salazar",
            "correo": "anthonysalazar006@gmail.com",
            "contrasena": "Admin123",
            "telefono": "0991234567",
            "nivel_autoridad": "Alto",
            "departamento_asignado": "Nivelación"
        }
    ]

    for datos_admin in admins_defecto:
        correo_admin = datos_admin["correo"].strip().lower()

        existe = any(
            admin.correo.strip().lower() == correo_admin
            for admin in estado.admins
        )

        if not existe:
            estado.admins.append(Administrador(**datos_admin))

    if estado.admin is None and estado.admins:
        estado.admin = estado.admins[0]

    if estado.sistema is None:
        estado.sistema = SistemaFachada(
            "ULEAM - Campus Manta",
            estado.admin,
            ruta_reportes=REPORTES_PATH
        )
        estado.gestor = estado.sistema.gestor

    for sede in estado.sedes:
        estado.sistema.registrar_sede(sede)

    for docente in estado.docentes:
        estado.sistema.registrar_docente(docente)

    for estudiante in estado.estudiantes:
        estado.sistema.registrar_estudiante(estudiante)

    for asignatura in estado.asignaturas:
        estado.sistema.registrar_asignatura(asignatura)

    for paralelo in estado.paralelos:
        estado.sistema.registrar_paralelo(paralelo)

def iniciar_sesion(correo, contrasena):
    correo_ingresado = correo.strip().lower()
    contrasena = contrasena.strip()

    if not correo_ingresado or not contrasena:
        return None

    for admin in estado.admins:
        if admin.correo.strip().lower() == correo_ingresado:
            if admin.iniciar_sesion(admin.correo, contrasena):
                estado.usuario_actual = admin
                return admin

    for docente in estado.docentes:
        if docente.correo.strip().lower() == correo_ingresado:
            if docente.iniciar_sesion(docente.correo, contrasena):
                estado.usuario_actual = docente
                return docente

    for estudiante in estado.estudiantes:
        if estudiante.correo.strip().lower() == correo_ingresado:
            if estudiante.iniciar_sesion(estudiante.correo, contrasena):
                estado.usuario_actual = estudiante
                return estudiante

    return None

def importar_docentes_csv(ruta_archivo):
    importados = 0
    errores = []

    try:
        with open(ruta_archivo, "r", encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo)

            for fila_num, fila in enumerate(lector, start=2):
                try:
                    id_docente = int(fila.get("id", "").strip())
                    nombre = fila.get("nombre", "").strip()
                    correo = fila.get("correo", "").strip()
                    contrasena = fila.get("contrasena", "").strip()
                    telefono = fila.get("telefono", "").strip()
                    titulo = fila.get("titulo", "").strip()
                    especialidad = fila.get("especialidad", "").strip()
                    nivel = fila.get("nivel", "").strip()
                    sede_nombre = fila.get("sede", "").strip()
                    horas = int(fila.get("horas", "0") or 0)

                    if not all([nombre, correo, contrasena, telefono, titulo, especialidad, nivel]):
                        errores.append(f"Fila {fila_num}: campos incompletos.")
                        continue

                    try:
                        validar_password_nueva(contrasena)
                    except ValueError as ex:
                        errores.append(f"Fila {fila_num}: {ex}")
                        continue

                    if any(d.id == id_docente for d in estado.docentes):
                        errores.append(f"Fila {fila_num}: ya existe un docente con ID {id_docente}.")
                        continue

                    if any(d.correo == correo for d in estado.docentes):
                        errores.append(f"Fila {fila_num}: ya existe un docente con correo {correo}.")
                        continue

                    docente = Docente(
                        id=id_docente,
                        nombre=nombre,
                        correo=correo,
                        contrasena=contrasena,
                        telefono=telefono,
                        titulo=titulo,
                        especialidad=especialidad,
                        nivel=nivel,
                    )

                    estado.sistema.registrar_docente(docente)

                    sede = next((s for s in estado.sedes if s.nombre_sede == sede_nombre), None)
                    if sede:
                        estado.sistema.asignar_sede_a_docente(docente, sede)

                    if horas > 0:
                        estado.sistema.asignar_carga_horaria(docente, horas)

                    estado.docentes.append(docente)
                    importados += 1

                except Exception as ex:
                    errores.append(f"Fila {fila_num}: {ex}")

        guardar_datos()
        return importados, errores

    except Exception as ex:
        return 0, [str(ex)]


def importar_estudiantes_csv(ruta_archivo):
    importados = 0
    errores = []

    try:
        with open(ruta_archivo, "r", encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo)

            for fila_num, fila in enumerate(lector, start=2):
                try:
                    id_estudiante = int(fila.get("id", "").strip())
                    nombre = fila.get("nombre", "").strip()
                    correo = fila.get("correo", "").strip()
                    contrasena = fila.get("contrasena", "").strip()
                    telefono = fila.get("telefono", "").strip()
                    sede_nombre = fila.get("sede", "").strip()
                    carrera_nombre = fila.get("carrera", "").strip()

                    if not all([nombre, correo, contrasena, telefono, sede_nombre, carrera_nombre]):
                        errores.append(f"Fila {fila_num}: campos incompletos.")
                        continue

                    try:
                        validar_password_nueva(contrasena)
                    except ValueError as ex:
                        errores.append(f"Fila {fila_num}: {ex}")
                        continue

                    if any(e.id == id_estudiante for e in estado.estudiantes):
                        errores.append(f"Fila {fila_num}: ya existe un estudiante con ID {id_estudiante}.")
                        continue

                    if any(e.correo == correo for e in estado.estudiantes):
                        errores.append(f"Fila {fila_num}: ya existe un estudiante con correo {correo}.")
                        continue

                    sede = next((s for s in estado.sedes if s.nombre_sede == sede_nombre), None)
                    carrera = next((c for c in estado.carreras if c.nombre_carrera == carrera_nombre), None)

                    if not sede:
                        errores.append(f"Fila {fila_num}: no existe la sede '{sede_nombre}'.")
                        continue

                    if not carrera:
                        errores.append(f"Fila {fila_num}: no existe la carrera '{carrera_nombre}'.")
                        continue

                    estudiante = Estudiante(
                        id=id_estudiante,
                        nombre=nombre,
                        correo=correo,
                        contrasena=contrasena,
                        telefono=telefono,
                        fecha_matricula=date.today(),
                        sede=sede,
                        carrera=carrera,
                    )

                    estado.sistema.registrar_estudiante(estudiante)
                    estado.estudiantes.append(estudiante)
                    importados += 1

                except Exception as ex:
                    errores.append(f"Fila {fila_num}: {ex}")

        guardar_datos()
        return importados, errores

    except Exception as ex:
        return 0, [str(ex)]


def importar_matriculas_csv(ruta_archivo):
    importados = 0
    errores = []

    try:
        with open(ruta_archivo, "r", encoding="utf-8-sig", newline="") as archivo:
            muestra = archivo.read(2048)
            archivo.seek(0)
            delimitador = ";" if muestra.count(";") > muestra.count(",") else ","
            lector = csv.DictReader(archivo, delimiter=delimitador)

            for fila_num, fila in enumerate(lector, start=2):
                try:
                    fila = {
                        (clave or "").strip().lower(): (valor or "").strip()
                        for clave, valor in fila.items()
                    }
                    estudiante_ref = (
                        fila.get("estudiante", "")
                        or fila.get("correo", "")
                        or fila.get("id", "")
                    )
                    paralelo_ref = fila.get("paralelo", "")

                    if not estudiante_ref or not paralelo_ref:
                        errores.append(f"Fila {fila_num}: faltan estudiante/correo/id o paralelo.")
                        continue

                    estudiante = next(
                        (
                            e for e in estado.estudiantes
                            if str(e.id) == estudiante_ref
                            or e.correo.lower() == estudiante_ref.lower()
                            or e.nombre.lower() == estudiante_ref.lower()
                        ),
                        None,
                    )
                    paralelo = next((p for p in estado.paralelos if p.codigo == paralelo_ref), None)

                    if not estudiante:
                        errores.append(f"Fila {fila_num}: no existe el estudiante '{estudiante_ref}'.")
                        continue
                    if not paralelo:
                        errores.append(f"Fila {fila_num}: no existe el paralelo '{paralelo_ref}'.")
                        continue
                    if estudiante in paralelo.estudiantes:
                        errores.append(f"Fila {fila_num}: estudiante ya matriculado en '{paralelo.codigo}'.")
                        continue
                    if paralelo.cupo_disponible <= 0:
                        errores.append(f"Fila {fila_num}: paralelo '{paralelo.codigo}' sin cupos.")
                        continue

                    estado.sistema.asignar_estudiante_a_paralelo(estudiante, paralelo)
                    importados += 1

                except Exception as ex:
                    errores.append(f"Fila {fila_num}: {ex}")

        guardar_datos()
        return importados, errores

    except Exception as ex:
        return 0, [str(ex)]

# HELPERS UI

COLORS = {
    "bg": "#1e1e2e",
    "surface": "#2a2a3e",
    "accent": "#7c3aed",
    "accent2": "#6d28d9",
    "text": "#e2e8f0",
    "text2": "#94a3b8",
    "success": "#10b981",
    "error": "#ef4444",
    "warning": "#f59e0b",
    "border": "#3f3f5a",
}

def lbl(parent, text, bold=False, size=10, color=None):
    font = ("Segoe UI", size, "bold" if bold else "normal")
    return tk.Label(
        parent, text=text, font=font,
        bg=COLORS["surface"], fg=color or COLORS["text"]
    )

def entry(parent, width=28, show=None):
    e = tk.Entry(
        parent, width=width, font=("Segoe UI", 10),
        bg=COLORS["bg"], fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief="flat", bd=4,
        show=show or ""
    )
    return e

def btn(parent, text, command, color=None):
    b = tk.Button(
        parent, text=text, command=command,
        font=("Segoe UI", 10, "bold"),
        bg=color or COLORS["accent"],
        fg="white", relief="flat",
        padx=14, pady=6,
        activebackground=COLORS["accent2"],
        activeforeground="white",
        cursor="hand2",
    )
    return b

def combo(parent, values, width=26):
    c = ttk.Combobox(parent, values=values, width=width, state="readonly",
                     font=("Segoe UI", 10))
    return c

def frame(parent, padx=16, pady=12):
    return tk.Frame(parent, bg=COLORS["surface"], padx=padx, pady=pady)

def separador(parent, row=None):
    sep = tk.Frame(parent, bg=COLORS["border"], height=1)

    if row is not None:
        sep.grid(row=row, column=0, columnspan=10, sticky="ew", pady=8)
    else:
        sep.pack(fill="x", pady=8)

def mostrar_texto(titulo, contenido):
    ventana = tk.Toplevel()
    ventana.title(titulo)
    ventana.geometry("650x420")
    ventana.configure(bg=COLORS["bg"])

    texto = scrolledtext.ScrolledText(
        ventana,
        wrap="word",
        bg="#0f0f1a",
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        font=("Courier New", 10),
        relief="flat",
    )
    texto.pack(fill="both", expand=True, padx=12, pady=12)
    texto.insert(tk.END, contenido)
    texto.configure(state="disabled")

def texto_calificaciones(estudiante):
    calificaciones = estudiante.ver_calificaciones()
    if not calificaciones:
        return f"{estudiante.nombre} no tiene calificaciones registradas."

    lineas = [f"Calificaciones de {estudiante.nombre}", ""]
    for materia, notas in calificaciones.items():
        if not isinstance(notas, list):
            notas = [{"nota": float(notas), "comentario": ""}]
        lineas.append(materia)
        for indice, registro in enumerate(notas, start=1):
            nota = float(registro.get("nota", registro) if isinstance(registro, dict) else registro)
            comentario = registro.get("comentario", "") if isinstance(registro, dict) else ""
            estado_nota = "Aprobado" if nota >= 7.0 else "Reprobado"
            detalle = f"  Nota {indice}: {nota:.2f} -> {estado_nota}"
            if comentario:
                detalle += f" | {comentario}"
            lineas.append(detalle)
    lineas.append("")
    lineas.append(f"Promedio actual: {estudiante.promedio:.2f}")
    return "\n".join(lineas)


def paralelos_de_estudiante(estudiante):
    return [paralelo for paralelo in estado.paralelos if estudiante in paralelo.estudiantes]


def texto_horario_estudiante(estudiante):
    paralelos = paralelos_de_estudiante(estudiante)
    if not paralelos:
        return f"{estudiante.nombre} no tiene horarios registrados."

    lineas = [f"Horario de {estudiante.nombre}", ""]
    for paralelo in paralelos:
        asignatura = paralelo.asignatura.nombre if paralelo.asignatura else "Sin asignatura"
        docente = paralelo.docente.nombre if paralelo.docente else "Sin docente"
        modalidad = paralelo.modalidad.tipo if paralelo.modalidad else "Sin modalidad"
        horario = paralelo.horario
        aula = horario.aula or "Sin aula"
        lineas.append(
            f"{horario.dia} {horario.hora_inicio}-{horario.hora_fin} | "
            f"{asignatura} | {paralelo.codigo} | {docente} | {modalidad} | Aula: {aula}"
        )
    return "\n".join(lineas)


# VENTANA PRINCIPAL
class LoginWindow(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Login SIGEN")
        self.configure(bg=COLORS["bg"])
        self.state("zoomed")

        self._mostrar_password = tk.IntVar(value=0)

        self._construir()

    def _construir(self):
        # Fondo principal
        main = tk.Frame(self, bg=COLORS["bg"])
        main.pack(fill="both", expand=True)

        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=2)
        main.grid_rowconfigure(0, weight=1)

        # PANEL IZQUIERDO
        panel_izq = tk.Frame(
            main,
            bg=COLORS["accent"],
            padx=70,
            pady=60
        )
        panel_izq.grid(row=0, column=0, sticky="nsew")

        tk.Label(
            panel_izq,
            text="SIGEN",
            font=("Segoe UI", 44, "bold"),
            bg=COLORS["accent"],
            fg="white"
        ).pack(anchor="w", pady=(80, 8))

        tk.Label(
            panel_izq,
            text="Sistema de Gestión de Nivelación",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["accent"],
            fg="white"
        ).pack(anchor="w")

        tk.Label(
            panel_izq,
            text="Universidad Laica Eloy Alfaro de Manabí",
            font=("Segoe UI", 12),
            bg=COLORS["accent"],
            fg="#e9d5ff"
        ).pack(anchor="w", pady=(8, 35))

        descripcion = (
            "Administra estudiantes, docentes, asignaturas,\n"
            "paralelos, matrículas, calificaciones y reportes\n"
            "desde una sola plataforma académica."
        )

        tk.Label(
            panel_izq,
            text=descripcion,
            font=("Segoe UI", 12),
            bg=COLORS["accent"],
            fg="white",
            justify="left"
        ).pack(anchor="w", pady=(0, 35))

        # Mini tarjetas informativas
        cards = tk.Frame(panel_izq, bg=COLORS["accent"])
        cards.pack(anchor="w", fill="x")

        self._login_card_info(
            cards,
            "Gestión académica",
            "Control de estudiantes, docentes y asignaturas."
        )

        self._login_card_info(
            cards,
            "Reportes",
            "Consulta de calificaciones, sedes y docentes."
        )

        self._login_card_info(
            cards,
            "Acceso por roles",
            "Administrador, docente y estudiante."
        )

        tk.Label(
            panel_izq,
            text="Proyecto POO — SIGEN",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["accent"],
            fg="#ddd6fe"
        ).pack(anchor="w", side="bottom", pady=20)

        # PANEL DERECHO
        panel_der = tk.Frame(
            main,
            bg=COLORS["bg"],
            padx=60,
            pady=60
        )
        panel_der.grid(row=0, column=1, sticky="nsew")

        panel_der.grid_rowconfigure(0, weight=1)
        panel_der.grid_rowconfigure(2, weight=1)
        panel_der.grid_columnconfigure(0, weight=1)

        card_sombra = tk.Frame(
            panel_der,
            bg="#11111f",
            padx=4,
            pady=4
        )
        card_sombra.grid(row=1, column=0)

        card = tk.Frame(
            card_sombra,
            bg=COLORS["surface"],
            padx=42,
            pady=36
        )
        card.pack()

        tk.Label(
            card,
            text="Bienvenido",
            font=("Segoe UI", 24, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text"]
        ).pack(anchor="w")

        tk.Label(
            card,
            text="Ingresa tus credenciales para continuar",
            font=("Segoe UI", 10),
            bg=COLORS["surface"],
            fg=COLORS["text2"]
        ).pack(anchor="w", pady=(4, 26))

        tk.Label(
            card,
            text="Correo electrónico",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text"]
        ).pack(anchor="w", pady=(0, 6))

        self.correo = tk.Entry(
            card,
            width=34,
            font=("Segoe UI", 11),
            bg=COLORS["bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            bd=8
        )
        self.correo.pack(pady=(0, 18), ipady=3)

        tk.Label(
            card,
            text="Contraseña",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text"]
        ).pack(anchor="w", pady=(0, 6))

        self.password = tk.Entry(
            card,
            width=34,
            show="*",
            font=("Segoe UI", 11),
            bg=COLORS["bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            bd=8
        )
        self.password.pack(pady=(0, 10), ipady=3)

        tk.Checkbutton(
            card,
            text="Mostrar contraseña",
            variable=self._mostrar_password,
            command=self._toggle_password,
            font=("Segoe UI", 9),
            bg=COLORS["surface"],
            fg=COLORS["text2"],
            activebackground=COLORS["surface"],
            activeforeground=COLORS["text"],
            selectcolor=COLORS["bg"]
        ).pack(anchor="w", pady=(0, 22))

        tk.Button(
            card,
            text="Ingresar al sistema",
            command=self.login,
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["success"],
            fg="white",
            activebackground=COLORS["accent2"],
            activeforeground="white",
            relief="flat",
            padx=28,
            pady=10,
            cursor="hand2"
        ).pack(fill="x", pady=(0, 18))

        tk.Label(
            card,
            text="Acceso autorizado para administradores, docentes y estudiantes",
            font=("Segoe UI", 8),
            bg=COLORS["surface"],
            fg=COLORS["text2"],
            wraplength=280,
            justify="center"
        ).pack()

        self.correo.focus()
        self.bind("<Return>", lambda event: self.login())

    def _login_card_info(self, parent, titulo, descripcion):
        caja = tk.Frame(
            parent,
            bg="#6d28d9",
            padx=18,
            pady=12
        )
        caja.pack(fill="x", pady=7)

        tk.Label(
            caja,
            text=titulo,
            font=("Segoe UI", 11, "bold"),
            bg="#6d28d9",
            fg="white"
        ).pack(anchor="w")

        tk.Label(
            caja,
            text=descripcion,
            font=("Segoe UI", 9),
            bg="#6d28d9",
            fg="#ede9fe",
            justify="left"
        ).pack(anchor="w", pady=(3, 0))

    def _toggle_password(self):
        if self._mostrar_password.get() == 1:
            self.password.config(show="")
        else:
            self.password.config(show="*")

    def login(self):
        usuario = iniciar_sesion(
            self.correo.get(),
            self.password.get()
        )

        if usuario:
            messagebox.showinfo(
                "Bienvenido",
                f"Hola {usuario.nombre}"
            )

            self.destroy()

            app = AppSIGEN()
            app.mainloop()

        else:
            messagebox.showerror(
                "Error",
                "Correo o contraseña incorrectos"
            )
class AppSIGEN(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SIGEN — Sistema de Gestión de Nivelación")
        self.configure(bg=COLORS["bg"])
        self.state("zoomed")

        self._construir_ui()
    
    def _cerrar_sesion(self):
        confirmar = messagebox.askyesno(
            "Cerrar sesión",
            "¿Deseas cerrar la sesión actual?"
        )

        if not confirmar:
            return

        estado.usuario_actual = None
        self.destroy()

        login = LoginWindow()
        login.mainloop()

    def _construir_ui(self):
        # HEADER SUPERIOR
        header = tk.Frame(self, bg=COLORS["accent"], pady=10)
        header.pack(fill="x")

        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=3)
        header.grid_columnconfigure(2, weight=1)

        usuario = estado.usuario_actual
        nombre_usuario = usuario.nombre if usuario else "Invitado"

        if isinstance(usuario, Docente):
            rol = "Docente"
        elif isinstance(usuario, Estudiante):
            rol = "Estudiante"
        else:
            rol = "Administrador"

        tk.Label(
            header,
            text=f"Usuario: {nombre_usuario} | Rol: {rol}",
            font=("Segoe UI", 9, "bold"),
            bg=COLORS["accent"],
            fg="white",
        ).grid(row=0, column=0, sticky="w", padx=16)

        tk.Label(
            header,
            text="SIGEN — Universidad Laica Eloy Alfaro de Manabí",
            font=("Segoe UI", 15, "bold"),
            bg=COLORS["accent"],
            fg="white",
        ).grid(row=0, column=1)

        tk.Button(
            header,
            text="Cerrar sesión",
            command=self._cerrar_sesion,
            font=("Segoe UI", 9, "bold"),
            bg=COLORS["error"],
            fg="white",
            activebackground="#b91c1c",
            activeforeground="white",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
        ).grid(row=0, column=2, sticky="e", padx=16)

        # CUERPO PRINCIPAL
        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True)

        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # MENÚ LATERAL
        self.menu_lateral = tk.Frame(
            body,
            bg=COLORS["surface"],
            width=210,
            padx=12,
            pady=18
        )
        self.menu_lateral.grid(row=0, column=0, sticky="ns")
        self.menu_lateral.grid_propagate(False)

        tk.Label(
            self.menu_lateral,
            text="MÓDULOS",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text2"]
        ).pack(anchor="w", pady=(0, 14))

        # CONTENIDO DERECHO
        self.contenido = tk.Frame(body, bg=COLORS["bg"])
        self.contenido.grid(row=0, column=1, sticky="nsew")
        self.contenido.grid_rowconfigure(0, weight=1)
        self.contenido.grid_columnconfigure(0, weight=1)

        # Estilo para tablas
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "TablaSIGEN.Treeview",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["bg"],
            rowheight=30,
            font=("Segoe UI", 10),
            borderwidth=0
        )

        style.configure(
            "TablaSIGEN.Treeview.Heading",
            background=COLORS["accent"],
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            padding=8
        )

        style.map(
            "TablaSIGEN.Treeview",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", "white")]
        )

        # Crear pestañas, cada una dentro de su propio contenedor con scrollbar
        self.tabs = {}
        self._contenedores_tabs = {}

        if isinstance(usuario, Docente):
            self._crear_tab_scrollable("Calificar", TabCalificar)
            self._crear_tab_scrollable("Reportes", TabReportes)
            self._crear_tab_scrollable("Resumen", TabResumen)

        elif isinstance(usuario, Estudiante):
            self._crear_tab_scrollable("Mi horario", TabHorarioEstudiante)
            self._crear_tab_scrollable("Mis notas", TabCalificar)
            self._crear_tab_scrollable("Mis reportes", TabReportes)
            self._crear_tab_scrollable("Resumen", TabResumen)

        else:
            self._crear_tab_scrollable("Inicio", TabInicio, self)
            self._crear_tab_scrollable("Sedes", TabSede)
            self._crear_tab_scrollable("Docentes", TabDocentes)
            self._crear_tab_scrollable("Estudiantes", TabEstudiantes)
            self._crear_tab_scrollable("Asignaturas", TabAsignaturas)
            self._crear_tab_scrollable("Paralelos", TabParalelos)
            self._crear_tab_scrollable("Matrícula", TabMatricula)
            self._crear_tab_scrollable("Carreras y Ofertas", TabCarrerasOfertas)
            self._crear_tab_scrollable("Reportes", TabReportes)
            self._crear_tab_scrollable("Resumen", TabResumen)

        self.botones_menu = {}

        for nombre in self.tabs:
            self._contenedores_tabs[nombre].grid(row=0, column=0, sticky="nsew")
            self._crear_boton_menu(nombre)

        primer_tab = list(self.tabs.keys())[0]
        self._mostrar_tab(primer_tab)

    def _crear_tab_scrollable(self, nombre, clase_tab, *args_extra):
        """Crea una pestaña dentro de un Canvas con scrollbar vertical propia,
        para que cada apartado pueda desplazarse sin que la consola tape contenido."""

        contenedor = tk.Frame(self.contenido, bg=COLORS["bg"])

        canvas = tk.Canvas(
            contenedor,
            bg=COLORS["bg"],
            highlightthickness=0,
            bd=0
        )
        scrollbar = ttk.Scrollbar(
            contenedor,
            orient="vertical",
            command=canvas.yview
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tab = clase_tab(canvas, *args_extra)
        ventana_id = canvas.create_window((0, 0), window=tab, anchor="nw")

        def _actualizar_scrollregion(_event=None, canvas=canvas):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _ajustar_ancho(event, canvas=canvas, ventana_id=ventana_id):
            canvas.itemconfig(ventana_id, width=event.width)

        def _en_scroll_mouse(event, canvas=canvas):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _activar_scroll_mouse(_event=None, canvas=canvas, cb=_en_scroll_mouse):
            canvas.bind_all("<MouseWheel>", cb)
            canvas.bind_all("<Button-4>", cb)
            canvas.bind_all("<Button-5>", cb)

        def _desactivar_scroll_mouse(_event=None, canvas=canvas):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        tab.bind("<Configure>", _actualizar_scrollregion)
        canvas.bind("<Configure>", _ajustar_ancho)
        canvas.bind("<Enter>", _activar_scroll_mouse)
        canvas.bind("<Leave>", _desactivar_scroll_mouse)

        self.tabs[nombre] = tab
        self._contenedores_tabs[nombre] = contenedor
        return tab

    def _crear_boton_menu(self, nombre):
        boton = tk.Button(
            self.menu_lateral,
            text=nombre,
            command=lambda n=nombre: self._mostrar_tab(n),
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text2"],
            activebackground=COLORS["accent"],
            activeforeground="white",
            relief="flat",
            anchor="w",
            padx=14,
            pady=10,
            cursor="hand2"
        )

        boton.pack(fill="x", pady=3)
        self.botones_menu[nombre] = boton


    def _mostrar_tab(self, nombre):
        tab = self.tabs[nombre]

        if hasattr(tab, "refrescar"):
            tab.refrescar()

        self._contenedores_tabs[nombre].tkraise()

        for texto, boton in self.botones_menu.items():
            if texto == nombre:
                boton.config(
                    bg=COLORS["accent"],
                    fg="white"
                )
            else:
                boton.config(
                    bg=COLORS["surface"],
                    fg=COLORS["text2"]
                )

# TAB 1 — INICIO / Configurar sistema

class TabInicio(tk.Frame):
    def __init__(self, parent, app: AppSIGEN):
        super().__init__(parent, bg=COLORS["bg"])
        self._app = app
        self._cards = {}
        self._lbl_usuario = None
        self._construir()

    def _construir(self):
        contenedor = tk.Frame(
            self,
            bg=COLORS["surface"],
            padx=35,
            pady=30
        )
        contenedor.pack(fill="both", expand=True, padx=25, pady=25)

        # Encabezado del dashboard
        tk.Label(
            contenedor,
            text="Panel principal SIGEN",
            font=("Segoe UI", 22, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text"]
        ).pack(anchor="w")

        tk.Label(
            contenedor,
            text="Resumen general del Sistema de Gestión de Nivelación",
            font=("Segoe UI", 11),
            bg=COLORS["surface"],
            fg=COLORS["text2"]
        ).pack(anchor="w", pady=(4, 18))

        usuario = estado.usuario_actual
        nombre_usuario = usuario.nombre if usuario else "Invitado"

        if isinstance(usuario, Docente):
            rol = "Docente"
        elif isinstance(usuario, Estudiante):
            rol = "Estudiante"
        else:
            rol = "Administrador"

        self._lbl_usuario = tk.Label(
            contenedor,
            text=f"Usuario actual: {nombre_usuario} | Rol: {rol}",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["success"]
        )
        self._lbl_usuario.pack(anchor="w", pady=(0, 18))
        estado_frame = tk.Frame(
    contenedor,
    bg=COLORS["bg"],
    padx=18,
    pady=10
)
        estado_frame.pack(fill="x", pady=(0, 18))

        self._lbl_estado = tk.Label(
            estado_frame,
            text="",
            font=("Segoe UI", 10),
            bg=COLORS["bg"],
            fg=COLORS["text2"],
            justify="left",
            anchor="w"
        )
        self._lbl_estado.pack(fill="x")

        # Contenedor de tarjetas
        tablero = tk.Frame(contenedor, bg=COLORS["surface"])
        tablero.pack(fill="x", pady=10)

        for i in range(3):
            tablero.grid_columnconfigure(i, weight=1)

        self._crear_card(tablero, "Estudiantes", "0", 0, 0)
        self._crear_card(tablero, "Docentes", "0", 0, 1)
        self._crear_card(tablero, "Asignaturas", "0", 0, 2)

        self._crear_card(tablero, "Paralelos", "0", 1, 0)
        self._crear_card(tablero, "Sedes", "0", 1, 1)
        self._crear_card(tablero, "Carreras", "0", 1, 2)

        tk.Button(
            contenedor,
            text="Actualizar dashboard",
            command=self.refrescar,
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["accent"],
            fg="white",
            activebackground=COLORS["accent2"],
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2"
        ).pack(anchor="e", pady=10)

        self.refrescar()

    def _crear_card(self, parent, titulo, valor, fila, columna):
        card = tk.Frame(
            parent,
            bg=COLORS["bg"],
            padx=22,
            pady=18
        )
        card.grid(
            row=fila,
            column=columna,
            sticky="nsew",
            padx=10,
            pady=10
        )

        tk.Label(
            card,
            text=titulo,
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["bg"],
            fg=COLORS["text2"]
        ).pack(anchor="w")

        lbl_valor = tk.Label(
            card,
            text=valor,
            font=("Segoe UI", 28, "bold"),
            bg=COLORS["bg"],
            fg=COLORS["success"]
        )
        lbl_valor.pack(anchor="w", pady=(8, 0))

        self._cards[titulo] = lbl_valor

    def refrescar(self):
        self._cards["Estudiantes"].config(text=str(len(estado.estudiantes)))
        self._cards["Docentes"].config(text=str(len(estado.docentes)))
        self._cards["Asignaturas"].config(text=str(len(estado.asignaturas)))
        self._cards["Paralelos"].config(text=str(len(estado.paralelos)))
        self._cards["Sedes"].config(text=str(len(estado.sedes)))
        self._cards["Carreras"].config(text=str(len(estado.carreras)))

        texto_estado = (
            f"Institución: {estado.sistema.nombre_institucion if estado.sistema else 'No iniciada'}\n"
            f"Administradores registrados: {len(estado.admins)}\n"
            f"Reportes disponibles: calificaciones, docentes y sedes\n"
            f"Estado: sistema cargado correctamente"
        )

        self._lbl_estado.config(text=texto_estado)


# TAB 2 — SEDES

class TabSede(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._construir()

    def _construir(self):
        lbl(self, "Gestión de Sedes", bold=True, size=12).pack(pady=(16, 8))

        f = frame(self)
        f.pack()

        campos = ["ID Sede", "Nombre", "Dirección", "Ciudad", "Capacidad total"]
        defaults = ["1", "Sede Manta", "Av. Universitaria s/n", "Manta", "500"]
        self._entries = {}
        for i, (c, d) in enumerate(zip(campos, defaults)):
            lbl(f, c).grid(row=i, column=0, sticky="w", pady=4)
            e = entry(f)
            e.insert(0, d)
            e.grid(row=i, column=1, pady=4, padx=8)
            self._entries[c] = e

        btn(f, "➕ Registrar Sede", self._registrar).grid(
            row=len(campos), column=0, columnspan=2, pady=14
        )

        separador(self)
        lbl(self, "Sedes registradas", bold=True).pack()
        self._lista = tk.Listbox(
            self, bg=COLORS["bg"], fg=COLORS["text"],
            font=("Segoe UI", 10), height=8, relief="flat",
            selectbackground=COLORS["accent"],
        )
        self._lista.pack(fill="x", padx=20, pady=6)

    def _registrar(self):
        if not self._validar_sistema(): return
        try:
            id_sede = int(self._entries["ID Sede"].get())
            nombre_sede = self._entries["Nombre"].get().strip()

            if not nombre_sede:
                messagebox.showwarning("Campos incompletos", "Ingresa el nombre de la sede.")
                return

            if any(s.id_sede == id_sede for s in estado.sedes):
                messagebox.showwarning("Duplicado", "Ya existe una sede con ese ID.")
                return

            sede = Sede(
                id_sede=id_sede,
                nombre_sede=nombre_sede,
                direccion=self._entries["Dirección"].get().strip(),
                ciudad=self._entries["Ciudad"].get().strip(),
                capacidad_total=int(self._entries["Capacidad total"].get()),
            )
            estado.sistema.registrar_sede(sede)
            estado.sedes.append(sede)
            guardar_datos()
            self._lista.insert(tk.END, f"  {sede.nombre_sede} — {sede.ciudad} (cap. {sede.capacidad_total})")
            messagebox.showinfo("OK", f"Sede '{sede.nombre_sede}' registrada.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _validar_sistema(self):
        if not estado.sistema:
            messagebox.showwarning("Sistema", "Primero inicia el sistema en la pestaña Inicio.")
            return False
        return True

    def refrescar(self):
        self._lista.delete(0, tk.END)

        for sede in estado.sedes:
            self._lista.insert(
            tk.END,
            f"{sede.nombre_sede} — {sede.ciudad} (cap. {sede.capacidad_total})"
        )


# TAB 3 — DOCENTES

class TabDocentes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._construir()

    def _construir(self):
        lbl(self, "Gestión de Docentes", bold=True, size=12).pack(pady=(16, 8))

        f = frame(self)
        f.pack()

        campos = ["ID", "Nombre", "Correo", "Contraseña", "Teléfono", "Título", "Especialidad", "Nivel"]
        defaults = ["", "", "", "", "", "", "", ""]

        self._entries = {}
        for i, (c, d) in enumerate(zip(campos, defaults)):
            lbl(f, c).grid(row=i, column=0, sticky="w", pady=3)
            e = entry(f, show="*" if c == "Contraseña" else None)
            e.insert(0, d)
            e.grid(row=i, column=1, pady=3, padx=8)
            self._entries[c] = e

        # Sede
        lbl(f, "Sede").grid(row=len(campos), column=0, sticky="w", pady=3)
        self._cb_sede = combo(f, [])
        self._cb_sede.grid(row=len(campos), column=1, pady=3, padx=8)

        # Horas
        lbl(f, "Horas a asignar").grid(row=len(campos)+1, column=0, sticky="w", pady=3)
        self._e_horas = entry(f, width=10)

        self._e_horas.grid(row=len(campos)+1, column=1, sticky="w", pady=3, padx=8)

        btn(f, "➕ Registrar Docente", self._registrar).grid(
            row=len(campos)+2, column=0, columnspan=2, pady=14
        )

        btn(
            f,
            "Importar docentes CSV",
            self._importar_csv,
            color=COLORS["warning"]
        ).grid(row=len(campos)+3, column=0, columnspan=2, pady=6)

        separador(self)
        lbl(self, "Docentes registrados", bold=True).pack()

        columnas = ("id", "nombre", "correo", "especialidad", "sede", "horas")

        self._tabla = ttk.Treeview(
            self,
            columns=columnas,
            show="headings",
            height=7,
            style="TablaSIGEN.Treeview"
        )

        self._tabla.heading("id", text="ID")
        self._tabla.heading("nombre", text="Nombre")
        self._tabla.heading("correo", text="Correo")
        self._tabla.heading("especialidad", text="Especialidad")
        self._tabla.heading("sede", text="Sede")
        self._tabla.heading("horas", text="Horas")

        self._tabla.column("id", width=60, anchor="center")
        self._tabla.column("nombre", width=180)
        self._tabla.column("correo", width=220)
        self._tabla.column("especialidad", width=180)
        self._tabla.column("sede", width=160)
        self._tabla.column("horas", width=80, anchor="center")

        self._tabla.pack(fill="x", padx=20, pady=6)
        self._tabla.tag_configure(
            "fila_par",
            background=COLORS["bg"],
            foreground=COLORS["text"]
        )

        self._tabla.tag_configure(
            "fila_impar",
            background=COLORS["surface"],
            foreground=COLORS["text"]
        )

    def _registrar(self):
        if not self._validar_sistema(): return
        try:
            valores = {campo: self._entries[campo].get().strip() for campo in self._entries}
            if not all(valores.values()):
                messagebox.showwarning("Campos incompletos", "Completa todos los datos del docente.")
                return

            id_docente = int(valores["ID"])
            if any(d.id == id_docente for d in estado.docentes):
                messagebox.showwarning("Duplicado", "Ya existe un docente con ese ID.")
                return
            if any(d.correo == valores["Correo"] for d in estado.docentes):
                messagebox.showwarning("Duplicado", "Ya existe un docente con ese correo.")
                return

            validar_password_nueva(valores["Contraseña"])

            docente = Docente(
                id=id_docente,
                nombre=valores["Nombre"],
                correo=valores["Correo"],
                contrasena=valores["Contraseña"],
                telefono=valores["Teléfono"],
                titulo=valores["Título"],
                especialidad=valores["Especialidad"],
                nivel=valores["Nivel"],
            )
            estado.sistema.registrar_docente(docente)

            # Sede
            sede_sel = self._cb_sede.get()
            sede = next((s for s in estado.sedes if s.nombre_sede == sede_sel), None)
            if sede:
                estado.sistema.asignar_sede_a_docente(docente, sede)

            # Horas
            horas = int(self._e_horas.get() or 0)
            if horas > 0:
                estado.sistema.asignar_carga_horaria(docente, horas)

            estado.docentes.append(docente)
            guardar_datos()
            self.refrescar()
            messagebox.showinfo("OK", f"Docente '{docente.nombre}' registrado.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _importar_csv(self):
        if not self._validar_sistema():
            return

        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de docentes",
            initialdir=DATA_DIR,
            filetypes=[("Archivos CSV", "*.csv")]
        )

        if not ruta:
            return

        importados, errores = importar_docentes_csv(ruta)
        self.refrescar()

        mensaje = f"Docentes importados: {importados}"

        if errores:
            mensaje += "\n\nErrores:\n" + "\n".join(errores[:10])

        messagebox.showinfo("Importación CSV", mensaje)

    def _validar_sistema(self):
        if not estado.sistema:
            messagebox.showwarning("Sistema", "Primero inicia el sistema en la pestaña Inicio.")
            return False
        return True

    def refrescar(self):
        self._cb_sede["values"] = [s.nombre_sede for s in estado.sedes]

        for item in self._tabla.get_children():
            self._tabla.delete(item)

        for i, docente in enumerate(estado.docentes):
            sede = docente.sede.nombre_sede if docente.sede else "Sin sede"
            horas = docente.horas_asignadas

            etiqueta = "fila_par" if i % 2 == 0 else "fila_impar"

            self._tabla.insert(
                "",
                tk.END,
                values=(
                    docente.id,
                    docente.nombre,
                    docente.correo,
                    docente.especialidad,
                    sede,
                    horas
                ),
                tags=(etiqueta,)
            )


# TAB 4 — ESTUDIANTES

class TabEstudiantes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._construir()

    def _construir(self):
        lbl(self, "Gestión de Estudiantes", bold=True, size=12).pack(pady=(16, 8))

        f = frame(self)
        f.pack()

        campos = ["ID", "Nombre", "Correo", "Contraseña", "Teléfono"]
        defaults = ["", "", "", "", ""]
        self._entries = {}
        for i, (c, d) in enumerate(zip(campos, defaults)):
            lbl(f, c).grid(row=i, column=0, sticky="w", pady=3)
            e = entry(f, show="*" if c == "Contraseña" else None)
            e.insert(0, d)
            e.grid(row=i, column=1, pady=3, padx=8)
            self._entries[c] = e

        lbl(f, "Sede").grid(row=5, column=0, sticky="w", pady=3)
        self._cb_sede = combo(f, [])
        self._cb_sede.grid(row=5, column=1, pady=3, padx=8)

        lbl(f, "Carrera").grid(row=6, column=0, sticky="w", pady=3)
        self._cb_carrera = combo(f, [])
        self._cb_carrera.grid(row=6, column=1, pady=3, padx=8)

        btn(f, "➕ Registrar Estudiante", self._registrar).grid(
            row=7, column=0, columnspan=2, pady=14
        )

        btn(
            f,
            "Importar estudiantes CSV",
            self._importar_csv,
            color=COLORS["warning"]
        ).grid(row=8, column=0, columnspan=2, pady=6)

        separador(self)
        lbl(self, "Estudiantes registrados", bold=True).pack()

        columnas = ("id", "nombre", "correo", "carrera", "sede", "estado")

        self._tabla = ttk.Treeview(
            self,
            columns=columnas,
            show="headings",
            height=7,
            style="TablaSIGEN.Treeview"
        )

        self._tabla.heading("id", text="ID")
        self._tabla.heading("nombre", text="Nombre")
        self._tabla.heading("correo", text="Correo")
        self._tabla.heading("carrera", text="Carrera")
        self._tabla.heading("sede", text="Sede")
        self._tabla.heading("estado", text="Estado")

        self._tabla.column("id", width=60, anchor="center")
        self._tabla.column("nombre", width=180)
        self._tabla.column("correo", width=230)
        self._tabla.column("carrera", width=200)
        self._tabla.column("sede", width=160)
        self._tabla.column("estado", width=100, anchor="center")

        self._tabla.pack(fill="x", padx=20, pady=6)

        self._tabla.tag_configure(
            "fila_par",
            background=COLORS["bg"],
            foreground=COLORS["text"]
        )

        self._tabla.tag_configure(
            "fila_impar",
            background=COLORS["surface"],
            foreground=COLORS["text"]
        )

    def _registrar(self):
        if not self._validar_sistema(): return
        try:
            valores = {campo: self._entries[campo].get().strip() for campo in self._entries}
            if not all(valores.values()):
                messagebox.showwarning("Campos incompletos", "Completa todos los datos del estudiante.")
                return

            id_estudiante = int(valores["ID"])
            if any(e.id == id_estudiante for e in estado.estudiantes):
                messagebox.showwarning("Duplicado", "Ya existe un estudiante con ese ID.")
                return
            if any(e.correo == valores["Correo"] for e in estado.estudiantes):
                messagebox.showwarning("Duplicado", "Ya existe un estudiante con ese correo.")
                return

            validar_password_nueva(valores["Contraseña"])

            sede_sel = self._cb_sede.get()
            carrera_sel = self._cb_carrera.get()
            sede = next((s for s in estado.sedes if s.nombre_sede == sede_sel), None)
            carrera = next((c for c in estado.carreras if c.nombre_carrera == carrera_sel), None)

            if not sede or not carrera:
                messagebox.showwarning("Faltan datos", "Selecciona una sede y una carrera.")
                return

            est = Estudiante(
                id=id_estudiante,
                nombre=valores["Nombre"],
                correo=valores["Correo"],
                contrasena=valores["Contraseña"],
                telefono=valores["Teléfono"],
                fecha_matricula=date.today(),
                sede=sede,
                carrera=carrera,
            )
            estado.sistema.registrar_estudiante(est)
            estado.estudiantes.append(est)
            guardar_datos()
            self.refrescar()
            messagebox.showinfo("OK", f"Estudiante '{est.nombre}' registrado.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _importar_csv(self):
        if not self._validar_sistema():
            return

        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de estudiantes",
            initialdir=DATA_DIR,
            filetypes=[("Archivos CSV", "*.csv")]
        )

        if not ruta:
            return

        importados, errores = importar_estudiantes_csv(ruta)
        self.refrescar()

        mensaje = f"Estudiantes importados: {importados}"

        if errores:
            mensaje += "\n\nErrores:\n" + "\n".join(errores[:10])

        messagebox.showinfo("Importación CSV", mensaje)

    def _validar_sistema(self):
        if not estado.sistema:
            messagebox.showwarning("Sistema", "Primero inicia el sistema en la pestaña Inicio.")
            return False
        return True

    def refrescar(self):
        self._cb_sede["values"] = [s.nombre_sede for s in estado.sedes]
        self._cb_carrera["values"] = [c.nombre_carrera for c in estado.carreras]

        for item in self._tabla.get_children():
            self._tabla.delete(item)

        for i, est in enumerate(estado.estudiantes):
            sede = est.sede.nombre_sede if getattr(est, "sede", None) else "Sin sede"
            carrera = est.carrera.nombre_carrera if getattr(est, "carrera", None) else "Sin carrera"
            estado_academico = getattr(est, "estado_academico", "Activo")

            etiqueta = "fila_par" if i % 2 == 0 else "fila_impar"

            self._tabla.insert(
                "",
                tk.END,
                values=(
                    est.id,
                    est.nombre,
                    est.correo,
                    carrera,
                    sede,
                    estado_academico
                ),
                tags=(etiqueta,)
            )


# TAB 5 — ASIGNATURAS

class TabAsignaturas(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._construir()

    def _construir(self):
        lbl(self, "Gestión de Asignaturas", bold=True, size=12).pack(pady=(16, 8))

        f = frame(self)
        f.pack()

        campos = ["ID", "Nombre", "Contenido", "Créditos"]
        defaults = ["A001", "Programación OO", "Clases, herencia, polimorfismo", "4"]
        self._entries = {}
        for i, (c, d) in enumerate(zip(campos, defaults)):
            lbl(f, c).grid(row=i, column=0, sticky="w", pady=3)
            e = entry(f)
            e.insert(0, d)
            e.grid(row=i, column=1, pady=3, padx=8)
            self._entries[c] = e

        lbl(f, "Docente").grid(row=4, column=0, sticky="w", pady=3)
        self._cb_docente = combo(f, [])
        self._cb_docente.grid(row=4, column=1, pady=3, padx=8)

        lbl(f, "Carrera").grid(row=5, column=0, sticky="w", pady=3)
        self._cb_carrera = combo(f, [])
        self._cb_carrera.grid(row=5, column=1, pady=3, padx=8)

        lbl(f, "Cupos").grid(row=6, column=0, sticky="w", pady=3)
        self._e_cupos = entry(f, width=10)
        self._e_cupos.insert(0, "30")
        self._e_cupos.grid(row=6, column=1, sticky="w", pady=3, padx=8)

        btn(f, "➕ Registrar Asignatura", self._registrar).grid(
            row=7, column=0, columnspan=2, pady=14
        )

        separador(self)
        lbl(self, "Asignaturas registradas", bold=True).pack()

        columnas = ("id", "nombre", "creditos", "cupos", "docente", "carrera")

        self._tabla = ttk.Treeview(
            self,
            columns=columnas,
            show="headings",
            height=7,
            style="TablaSIGEN.Treeview"
        )

        self._tabla.heading("id", text="ID")
        self._tabla.heading("nombre", text="Nombre")
        self._tabla.heading("creditos", text="Créditos")
        self._tabla.heading("cupos", text="Cupos")
        self._tabla.heading("docente", text="Docente")
        self._tabla.heading("carrera", text="Carrera")

        self._tabla.column("id", width=80, anchor="center")
        self._tabla.column("nombre", width=220)
        self._tabla.column("creditos", width=90, anchor="center")
        self._tabla.column("cupos", width=90, anchor="center")
        self._tabla.column("docente", width=200)
        self._tabla.column("carrera", width=220)

        self._tabla.pack(fill="x", padx=20, pady=6)

        self._tabla.tag_configure(
            "fila_par",
            background=COLORS["bg"],
            foreground=COLORS["text"]
        )

        self._tabla.tag_configure(
            "fila_impar",
            background=COLORS["surface"],
            foreground=COLORS["text"]
        )

        separador(self)
        lbl(self, "Estudiantes registrados por materia", bold=True).pack()

        columnas_matriculas = ("materia", "paralelo", "estudiante", "carrera", "docente", "horario")
        self._tabla_por_materia = ttk.Treeview(
            self,
            columns=columnas_matriculas,
            show="headings",
            height=6,
            style="TablaSIGEN.Treeview"
        )

        encabezados_matriculas = (
            ("materia", "Asignatura", 190),
            ("paralelo", "Paralelo", 90),
            ("estudiante", "Estudiante", 170),
            ("carrera", "Carrera", 190),
            ("docente", "Docente", 160),
            ("horario", "Horario", 170),
        )
        for columna, titulo, ancho in encabezados_matriculas:
            self._tabla_por_materia.heading(columna, text=titulo)
            self._tabla_por_materia.column(columna, width=ancho, anchor="w")

        self._tabla_por_materia.pack(fill="x", padx=20, pady=6)
        self._tabla_por_materia.tag_configure(
            "fila_par",
            background=COLORS["bg"],
            foreground=COLORS["text"]
        )
        self._tabla_por_materia.tag_configure(
            "fila_impar",
            background=COLORS["surface"],
            foreground=COLORS["text"]
        )

    def _registrar(self):
        if not self._validar_sistema(): return
        try:
            id_asignatura = self._entries["ID"].get().strip()
            nombre_asignatura = self._entries["Nombre"].get().strip()
            contenido = self._entries["Contenido"].get().strip()

            if not all([id_asignatura, nombre_asignatura, contenido, self._entries["Créditos"].get().strip()]):
                messagebox.showwarning("Campos incompletos", "Completa todos los datos de la asignatura.")
                return

            if any(a.id_asignatura == id_asignatura for a in estado.asignaturas):
                messagebox.showwarning("Duplicado", "Ya existe una asignatura con ese ID.")
                return
            if any(a.nombre == nombre_asignatura for a in estado.asignaturas):
                messagebox.showwarning("Duplicado", "Ya existe una asignatura con ese nombre.")
                return

            asig = Asignatura(
                id_asignatura=id_asignatura,
                nombre=nombre_asignatura,
                contenido=contenido,
                creditos=int(self._entries["Créditos"].get()),
            )
            cupos = int(self._e_cupos.get() or 0)
            if cupos > 0:
                asig.asignar_cupos(cupos)

            docente_sel = self._cb_docente.get()
            docente = next((d for d in estado.docentes if d.nombre == docente_sel), None)
            if docente:
                estado.sistema.asignar_docente_a_asignatura(docente, asig)

            carrera_sel = self._cb_carrera.get()
            carrera = next((c for c in estado.carreras if c.nombre_carrera == carrera_sel), None)
            if carrera:
                carrera.agregar_asignatura(asig)

            estado.sistema.registrar_asignatura(asig)
            estado.asignaturas.append(asig)
            guardar_datos()
            self.refrescar()
            messagebox.showinfo("OK", f"Asignatura '{asig.nombre}' registrada.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _validar_sistema(self):
        if not estado.sistema:
            messagebox.showwarning("Sistema", "Primero inicia el sistema en la pestaña Inicio.")
            return False
        return True

    def refrescar(self):
        self._cb_docente["values"] = [d.nombre for d in estado.docentes]
        self._cb_carrera["values"] = [c.nombre_carrera for c in estado.carreras]

        for item in self._tabla.get_children():
            self._tabla.delete(item)
        self._tabla_por_materia.delete(*self._tabla_por_materia.get_children())

        for i, asig in enumerate(estado.asignaturas):
            docente = asig.docente.nombre if asig.docente else "Sin docente"
            cupos = asig.cupos_maximos

            carrera = next(
                (
                    c.nombre_carrera
                    for c in estado.carreras
                    if asig in c.obtener_asignaturas()
                ),
                "Sin carrera"
            )

            etiqueta = "fila_par" if i % 2 == 0 else "fila_impar"

            self._tabla.insert(
                "",
                tk.END,
                values=(
                    asig.id_asignatura,
                    asig.nombre,
                    asig.creditos,
                    cupos,
                    docente,
                    carrera
                ),
                tags=(etiqueta,)
            )

        fila = 0
        for asig in estado.asignaturas:
            paralelos = [p for p in estado.paralelos if p.asignatura == asig]
            if not paralelos:
                etiqueta = "fila_par" if fila % 2 == 0 else "fila_impar"
                docente = asig.docente.nombre if asig.docente else "Sin docente"
                self._tabla_por_materia.insert(
                    "",
                    tk.END,
                    values=(asig.nombre, "Sin paralelo", "Sin estudiantes", "Sin carrera", docente, "Sin horario"),
                    tags=(etiqueta,)
                )
                fila += 1
                continue

            for paralelo in paralelos:
                docente = paralelo.docente.nombre if paralelo.docente else "Sin docente"
                horario = paralelo.horario
                texto_horario = f"{horario.dia} {horario.hora_inicio}-{horario.hora_fin} | {horario.aula or 'Sin aula'}"
                if paralelo.estudiantes:
                    for estudiante in paralelo.estudiantes:
                        carrera = estudiante.carrera.nombre_carrera if estudiante.carrera else "Sin carrera"
                        etiqueta = "fila_par" if fila % 2 == 0 else "fila_impar"
                        self._tabla_por_materia.insert(
                            "",
                            tk.END,
                            values=(asig.nombre, paralelo.codigo, estudiante.nombre, carrera, docente, texto_horario),
                            tags=(etiqueta,)
                        )
                        fila += 1
                else:
                    etiqueta = "fila_par" if fila % 2 == 0 else "fila_impar"
                    self._tabla_por_materia.insert(
                        "",
                        tk.END,
                        values=(asig.nombre, paralelo.codigo, "Sin estudiantes", "Sin carrera", docente, texto_horario),
                        tags=(etiqueta,)
                    )
                    fila += 1


# TAB 6 — PARALELOS

class TabParalelos(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._construir()

    def _construir(self):
        lbl(self, "Gestión de Paralelos", bold=True, size=12).pack(pady=(16, 8))

        f = frame(self)
        f.pack()

        # Crear Modalidad inline
        lbl(f, "Código paralelo").grid(row=0, column=0, sticky="w", pady=3)
        self._e_codigo = entry(f)
        self._e_codigo.insert(0, "SIS-A")
        self._e_codigo.grid(row=0, column=1, pady=3, padx=8)

        lbl(f, "Capacidad").grid(row=1, column=0, sticky="w", pady=3)
        self._e_cap = entry(f, width=10)
        self._e_cap.insert(0, "30")
        self._e_cap.grid(row=1, column=1, sticky="w", pady=3, padx=8)

        lbl(f, "Docente").grid(row=2, column=0, sticky="w", pady=3)
        self._cb_docente = combo(f, [])
        self._cb_docente.grid(row=2, column=1, pady=3, padx=8)

        lbl(f, "Modalidad").grid(row=3, column=0, sticky="w", pady=3)
        self._cb_modalidad = combo(f, ["Presencial", "Virtual", "Híbrida", "Semipresencial"])
        self._cb_modalidad.current(0)
        self._cb_modalidad.grid(row=3, column=1, pady=3, padx=8)

        lbl(f, "Día").grid(row=4, column=0, sticky="w", pady=3)
        self._cb_dia = combo(f, ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"])
        self._cb_dia.current(0)
        self._cb_dia.grid(row=4, column=1, pady=3, padx=8)

        lbl(f, "Hora inicio").grid(row=5, column=0, sticky="w", pady=3)
        self._e_hi = entry(f, width=10)
        self._e_hi.insert(0, "07:00")
        self._e_hi.grid(row=5, column=1, sticky="w", pady=3, padx=8)

        lbl(f, "Hora fin").grid(row=6, column=0, sticky="w", pady=3)
        self._e_hf = entry(f, width=10)
        self._e_hf.insert(0, "09:00")
        self._e_hf.grid(row=6, column=1, sticky="w", pady=3, padx=8)

        lbl(f, "Aula").grid(row=7, column=0, sticky="w", pady=3)
        self._e_aula = entry(f)
        self._e_aula.insert(0, "Aula 101")
        self._e_aula.grid(row=7, column=1, pady=3, padx=8)

        lbl(f, "Sede").grid(row=8, column=0, sticky="w", pady=3)
        self._cb_sede = combo(f, [])
        self._cb_sede.grid(row=8, column=1, pady=3, padx=8)

        lbl(f, "Asignatura").grid(row=9, column=0, sticky="w", pady=3)
        self._cb_asignatura = combo(f, [])
        self._cb_asignatura.grid(row=9, column=1, pady=3, padx=8)

        btn(f, "➕ Crear Paralelo", self._registrar).grid(
            row=10, column=0, columnspan=2, pady=14
        )

        separador(self)
        acciones = frame(self)
        acciones.pack(pady=4)

        lbl(acciones, "Cupos extra").grid(row=0, column=0, sticky="w", pady=12)
        self._e_cupos_extra = entry(acciones, width=10)
        self._e_cupos_extra.insert(0, "5")
        self._e_cupos_extra.grid(row=0, column=1, sticky="w", pady=12, padx=8)
        btn(acciones, "Agregar cupos", self._agregar_cupos_extra, color=COLORS["success"]).grid(
            row=0, column=2, padx=12, pady=12
        )

        lbl(acciones, "Nuevo docente").grid(row=1, column=0, sticky="w", pady=12)
        self._cb_docente_reasignar = combo(acciones, [])
        self._cb_docente_reasignar.grid(row=1, column=1, pady=12, padx=8)
        btn(acciones, "Reasignar docente", self._reasignar_docente, color=COLORS["warning"]).grid(
            row=1, column=2, padx=12, pady=12
        )

        lbl(acciones, "Paralelo").grid(row=2, column=0, sticky="w", pady=12)
        self._cb_paralelo_accion = combo(acciones, [], width=34)
        self._cb_paralelo_accion.grid(row=2, column=1, columnspan=2, sticky="w", pady=12, padx=8)

        btn(acciones, "Ver estudiantes del paralelo", self._ver_estudiantes_paralelo, color=COLORS["accent"]).grid(
            row=3, column=0, columnspan=3, pady=(18, 8)
        )

        separador(self)
        lbl(self, "Paralelos registrados", bold=True).pack()
        self._lista = tk.Listbox(
            self, bg=COLORS["bg"], fg=COLORS["text"],
            font=("Segoe UI", 10), height=5, relief="flat",
            selectbackground=COLORS["accent"],
        )
        self._lista.pack(fill="x", padx=20, pady=6)
        self._lista.bind("<<ListboxSelect>>", self._sincronizar_paralelo_seleccionado)

    def _registrar(self):
        if not self._validar_sistema(): return
        try:
            codigo = self._e_codigo.get().strip()
            if not codigo:
                messagebox.showwarning("Campos incompletos", "Ingresa el código del paralelo.")
                return
            if any(p.codigo == codigo for p in estado.paralelos):
                messagebox.showwarning("Duplicado", "Ya existe un paralelo con ese código.")
                return

            docente_sel = self._cb_docente.get()
            docente = next((d for d in estado.docentes if d.nombre == docente_sel), None)
            if not docente:
                messagebox.showwarning("Faltan datos", "Selecciona un docente.")
                return

            asignatura_sel = self._cb_asignatura.get()
            asignatura = next((a for a in estado.asignaturas if a.nombre == asignatura_sel), None)
            if not asignatura:
                messagebox.showwarning("Faltan datos", "Selecciona una asignatura.")
                return

            modalidad = Modalidad.crear(
                id_modalidad=len(estado.paralelos)+1,
                tipo=self._cb_modalidad.get(),
            )
            horario = Horario(
                id_horario=f"H{len(estado.paralelos)+1:03d}",
                dia=self._cb_dia.get(),
                hora_inicio=self._e_hi.get(),
                hora_fin=self._e_hf.get(),
                aula=self._e_aula.get(),
            )
            paralelo = Paralelo(
                codigo=codigo,
                capacidad=int(self._e_cap.get()),
                docente=docente,
                horario=horario,
                modalidad=modalidad,
                asignatura=asignatura,
            )
            estado.sistema.registrar_paralelo(paralelo)

            sede_sel = self._cb_sede.get()
            sede = next((s for s in estado.sedes if s.nombre_sede == sede_sel), None)
            if sede:
                sede.agregar_paralelo(paralelo)

            estado.paralelos.append(paralelo)
            estado.modalidades.append(modalidad)
            estado.horarios.append(horario)
            guardar_datos()
            self._lista.insert(tk.END, f"  {paralelo.codigo} — {asignatura.nombre} | {docente.nombre} | {horario.dia} {horario.hora_inicio}-{horario.hora_fin}")
            self.refrescar()
            self._cb_paralelo_accion.set(self._texto_paralelo_detallado(paralelo))
            messagebox.showinfo("OK", f"Paralelo '{paralelo.codigo}' creado.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _paralelo_de_lista(self):
        seleccion_combo = self._cb_paralelo_accion.get()
        for texto, paralelo in getattr(self, "_opciones_paralelo_accion", []):
            if texto == seleccion_combo:
                return paralelo

        return self._paralelo_desde_lista()

    def _paralelo_desde_lista(self):
        seleccion = self._lista.curselection()
        if not seleccion:
            return None
        texto = self._lista.get(seleccion[0]).strip()
        codigo = texto.split(" ")[0]
        return next((p for p in estado.paralelos if p.codigo == codigo), None)

    def _sincronizar_paralelo_seleccionado(self, _event=None):
        paralelo = self._paralelo_desde_lista()
        if paralelo:
            self._cb_paralelo_accion.set(self._texto_paralelo_detallado(paralelo))

    def _texto_paralelo_detallado(self, paralelo):
        asignatura = paralelo.asignatura.nombre if paralelo.asignatura else "Sin asignatura"
        horario = paralelo.horario
        return (
            f"{paralelo.codigo} — {asignatura} | {paralelo.docente.nombre} | "
            f"{horario.dia} {horario.hora_inicio}-{horario.hora_fin}"
        )

    def _agregar_cupos_extra(self):
        if not self._validar_sistema(): return
        try:
            paralelo = self._paralelo_de_lista()
            if not paralelo:
                messagebox.showwarning("Paralelo", "Selecciona un paralelo de la lista.")
                return
            cantidad = int(self._e_cupos_extra.get() or 0)
            estado.sistema.aumentar_cupos_paralelo(paralelo, cantidad)
            guardar_datos()
            self.refrescar()
            messagebox.showinfo("OK", f"Se agregaron {cantidad} cupos a '{paralelo.codigo}'.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _reasignar_docente(self):
        if not self._validar_sistema(): return
        try:
            paralelo = self._paralelo_de_lista()
            docente = next((d for d in estado.docentes if d.nombre == self._cb_docente_reasignar.get()), None)
            if not paralelo or not docente:
                messagebox.showwarning("Faltan datos", "Selecciona un paralelo y un docente.")
                return
            if not messagebox.askyesno("Reasignar docente", f"Reasignar '{paralelo.codigo}' a {docente.nombre}?"):
                return
            estado.sistema.reasignar_docente_paralelo(paralelo, docente)
            guardar_datos()
            self.refrescar()
            messagebox.showinfo("OK", f"Docente reasignado en '{paralelo.codigo}'.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _ver_estudiantes_paralelo(self):
        paralelo = self._paralelo_de_lista()
        if not paralelo:
            messagebox.showwarning("Paralelo", "Selecciona un paralelo de la lista.")
            return
        materia = paralelo.asignatura.nombre if paralelo.asignatura else "Sin asignatura"
        lineas = [
            f"Paralelo: {paralelo.codigo}",
            f"Asignatura: {materia}",
            f"Docente: {paralelo.docente.nombre if paralelo.docente else 'Sin docente'}",
            f"Cupos: {paralelo.cupo_disponible}/{paralelo.capacidad}",
            "",
            "Estudiantes:",
        ]
        if paralelo.estudiantes:
            for indice, estudiante in enumerate(paralelo.estudiantes, start=1):
                lineas.append(f"{indice}. {estudiante.nombre} | {estudiante.correo}")
        else:
            lineas.append("No hay estudiantes registrados.")
        mostrar_texto("Estudiantes del paralelo", "\n".join(lineas))

    def _validar_sistema(self):
        if not estado.sistema:
            messagebox.showwarning("Sistema", "Primero inicia el sistema en la pestaña Inicio.")
            return False
        return True

    def refrescar(self):
        self._cb_docente["values"] = [d.nombre for d in estado.docentes]
        self._cb_docente_reasignar["values"] = [d.nombre for d in estado.docentes]
        self._cb_sede["values"] = [s.nombre_sede for s in estado.sedes]
        self._cb_asignatura["values"] = [a.nombre for a in estado.asignaturas]
        self._opciones_paralelo_accion = [
            (self._texto_paralelo_detallado(paralelo), paralelo)
            for paralelo in estado.paralelos
        ]
        self._cb_paralelo_accion["values"] = [
            texto for texto, _paralelo in self._opciones_paralelo_accion
        ]
        if self._opciones_paralelo_accion and not self._cb_paralelo_accion.get():
            self._cb_paralelo_accion.set(self._opciones_paralelo_accion[0][0])

        self._lista.delete(0, tk.END)
        for paralelo in estado.paralelos:
            asignatura = paralelo.asignatura.nombre if paralelo.asignatura else "Sin asignatura"
            horario = paralelo.horario
            self._lista.insert(
                tk.END,
                f"{paralelo.codigo} — {asignatura} | {paralelo.docente.nombre} | Cupos {paralelo.cupo_disponible}/{paralelo.capacidad} | {horario.dia} {horario.hora_inicio}-{horario.hora_fin}"
            )


# TAB 7 — MATRÍCULA

class TabMatricula(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._construir()

    def _construir(self):
        lbl(self, "Matrícula de Estudiantes", bold=True, size=12).pack(pady=(16, 8))

        f1 = frame(self)
        f1.pack(pady=4)
        lbl(f1, "Asignar a Paralelo", bold=True).grid(row=0, column=0, columnspan=2, pady=(0,8))

        lbl(f1, "Estudiante").grid(row=1, column=0, sticky="w", pady=3)
        self._cb_est_par = combo(f1, [])
        self._cb_est_par.grid(row=1, column=1, pady=3, padx=8)

        lbl(f1, "Paralelo").grid(row=2, column=0, sticky="w", pady=3)
        self._cb_par = combo(f1, [])
        self._cb_par.grid(row=2, column=1, pady=3, padx=8)

        btn(f1, "✅ Matricular en Paralelo", self._matricular_paralelo).grid(
            row=3, column=0, columnspan=2, pady=10
        )

        btn(f1, "Importar matrículas CSV", self._importar_matriculas_csv, color=COLORS["warning"]).grid(
            row=4, column=0, columnspan=2, pady=(0, 10)
        )

        btn(f1, "Retirar del paralelo", self._retirar_paralelo, color=COLORS["error"]).grid(
            row=5, column=0, columnspan=2, pady=(0, 10)
        )

        separador(self)
        lbl(self, "Matrículas registradas", bold=True).pack()

        columnas = ("estudiante", "carrera", "paralelo", "materia")
        self._tabla_matriculas = ttk.Treeview(
            self,
            columns=columnas,
            show="headings",
            height=7,
            style="TablaSIGEN.Treeview",
        )
        for col, titulo in zip(columnas, ("Estudiante", "Carrera", "Paralelo", "Materia")):
            self._tabla_matriculas.heading(col, text=titulo)
            self._tabla_matriculas.column(col, width=160, anchor="w")
        self._tabla_matriculas.pack(fill="x", padx=20, pady=6)
        self._tabla_matriculas.tag_configure(
            "fila_par",
            background=COLORS["bg"],
            foreground=COLORS["text"],
        )
        self._tabla_matriculas.tag_configure(
            "fila_impar",
            background=COLORS["surface"],
            foreground=COLORS["text"],
        )

    def _matricular_paralelo(self):
        if not self._validar_sistema(): return
        try:
            est_n = self._cb_est_par.get()
            est = next((e for e in estado.estudiantes if e.nombre == est_n), None)
            par = self._paralelo_seleccionado()
            if not est or not par:
                messagebox.showwarning("Faltan datos", "Selecciona estudiante y paralelo.")
                return
            if not messagebox.askyesno("Confirmar matrícula", "¿Estás seguro de realizar esta acción?"):
                return
            estado.sistema.asignar_estudiante_a_paralelo(est, par)
            guardar_datos()
            self.refrescar()
            self._limpiar_seleccion()
            messagebox.showinfo("OK", f"'{est.nombre}' matriculado en paralelo '{par.codigo}'.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _retirar_paralelo(self):
        if not self._validar_sistema(): return
        try:
            est_n = self._cb_est_par.get()
            est = next((e for e in estado.estudiantes if e.nombre == est_n), None)
            par = self._paralelo_seleccionado()
            if not est or not par:
                messagebox.showwarning("Faltan datos", "Selecciona estudiante y paralelo.")
                return
            if est not in par.estudiantes:
                messagebox.showwarning("Matrícula", "El estudiante no pertenece a ese paralelo.")
                return
            if not messagebox.askyesno("Retirar estudiante", f"¿Retirar a '{est.nombre}' de '{par.codigo}'?"):
                return
            estado.sistema.retirar_estudiante_de_paralelo(est, par)
            guardar_datos()
            self.refrescar()
            self._limpiar_seleccion()
            messagebox.showinfo("OK", f"'{est.nombre}' fue retirado de '{par.codigo}'.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _texto_paralelo(self, paralelo):
        materia = paralelo.asignatura.nombre if paralelo.asignatura else "Sin asignatura"
        return f"{paralelo.codigo} | {materia} | Cupos {paralelo.cupo_disponible}/{paralelo.capacidad}"

    def _paralelo_seleccionado(self):
        seleccion = self._cb_par.get()
        for texto, paralelo in getattr(self, "_opciones_paralelo", []):
            if texto == seleccion:
                return paralelo
        return next((p for p in estado.paralelos if p.codigo == seleccion), None)

    def _importar_matriculas_csv(self):
        if not self._validar_sistema(): return
        if not messagebox.askyesno("Confirmar matrícula", "¿Estás seguro de realizar esta acción?"):
            return
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de matrículas",
            initialdir=DATA_DIR,
            filetypes=[("Archivos CSV", "*.csv")]
        )
        if not ruta:
            return
        importados, errores = importar_matriculas_csv(ruta)
        self.refrescar()
        mensaje = f"Matrículas importadas: {importados}"
        if errores:
            mensaje += "\n\nErrores:\n" + "\n".join(errores[:10])
        messagebox.showinfo("Importación CSV", mensaje)

    def _limpiar_seleccion(self):
        self._cb_est_par.set("")
        self._cb_par.set("")

    def _validar_sistema(self):
        if not estado.sistema:
            messagebox.showwarning("Sistema", "Primero inicia el sistema en la pestaña Inicio.")
            return False
        return True

    def refrescar(self):
        self._cb_est_par["values"] = [e.nombre for e in estado.estudiantes]
        self._opciones_paralelo = [(self._texto_paralelo(p), p) for p in estado.paralelos]
        self._cb_par["values"] = [texto for texto, _ in self._opciones_paralelo]
        self._tabla_matriculas.delete(*self._tabla_matriculas.get_children())
        fila = 0
        for paralelo in estado.paralelos:
            materia = paralelo.asignatura.nombre if paralelo.asignatura else "Sin asignatura"
            for estudiante in paralelo.estudiantes:
                carrera = estudiante.carrera.nombre_carrera if estudiante.carrera else "Sin carrera"
                etiqueta = "fila_par" if fila % 2 == 0 else "fila_impar"
                self._tabla_matriculas.insert(
                    "",
                    tk.END,
                    values=(estudiante.nombre, carrera, paralelo.codigo, materia),
                    tags=(etiqueta,),
                )
                fila += 1


class TabCarrerasOfertas(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._construir()

    def _construir(self):
        lbl(self, "Carreras y Ofertas", bold=True, size=12).pack(pady=(16, 8))

        lbl(self, "📋 Registrar Carrera y Oferta", bold=True).pack(pady=(4, 6))
        f1 = frame(self)
        f1.pack(pady=4)

        lbl(f1, "ID Carrera").grid(row=0, column=0, sticky="w", pady=3)
        self._e_id_car = entry(f1, width=10)
        self._e_id_car.insert(0, "1")
        self._e_id_car.grid(row=0, column=1, sticky="w", pady=3, padx=8)

        lbl(f1, "Nombre de la carrera").grid(row=1, column=0, sticky="w", pady=3)
        self._e_nom_car = entry(f1)
        self._e_nom_car.insert(0, "Ingeniería en Sistemas")
        self._e_nom_car.grid(row=1, column=1, pady=3, padx=8)

        lbl(f1, "Facultad").grid(row=2, column=0, sticky="w", pady=3)
        self._e_fac = entry(f1)
        self._e_fac.insert(0, "Ciencias Informáticas")
        self._e_fac.grid(row=2, column=1, pady=3, padx=8)

        lbl(f1, "Cupos totales").grid(row=3, column=0, sticky="w", pady=3)
        self._e_cupos_car = entry(f1, width=10)
        self._e_cupos_car.insert(0, "40")
        self._e_cupos_car.grid(row=3, column=1, sticky="w", pady=3, padx=8)

        lbl(f1, "Puntaje mínimo").grid(row=4, column=0, sticky="w", pady=3)
        self._e_pmin = entry(f1, width=10)
        self._e_pmin.insert(0, "600")
        self._e_pmin.grid(row=4, column=1, sticky="w", pady=3, padx=8)

        lbl(f1, "Puntaje máximo").grid(row=5, column=0, sticky="w", pady=3)
        self._e_pmax = entry(f1, width=10)
        self._e_pmax.insert(0, "1000")
        self._e_pmax.grid(row=5, column=1, sticky="w", pady=3, padx=8)

        lbl(f1, "Modalidad").grid(row=6, column=0, sticky="w", pady=3)
        self._cb_modalidad_car = combo(f1, ["Presencial", "Virtual", "Híbrida", "Semipresencial"])
        self._cb_modalidad_car.current(0)
        self._cb_modalidad_car.grid(row=6, column=1, pady=3, padx=8)

        lbl(f1, "Sede").grid(row=7, column=0, sticky="w", pady=3)
        self._cb_sede_car = combo(f1, [])
        self._cb_sede_car.grid(row=7, column=1, pady=3, padx=8)

        btn(
            f1,
            "➕ Crear Carrera y Oferta",
            self._crear_carrera_oferta,
            color=COLORS["warning"],
        ).grid(row=8, column=0, columnspan=2, pady=10)

        separador(self)

        lbl(self, "🎓 Inscribir en Carrera vía Oferta", bold=True).pack(pady=(4, 6))
        f2 = frame(self)
        f2.pack(pady=4)

        lbl(f2, "Estudiante").grid(row=0, column=0, sticky="w", pady=3)
        self._cb_est_car = combo(f2, [])
        self._cb_est_car.grid(row=0, column=1, pady=3, padx=8)

        lbl(f2, "Oferta").grid(row=1, column=0, sticky="w", pady=3)
        self._cb_oferta_car = combo(f2, [])
        self._cb_oferta_car.grid(row=1, column=1, pady=3, padx=8)
        self._ofertas_por_etiqueta = {}

        lbl(f2, "Puntaje obtenido").grid(row=2, column=0, sticky="w", pady=3)
        self._e_puntaje = entry(f2, width=10)
        self._e_puntaje.insert(0, "750")
        self._e_puntaje.grid(row=2, column=1, sticky="w", pady=3, padx=8)

        btn(
            f2,
            "✅ Inscribir en Carrera",
            self._matricular_carrera,
            color=COLORS["success"],
        ).grid(row=3, column=0, columnspan=2, pady=10)

    def _crear_carrera_oferta(self):
        if not self._validar_sistema(): return
        try:
            sede_sel = self._cb_sede_car.get()
            sede = next((s for s in estado.sedes if s.nombre_sede == sede_sel), None)
            carrera = Carrera(
                id_carrera=int(self._e_id_car.get()),
                nombre_carrera=self._e_nom_car.get().strip(),
                facultad=self._e_fac.get().strip(),
                duracion_semestre=8,
                creditos_totales=240,
                cupos_totales=int(self._e_cupos_car.get()),
            )
            if sede:
                sede.agregar_carrera(carrera)
            oferta = Oferta(
                cupos_total=int(self._e_cupos_car.get()),
                cupos_ocupados=0,
                modalidad=Modalidad.crear(
                    id_modalidad=carrera.id_carrera,
                    tipo=self._cb_modalidad_car.get(),
                ),
                puntaje_minimo=float(self._e_pmin.get()),
                puntaje_maximo=float(self._e_pmax.get()),
                fecha_apertura=date.today(),
                fecha_cierre=date(date.today().year, 12, 31),
                sede=sede,
                carrera=carrera,
            )
            if sede:
                sede.agregar_oferta(oferta)
            estado.carreras.append(carrera)
            estado.ofertas.append(oferta)
            guardar_datos()
            self.refrescar()
            messagebox.showinfo("OK", f"Carrera '{carrera.nombre_carrera}' y oferta creadas.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _matricular_carrera(self):
        if not self._validar_sistema(): return
        if not estado.ofertas:
            messagebox.showwarning("Sin ofertas", "Primero crea una carrera y oferta.")
            return
        try:
            est_n = self._cb_est_car.get()
            est = next((e for e in estado.estudiantes if e.nombre == est_n), None)
            if not est:
                messagebox.showwarning("Faltan datos", "Selecciona un estudiante.")
                return
            etiqueta_oferta = self._cb_oferta_car.get()
            oferta = self._ofertas_por_etiqueta.get(etiqueta_oferta)
            if not oferta:
                messagebox.showwarning("Faltan datos", "Selecciona una oferta.")
                return
            if not messagebox.askyesno("Confirmar matrícula", "¿Estás seguro de realizar esta acción?"):
                return
            puntaje = float(self._e_puntaje.get())
            estado.sistema.matricular_en_carrera(est, oferta, puntaje)
            guardar_datos()
            messagebox.showinfo("OK", f"Inscripción procesada para '{est.nombre}'.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _validar_sistema(self):
        if not estado.sistema:
            messagebox.showwarning("Sistema", "Primero inicia el sistema en la pestaña Inicio.")
            return False
        return True

    def refrescar(self):
        self._cb_est_car["values"] = [e.nombre for e in estado.estudiantes]
        self._cb_sede_car["values"] = [s.nombre_sede for s in estado.sedes]

        self._ofertas_por_etiqueta = {
            self._etiqueta_oferta(o): o for o in estado.ofertas
        }
        self._cb_oferta_car["values"] = list(self._ofertas_por_etiqueta.keys())

    @staticmethod
    def _etiqueta_oferta(oferta):
        nombre_carrera = oferta.carrera.nombre_carrera if oferta.carrera else "Sin carrera"
        tipo_modalidad = oferta.modalidad.tipo if oferta.modalidad else "Sin modalidad"
        return (
            f"#{oferta.id_oferta} - {nombre_carrera} - {tipo_modalidad} "
            f"(cupos: {oferta.cupo_disponible}/{oferta.cupos_total})"
        )


# TAB 8 — HORARIO DEL ESTUDIANTE

class TabHorarioEstudiante(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._construir()

    def _construir(self):
        lbl(self, "Mi horario", bold=True, size=12).pack(pady=(16, 8))

        f = frame(self)
        f.pack(fill="x", padx=24, pady=(10, 14))

        estudiante = estado.usuario_actual
        lbl(f, f"Estudiante: {estudiante.nombre}", bold=True, size=11).pack(anchor="w", pady=(0, 8))
        lbl(
            f,
            "Estos son los paralelos en los que estás matriculado.",
            size=10,
            color=COLORS["text2"]
        ).pack(anchor="w")

        columnas = ("dia", "hora", "materia", "paralelo", "docente", "modalidad", "aula")
        self._tabla = ttk.Treeview(
            self,
            columns=columnas,
            show="headings",
            height=8,
            style="TablaSIGEN.Treeview",
        )

        encabezados = (
            ("dia", "Día", 120),
            ("hora", "Hora", 120),
            ("materia", "Materia", 180),
            ("paralelo", "Paralelo", 100),
            ("docente", "Docente", 180),
            ("modalidad", "Modalidad", 130),
            ("aula", "Aula", 120),
        )
        for columna, titulo, ancho in encabezados:
            self._tabla.heading(columna, text=titulo)
            self._tabla.column(columna, width=ancho, anchor="w")

        self._tabla.pack(fill="x", padx=24, pady=8)
        self._tabla.tag_configure("fila_par", background=COLORS["bg"], foreground=COLORS["text"])
        self._tabla.tag_configure("fila_impar", background=COLORS["surface"], foreground=COLORS["text"])

        self._mensaje = lbl(self, "", size=10, color=COLORS["text2"])
        self._mensaje.pack(pady=10)

        btn(
            self,
            "Ver horario en detalle",
            self._ver_horario_detalle,
            color=COLORS["success"]
        ).pack(pady=8)

    def refrescar(self):
        self._tabla.delete(*self._tabla.get_children())
        estudiante = estado.usuario_actual
        if not isinstance(estudiante, Estudiante):
            return

        paralelos = paralelos_de_estudiante(estudiante)
        if not paralelos:
            self._mensaje.config(text="Todavía no tienes paralelos matriculados.")
            return

        self._mensaje.config(text=f"Total de clases registradas: {len(paralelos)}")
        for indice, paralelo in enumerate(paralelos):
            horario = paralelo.horario
            asignatura = paralelo.asignatura.nombre if paralelo.asignatura else "Sin asignatura"
            docente = paralelo.docente.nombre if paralelo.docente else "Sin docente"
            modalidad = paralelo.modalidad.tipo if paralelo.modalidad else "Sin modalidad"
            aula = horario.aula or "Sin aula"
            etiqueta = "fila_par" if indice % 2 == 0 else "fila_impar"
            self._tabla.insert(
                "",
                tk.END,
                values=(
                    horario.dia,
                    f"{horario.hora_inicio}-{horario.hora_fin}",
                    asignatura,
                    paralelo.codigo,
                    docente,
                    modalidad,
                    aula,
                ),
                tags=(etiqueta,),
            )

    def _ver_horario_detalle(self):
        estudiante = estado.usuario_actual
        if isinstance(estudiante, Estudiante):
            mostrar_texto("Mi horario", texto_horario_estudiante(estudiante))


# TAB 9 — CALIFICAR

class TabCalificar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._construir()

    def _construir(self):
        usuario = estado.usuario_actual

        if isinstance(usuario, Estudiante):
            self._construir_vista_estudiante()
        else:
            self._construir_vista_docente_admin()

    def _construir_vista_estudiante(self):
        lbl(self, "Mis calificaciones", bold=True, size=12).pack(pady=(16, 8))

        f = frame(self)
        f.pack(pady=20)

        lbl(
            f,
            f"Estudiante: {estado.usuario_actual.nombre}",
            bold=True,
            size=11
        ).pack(pady=8)

        lbl(
            f,
            "En esta sección puedes consultar tus calificaciones registradas.",
            size=10,
            color=COLORS["text2"]
        ).pack(pady=8)

        btn(
            f,
            "Ver mis calificaciones",
            self._ver_mis_calificaciones,
            color=COLORS["success"]
        ).pack(pady=14)

    def _construir_vista_docente_admin(self):
        usuario = estado.usuario_actual

        if isinstance(usuario, Docente):
            titulo = "Registro de calificaciones - Docente"
        else:
            titulo = "Registro de calificaciones"

        lbl(self, titulo, bold=True, size=12).pack(pady=(16, 8))

        f = frame(self)
        f.pack()

        lbl(f, "Docente").grid(row=0, column=0, sticky="w", pady=4)
        self._cb_docente = combo(f, [])
        self._cb_docente.grid(row=0, column=1, pady=4, padx=8)

        lbl(f, "Estudiante").grid(row=1, column=0, sticky="w", pady=4)
        self._cb_estudiante = combo(f, [])
        self._cb_estudiante.grid(row=1, column=1, pady=4, padx=8)

        lbl(f, "Asignatura").grid(row=2, column=0, sticky="w", pady=4)
        self._cb_asignatura = combo(f, [])
        self._cb_asignatura.grid(row=2, column=1, pady=4, padx=8)

        lbl(f, "Nota (0.0 - 10.0)").grid(row=3, column=0, sticky="w", pady=4)
        self._e_nota = entry(f, width=10)
        self._e_nota.insert(0, "8.5")
        self._e_nota.grid(row=3, column=1, sticky="w", pady=4, padx=8)

        lbl(f, "Comentario (opcional)").grid(row=4, column=0, sticky="w", pady=4)
        self._e_comentario = entry(f, width=28)
        self._e_comentario.grid(row=4, column=1, pady=4, padx=8)

        btn(
            f,
            "Registrar Calificación",
            self._calificar,
            color=COLORS["success"]
        ).grid(row=5, column=0, columnspan=2, pady=14)

        separador(self)

        lbl(self, "Ver calificaciones de estudiante", bold=True).pack(pady=(4, 4))

        f2 = frame(self)
        f2.pack()

        lbl(f2, "Estudiante").grid(row=0, column=0, sticky="w", pady=4)
        self._cb_ver = combo(f2, [])
        self._cb_ver.grid(row=0, column=1, pady=4, padx=8)

        btn(
            f2,
            "Ver Calificaciones",
            self._ver_calificaciones,
            color=COLORS["accent"]
        ).grid(row=1, column=0, columnspan=2, pady=8)

    def _calificar(self):
        if not self._validar_sistema():
            return

        try:
            usuario = estado.usuario_actual

            if isinstance(usuario, Docente):
                docente = usuario
            else:
                doc_n = self._cb_docente.get()
                docente = next((d for d in estado.docentes if d.nombre == doc_n), None)

            est_n = self._cb_estudiante.get()
            asi_n = self._cb_asignatura.get()
            nota = float(self._e_nota.get())
            comentario = self._e_comentario.get().strip() or None

            estudiante = next((e for e in estado.estudiantes if e.nombre == est_n), None)
            asignatura = next((a for a in estado.asignaturas if a.nombre == asi_n), None)

            if not all([docente, estudiante, asignatura]):
                messagebox.showwarning(
                    "Faltan datos",
                    "Selecciona docente, estudiante y asignatura."
                )
                return

            matriculado = any(
                paralelo.asignatura == asignatura and estudiante in paralelo.estudiantes
                for paralelo in estado.paralelos
            )

            if not matriculado:
                messagebox.showwarning(
                    "Matrícula requerida",
                    "El estudiante no está matriculado en un paralelo de esta asignatura."
                )
                return

            estado.sistema.calificar_estudiante(
                docente,
                estudiante,
                asignatura,
                nota,
                comentario
            )
            guardar_datos()

            messagebox.showinfo(
                "OK",
                f"Nota {nota} registrada para '{estudiante.nombre}'."
            )
            mostrar_texto("Calificaciones", texto_calificaciones(estudiante))

        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _ver_calificaciones(self):
        if not self._validar_sistema():
            return

        est_n = self._cb_ver.get()
        est = next((e for e in estado.estudiantes if e.nombre == est_n), None)

        if not est:
            messagebox.showwarning("Faltan datos", "Selecciona un estudiante.")
            return

        mostrar_texto("Calificaciones", texto_calificaciones(est))

    def _ver_mis_calificaciones(self):
        if not self._validar_sistema():
            return

        estudiante = estado.usuario_actual

        if isinstance(estudiante, Estudiante):
            mostrar_texto("Mis calificaciones", texto_calificaciones(estudiante))
        else:
            messagebox.showwarning("Usuario", "Esta opción solo es para estudiantes.")

    def _validar_sistema(self):
        if not estado.sistema:
            messagebox.showwarning("Sistema", "Primero inicia el sistema.")
            return False
        return True

    def refrescar(self):
        usuario = estado.usuario_actual

        if isinstance(usuario, Estudiante):
            return

        if isinstance(usuario, Docente):
            self._cb_docente["values"] = [usuario.nombre]
            self._cb_docente.set(usuario.nombre)
        else:
            self._cb_docente["values"] = [d.nombre for d in estado.docentes]

        self._cb_estudiante["values"] = [e.nombre for e in estado.estudiantes]
        self._cb_asignatura["values"] = [a.nombre for a in estado.asignaturas]
        self._cb_ver["values"] = [e.nombre for e in estado.estudiantes]

# TAB 9 — REPORTES

class TabReportes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._construir()

    def _construir(self):
        usuario = estado.usuario_actual

        if isinstance(usuario, Estudiante):
            self._construir_estudiante()
        elif isinstance(usuario, Docente):
            self._construir_docente()
        else:
            self._construir_admin()

    def _construir_estudiante(self):
        lbl(self, "Mis reportes", bold=True, size=12).pack(pady=(16, 8))

        f = frame(self)
        f.pack(pady=20)

        lbl(
            f,
            f"Estudiante: {estado.usuario_actual.nombre}",
            bold=True,
            size=11
        ).pack(pady=8)

        lbl(
            f,
            "Aquí puedes generar tu reporte de calificaciones.",
            size=10,
            color=COLORS["text2"]
        ).pack(pady=8)

        btn(
            f,
            "Generar reporte de mis calificaciones",
            self._rep_mis_calificaciones,
            color=COLORS["success"]
        ).pack(pady=14)

    def _construir_docente(self):
        lbl(self, "Reporte del docente", bold=True, size=12).pack(pady=(16, 8))

        f = frame(self)
        f.pack(pady=20)

        lbl(
            f,
            f"Docente: {estado.usuario_actual.nombre}",
            bold=True,
            size=11
        ).pack(pady=8)

        lbl(
            f,
            "Aquí puedes generar tu reporte como docente.",
            size=10,
            color=COLORS["text2"]
        ).pack(pady=8)

        btn(
            f,
            "Generar mi reporte docente",
            self._rep_mi_docente,
            color=COLORS["success"]
        ).pack(pady=14)

    def _construir_admin(self):
        lbl(self, "Generación de Reportes", bold=True, size=12).pack(pady=(16, 8))

        f = frame(self)
        f.pack()

        lbl(f, "Reporte de calificaciones - Estudiante").grid(
            row=0, column=0, sticky="w", pady=4
        )
        self._cb_est = combo(f, [])
        self._cb_est.grid(row=0, column=1, pady=4, padx=8)
        btn(f, "Generar", self._rep_calificaciones).grid(row=0, column=2, padx=8)

        lbl(f, "Reporte de docente").grid(row=1, column=0, sticky="w", pady=4)
        self._cb_doc = combo(f, [])
        self._cb_doc.grid(row=1, column=1, pady=4, padx=8)
        btn(f, "Generar", self._rep_docente).grid(row=1, column=2, padx=8)

        lbl(f, "Reporte de sede").grid(row=2, column=0, sticky="w", pady=4)
        self._cb_sede = combo(f, [])
        self._cb_sede.grid(row=2, column=1, pady=4, padx=8)
        btn(f, "Generar", self._rep_sede).grid(row=2, column=2, padx=8)

        btn(
            f,
            "Listar todos los reportes",
            self._listar,
            color=COLORS["warning"]
        ).grid(row=3, column=0, columnspan=3, pady=14)

    def _rep_mis_calificaciones(self):
        if not self._validar_sistema():
            return

        estudiante = estado.usuario_actual

        if isinstance(estudiante, Estudiante):
            reporte = estado.sistema.generar_reporte_calificaciones(estudiante)
            mostrar_texto("Reporte de calificaciones", reporte.contenido_completo)
        else:
            messagebox.showwarning("Usuario", "Esta opción solo es para estudiantes.")

    def _rep_mi_docente(self):
        if not self._validar_sistema():
            return

        docente = estado.usuario_actual

        if isinstance(docente, Docente):
            reporte = estado.sistema.generar_reporte_docente(docente)
            mostrar_texto("Reporte de docente", reporte.contenido_completo)
        else:
            messagebox.showwarning("Usuario", "Esta opción solo es para docentes.")

    def _rep_calificaciones(self):
        if not self._validar_sistema():
            return

        est_n = self._cb_est.get()
        est = next((e for e in estado.estudiantes if e.nombre == est_n), None)

        if not est:
            messagebox.showwarning("Faltan datos", "Selecciona un estudiante.")
            return

        reporte = estado.sistema.generar_reporte_calificaciones(est)
        mostrar_texto("Reporte de calificaciones", reporte.contenido_completo)

    def _rep_docente(self):
        if not self._validar_sistema():
            return

        doc_n = self._cb_doc.get()
        doc = next((d for d in estado.docentes if d.nombre == doc_n), None)

        if not doc:
            messagebox.showwarning("Faltan datos", "Selecciona un docente.")
            return

        reporte = estado.sistema.generar_reporte_docente(doc)
        mostrar_texto("Reporte de docente", reporte.contenido_completo)

    def _rep_sede(self):
        if not self._validar_sistema():
            return

        sede_n = self._cb_sede.get()
        sede = next((s for s in estado.sedes if s.nombre_sede == sede_n), None)

        if not sede:
            messagebox.showwarning("Faltan datos", "Selecciona una sede.")
            return

        reporte = estado.sistema.generar_reporte_sede(sede)
        mostrar_texto("Reporte de sede", reporte.contenido_completo)

    def _listar(self):
        if not self._validar_sistema():
            return

        reportes = estado.sistema.listar_todos_reportes()
        if not reportes:
            messagebox.showinfo("Reportes", "No hay reportes generados todavía.")
            return
        resumen = "\n".join(f"{i}. {reporte}" for i, reporte in enumerate(reportes, start=1))
        mostrar_texto("Reportes generados", resumen)

    def _validar_sistema(self):
        if not estado.sistema:
            messagebox.showwarning("Sistema", "Primero inicia el sistema.")
            return False
        return True

    def refrescar(self):
        usuario = estado.usuario_actual

        if isinstance(usuario, Estudiante):
            return

        if isinstance(usuario, Docente):
            return

        self._cb_est["values"] = [e.nombre for e in estado.estudiantes]
        self._cb_doc["values"] = [d.nombre for d in estado.docentes]
        self._cb_sede["values"] = [s.nombre_sede for s in estado.sedes]


# TAB 10 — RESUMEN


class TabResumen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._construir()

    def _construir(self):
        usuario = estado.usuario_actual

        if isinstance(usuario, Estudiante):
            self._construir_estudiante()
        elif isinstance(usuario, Docente):
            self._construir_docente()
        else:
            self._construir_admin()

    def _construir_estudiante(self):
        lbl(self, "Resumen del estudiante", bold=True, size=12).pack(pady=(16, 8))

        f = frame(self)
        f.pack(pady=20)

        estudiante = estado.usuario_actual

        lbl(f, f"Nombre: {estudiante.nombre}", bold=True, size=11).pack(pady=5)
        lbl(f, f"Correo: {estudiante.correo}", size=10).pack(pady=5)
        lbl(f, f"Estado académico: {getattr(estudiante, 'estado_academico', 'Activo')}", size=10).pack(pady=5)
        lbl(f, f"Promedio: {getattr(estudiante, 'promedio', 0.0)}", size=10).pack(pady=5)

        lbl(f, "Horario:", bold=True, size=10).pack(anchor="w", pady=(12, 4))
        paralelos = paralelos_de_estudiante(estudiante)
        if paralelos:
            for paralelo in paralelos:
                horario = paralelo.horario
                asignatura = paralelo.asignatura.nombre if paralelo.asignatura else "Sin asignatura"
                lbl(
                    f,
                    f"{horario.dia} {horario.hora_inicio}-{horario.hora_fin} | {asignatura} | Aula: {horario.aula or 'Sin aula'}",
                    size=10,
                    color=COLORS["text2"]
                ).pack(anchor="w", pady=2)
        else:
            lbl(
                f,
                "Todavía no tienes horarios registrados.",
                size=10,
                color=COLORS["text2"]
            ).pack(anchor="w", pady=2)

        btn(
            f,
            "Ver mis calificaciones",
            self._ver_mis_calificaciones,
            color=COLORS["success"]
        ).pack(pady=15)

    def _construir_docente(self):
        lbl(self, "Resumen del docente", bold=True, size=12).pack(pady=(16, 8))

        f = frame(self)
        f.pack(pady=20)

        docente = estado.usuario_actual
        sede = docente.sede.nombre_sede if getattr(docente, "sede", None) else "Sin sede asignada"

        lbl(f, f"Nombre: {docente.nombre}", bold=True, size=11).pack(pady=5)
        lbl(f, f"Correo: {docente.correo}", size=10).pack(pady=5)
        lbl(f, f"Especialidad: {docente.especialidad}", size=10).pack(pady=5)
        lbl(f, f"Nivel: {docente.nivel}", size=10).pack(pady=5)
        lbl(f, f"Sede: {sede}", size=10).pack(pady=5)
        lbl(f, f"Horas asignadas: {getattr(docente, 'horas_asignadas', 0)}", size=10).pack(pady=5)

        btn(
            f,
            "Generar mi reporte docente",
            self._reporte_docente,
            color=COLORS["success"]
        ).pack(pady=15)

    def _construir_admin(self):
        lbl(self, "Resumen del Sistema", bold=True, size=12).pack(pady=(16, 8))

        btn(
            self,
            "Actualizar resumen",
            self._actualizar,
            color=COLORS["accent"]
        ).pack(pady=8)

        self._frame_cards = tk.Frame(self, bg=COLORS["bg"])
        self._frame_cards.pack(pady=10)

        self._cards = {}
        items = [
            ("Estudiantes", "estudiantes"),
            ("Docentes", "docentes"),
            ("Asignaturas", "asignaturas"),
            ("Paralelos", "paralelos"),
            ("Sedes", "sedes"),
            ("Carreras", "carreras"),
        ]

        for i, (titulo, key) in enumerate(items):
            card = tk.Frame(
                self._frame_cards,
                bg=COLORS["surface"],
                padx=20,
                pady=16,
                relief="flat"
            )
            card.grid(row=i // 3, column=i % 3, padx=10, pady=10)

            tk.Label(
                card,
                text=titulo,
                font=("Segoe UI", 10, "bold"),
                bg=COLORS["surface"],
                fg=COLORS["text2"]
            ).pack()

            lbl_num = tk.Label(
                card,
                text="0",
                font=("Segoe UI", 22, "bold"),
                bg=COLORS["surface"],
                fg=COLORS["accent"]
            )
            lbl_num.pack()

            self._cards[key] = lbl_num

        separador(self)

        btn(
            self,
            "Resumen completo en consola",
            self._resumen_completo
        ).pack(pady=6)

        btn(
            self,
            "Cerrar periodo activo",
            self._cerrar_periodo,
            color=COLORS["error"]
        ).pack(pady=6)

    def _ver_mis_calificaciones(self):
        if not self._validar_sistema():
            return

        estudiante = estado.usuario_actual

        if isinstance(estudiante, Estudiante):
            mostrar_texto("Mis calificaciones", texto_calificaciones(estudiante))

    def _reporte_docente(self):
        if not self._validar_sistema():
            return

        docente = estado.usuario_actual

        if isinstance(docente, Docente):
            reporte = estado.sistema.generar_reporte_docente(docente)
            mostrar_texto("Reporte de docente", reporte.contenido_completo)

    def _actualizar(self):
        if not hasattr(self, "_cards"):
            return

        self._cards["estudiantes"].config(text=str(len(estado.estudiantes)))
        self._cards["docentes"].config(text=str(len(estado.docentes)))
        self._cards["asignaturas"].config(text=str(len(estado.asignaturas)))
        self._cards["paralelos"].config(text=str(len(estado.paralelos)))
        self._cards["sedes"].config(text=str(len(estado.sedes)))
        self._cards["carreras"].config(text=str(len(estado.carreras)))

    def _resumen_completo(self):
        if not self._validar_sistema():
            return

        estado.sistema.resumen_sistema()

    def _cerrar_periodo(self):
        if not self._validar_sistema():
            return

        if not estado.periodos:
            messagebox.showwarning("Sin periodos", "No hay periodos activos registrados.")
            return

        periodo = estado.periodos[-1]
        estado.sistema.cerrar_periodo(periodo)
        messagebox.showinfo("OK", f"Periodo '{periodo.semestre}' cerrado.")

    def _validar_sistema(self):
        if not estado.sistema:
            messagebox.showwarning("Sistema", "Primero inicia el sistema.")
            return False
        return True

    def refrescar(self):
        usuario = estado.usuario_actual

        if isinstance(usuario, Administrador):
            self._actualizar()


# ENTRY POINT

def main():
    cargar_datos()
    iniciar_sistema_automatico()

    login = LoginWindow()
    login.mainloop()


if __name__ == "__main__":
    main()