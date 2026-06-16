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

# Modelos:
from models import usuario
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
        ]
    }

    with open("datos.json", "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

def cargar_datos():
    try:
        with open("datos.json", "r", encoding="utf-8") as archivo:
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

            for materia, nota in e.get("calificaciones", {}).items():
                estudiante._registrar_calificacion(materia, float(nota))

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
            modalidad = Modalidad(
                id_modalidad=modalidad_data.get("id_modalidad", len(estado.modalidades) + 1),
                tipo=modalidad_data.get("tipo", "Presencial"),
                descripcion=modalidad_data.get("descripcion", "Modalidad del paralelo"),
                duracion_horas=modalidad_data.get("duracion_horas", 2),
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

    if estado.gestor is None:
        estado.gestor = GestorNivelacion(
            "ULEAM - Campus Manta",
            estado.admin
        )

    for sede in estado.sedes:
        estado.gestor.registrar_sede(sede)

    for docente in estado.docentes:
        estado.gestor.registrar_docente(docente)

    for estudiante in estado.estudiantes:
        estado.gestor.registrar_estudiante(estudiante)

    for asignatura in estado.asignaturas:
        estado.gestor.registrar_asignatura(asignatura)

    for paralelo in estado.paralelos:
        estado.gestor.registrar_paralelo(paralelo)

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

                    estado.gestor.registrar_docente(docente)

                    sede = next((s for s in estado.sedes if s.nombre_sede == sede_nombre), None)
                    if sede:
                        estado.gestor.asignar_sede_a_docente(docente, sede)

                    if horas > 0:
                        estado.gestor.asignar_carga_horaria(docente, horas)

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

                    estado.gestor.registrar_estudiante(estudiante)
                    estado.estudiantes.append(estudiante)
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
    for materia, nota in calificaciones.items():
        estado_nota = "Aprobado" if nota >= 7.0 else "Reprobado"
        lineas.append(f"{materia}: {nota:.2f} -> {estado_nota}")
    lineas.append("")
    lineas.append(f"Promedio actual: {estudiante.promedio:.2f}")
    return "\n".join(lineas)


# VENTANA PRINCIPAL
class LoginWindow(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Login SIGEN")
        self.configure(bg=COLORS["bg"])
        self.state("zoomed")

        self._construir()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = 520
        alto = 420
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _construir(self):
        header = tk.Frame(self, bg=COLORS["accent"], height=90)
        header.pack(fill="x")

        tk.Label(
            header,
            text="SIGEN",
            font=("Segoe UI", 24, "bold"),
            bg=COLORS["accent"],
            fg="white"
        ).pack(pady=(18, 0))

        tk.Label(
            header,
            text="Sistema de Gestión de Nivelación",
            font=("Segoe UI", 10),
            bg=COLORS["accent"],
            fg="white"
        ).pack()

        contenedor = tk.Frame(self, bg=COLORS["bg"])
        contenedor.pack(fill="both", expand=True)

        card = tk.Frame(
            contenedor,
            bg=COLORS["surface"],
            padx=35,
            pady=28
        )
        card.pack(expand=True)

        tk.Label(
            card,
            text="Iniciar sesión",
            font=("Segoe UI", 16, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text"]
        ).grid(row=0, column=0, columnspan=2, pady=(0, 18))

        tk.Label(
            card,
            text="Correo",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text"]
        ).grid(row=1, column=0, sticky="w", pady=6)

        self.correo = tk.Entry(
            card,
            width=32,
            font=("Segoe UI", 10),
            bg=COLORS["bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            bd=6
        )
        self.correo.grid(row=2, column=0, columnspan=2, pady=(0, 12))

        tk.Label(
            card,
            text="Contraseña",
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text"]
        ).grid(row=3, column=0, sticky="w", pady=6)

        self.password = tk.Entry(
            card,
            width=32,
            show="*",
            font=("Segoe UI", 10),
            bg=COLORS["bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            bd=6
        )
        self.password.grid(row=4, column=0, columnspan=2, pady=(0, 18))

        tk.Button(
            card,
            text="Iniciar sesión",
            command=self.login,
            font=("Segoe UI", 10, "bold"),
            bg=COLORS["success"],
            fg="white",
            activebackground=COLORS["accent2"],
            activeforeground="white",
            relief="flat",
            padx=22,
            pady=8,
            cursor="hand2"
        ).grid(row=5, column=0, columnspan=2, pady=(4, 12))

        tk.Label(
            card,
            text="Acceso para administradores, docentes y estudiantes",
            font=("Segoe UI", 8),
            bg=COLORS["surface"],
            fg=COLORS["text2"]
        ).grid(row=6, column=0, columnspan=2)

        self.bind("<Return>", lambda event: self.login())

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

        try:
            self._stdout_gui.desactivar()
        except Exception:
            pass

        estado.usuario_actual = None
        self.destroy()

        login = LoginWindow()
        login.mainloop()

    def _construir_ui(self):
        # Header:
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
            font=("Segoe UI", 14, "bold"),
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
            padx=12,
            pady=5,
            cursor="hand2",
        ).grid(row=0, column=2, sticky="e", padx=16)

        # Body:
        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=12, pady=8)

        # Notebook (pestañas)
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "TNotebook", background=COLORS["bg"], borderwidth=0
        )
        style.configure(
            "TNotebook.Tab",
            background=COLORS["surface"],
            foreground=COLORS["text2"],
            font=("Segoe UI", 10, "bold"),
            padding=[12, 6],
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", "white")],
        )

        nb = ttk.Notebook(body)
        nb.pack(fill="both", expand=True)

        # Consola abajo
        console_frame = tk.Frame(self, bg=COLORS["bg"])
        console_frame.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(
            console_frame, text="Consola del sistema",
            font=("Segoe UI", 9, "bold"),
            bg=COLORS["bg"], fg=COLORS["text2"]
        ).pack(anchor="w")
        self.consola = scrolledtext.ScrolledText(
            console_frame, height=8, state="disabled",
            bg="#0f0f1a", fg=COLORS["success"],
            font=("Courier New", 9), relief="flat",
            insertbackground=COLORS["text"],
        )
        self.consola.pack(fill="x")

        # Redirigir stdout
        self._stdout_gui = ConsolaGUI(self.consola)
        self._stdout_gui.activar()

        # Pestañas: 
        self.tab_inicio    = TabInicio(nb, self)
        self.tab_sede      = TabSede(nb)
        self.tab_docentes  = TabDocentes(nb)
        self.tab_estudiantes = TabEstudiantes(nb)
        self.tab_asignaturas = TabAsignaturas(nb)
        self.tab_paralelos   = TabParalelos(nb)
        self.tab_matricula   = TabMatricula(nb)
        self.tab_calificar   = TabCalificar(nb)
        self.tab_reportes    = TabReportes(nb)
        self.tab_resumen     = TabResumen(nb)

        usuario = estado.usuario_actual

        if isinstance(usuario, Docente):
            nb.add(self.tab_calificar, text="Calificar")
            nb.add(self.tab_reportes, text="Reportes")
            nb.add(self.tab_resumen, text="Resumen")

        elif isinstance(usuario, Estudiante):
            nb.add(self.tab_calificar, text="Mis notas")
            nb.add(self.tab_reportes, text="Mis reportes")
            nb.add(self.tab_resumen, text="Resumen")

        else:
            nb.add(self.tab_inicio,      text="Inicio")
            nb.add(self.tab_sede,        text="Sedes")
            nb.add(self.tab_docentes,    text="Docentes")
            nb.add(self.tab_estudiantes, text="Estudiantes")
            nb.add(self.tab_asignaturas, text="Asignaturas")
            nb.add(self.tab_paralelos,   text="Paralelos")
            nb.add(self.tab_matricula,   text="Matrícula")
            nb.add(self.tab_reportes,    text="Reportes")
            nb.add(self.tab_resumen,     text="Resumen")

        nb.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def _on_tab_change(self, event):
        """Refresca combos cuando se cambia de pestaña."""
        tab = event.widget.nametowidget(event.widget.select())
        if hasattr(tab, "refrescar"):
            tab.refrescar()


# TAB 1 — INICIO / Configurar sistema

class TabInicio(tk.Frame):
    def __init__(self, parent, app: AppSIGEN):
        super().__init__(parent, bg=COLORS["bg"])
        self._app = app
        self._construir()

    def _construir(self):
        contenedor = frame(self, padx=40, pady=30)
        contenedor.pack(expand=True)

        lbl(contenedor, "Configuración inicial del sistema", bold=True, size=13).grid(
            row=0, column=0, columnspan=2, pady=(0, 20)
        )
        lbl(contenedor, "Nombre de la institución").grid(row=1, column=0, sticky="w", pady=4)
        self.e_institucion = entry(contenedor, width=35)
        self.e_institucion.insert(0, "ULEAM - Campus Manta")
        self.e_institucion.grid(row=1, column=1, pady=4, padx=8)

        separador(contenedor, row=2)
        lbl(contenedor, "Datos del Administrador", bold=True, size=11).grid(
            row=3, column=0, columnspan=2, pady=(8, 4)
        )

        campos = [
            ("Nombre", "ADONIS SOLORZANO"),
            ("Correo", "ADONIS@uleam.edu.ec"),
            ("Contraseña", "Admin123"),
            ("Teléfono", "0991234567"),
            ("Nivel de autoridad", "Alto"),
            ("Departamento", "Nivelación"),
        ]
        campos = [
            ("Nombre", "Anthony Salazar"),
            ("Correo", "anthonysalazar006@gmail.com"),
            ("Contraseña", "Admin123"),
            ("Teléfono", "0991234567"),
            ("Nivel de autoridad", "Alto"),
            ("Departamento", "Nivelación"),
        ]
        self._entries = {}
        for i, (label, default) in enumerate(campos):
            lbl(contenedor, label).grid(row=4+i, column=0, sticky="w", pady=3)
            e = entry(contenedor, show="*" if label == "Contraseña" else None)
            e.insert(0, default)
            e.grid(row=4+i, column=1, pady=3, padx=8)
            self._entries[label] = e

        btn(contenedor, "🚀 Iniciar Sistema", self._iniciar,
            color=COLORS["success"]).grid(
            row=4+len(campos)+1, column=0, columnspan=2, pady=20
        )

        self._lbl_estado = lbl(contenedor, "", color=COLORS["text2"])
        self._lbl_estado.grid(row=4+len(campos)+2, column=0, columnspan=2)

    def _iniciar(self):
        nombre_inst = self.e_institucion.get().strip()
        nombre_admin = self._entries["Nombre"].get().strip()
        correo = self._entries["Correo"].get().strip()
        contrasena = self._entries["Contraseña"].get().strip()
        telefono = self._entries["Teléfono"].get().strip()
        nivel = self._entries["Nivel de autoridad"].get().strip()
        depto = self._entries["Departamento"].get().strip()

        if not all([nombre_inst, nombre_admin, correo, contrasena]):
            messagebox.showwarning("Campos incompletos", "Completa todos los campos obligatorios.")
            return

        try:
            admin = Administrador(
                id=1, nombre=nombre_admin, correo=correo,
                contrasena=contrasena, telefono=telefono,
                nivel_autoridad=nivel, departamento_asignado=depto,
            )
            estado.admin = admin
            estado.gestor = GestorNivelacion(nombre_inst, admin)
            self._lbl_estado.config(
                text=f"Sistema iniciado como: {nombre_admin}",
                fg=COLORS["success"]
            )
            messagebox.showinfo("SIGEN", f"Sistema iniciado correctamente.\nBienvenido, {nombre_admin}.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))


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
            estado.gestor.registrar_sede(sede)
            estado.sedes.append(sede)
            guardar_datos()
            self._lista.insert(tk.END, f"  {sede.nombre_sede} — {sede.ciudad} (cap. {sede.capacidad_total})")
            messagebox.showinfo("OK", f"Sede '{sede.nombre_sede}' registrada.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _validar_sistema(self):
        if not estado.gestor:
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
        self._lista = tk.Listbox(
            self, bg=COLORS["bg"], fg=COLORS["text"],
            font=("Segoe UI", 10), height=6, relief="flat",
            selectbackground=COLORS["accent"],
        )
        self._lista.pack(fill="x", padx=20, pady=6)

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
            estado.gestor.registrar_docente(docente)

            # Sede
            sede_sel = self._cb_sede.get()
            sede = next((s for s in estado.sedes if s.nombre_sede == sede_sel), None)
            if sede:
                estado.gestor.asignar_sede_a_docente(docente, sede)

            # Horas
            horas = int(self._e_horas.get() or 0)
            if horas > 0:
                estado.gestor.asignar_carga_horaria(docente, horas)

            estado.docentes.append(docente)
            guardar_datos()
            self._lista.insert(tk.END, f"  {docente.nombre} — {docente.especialidad}")
            messagebox.showinfo("OK", f"Docente '{docente.nombre}' registrado.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _importar_csv(self):
        if not self._validar_sistema():
            return

        ruta = filedialog.askopenfilename(
        title="Seleccionar archivo CSV de docentes",
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
        if not estado.gestor:
            messagebox.showwarning("Sistema", "Primero inicia el sistema en la pestaña Inicio.")
            return False
        return True

    def refrescar(self):
        self._cb_sede["values"] = [s.nombre_sede for s in estado.sedes]

        self._lista.delete(0, tk.END)

        for docente in estado.docentes:
            self._lista.insert(
            tk.END,
            f"{docente.nombre} — {docente.especialidad}"
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
        self._lista = tk.Listbox(
            self, bg=COLORS["bg"], fg=COLORS["text"],
            font=("Segoe UI", 10), height=6, relief="flat",
            selectbackground=COLORS["accent"],
        )
        self._lista.pack(fill="x", padx=20, pady=6)

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
            estado.gestor.registrar_estudiante(est)
            estado.estudiantes.append(est)
            guardar_datos()
            self._lista.insert(tk.END, f"  {est.nombre} — {carrera.nombre_carrera}")
            messagebox.showinfo("OK", f"Estudiante '{est.nombre}' registrado.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _importar_csv(self):
        if not self._validar_sistema():
            return

        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de estudiantes",
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
        if not estado.gestor:
            messagebox.showwarning("Sistema", "Primero inicia el sistema en la pestaña Inicio.")
            return False
        return True

    def refrescar(self):
        self._cb_sede["values"] = [s.nombre_sede for s in estado.sedes]
        self._cb_carrera["values"] = [c.nombre_carrera for c in estado.carreras]

        self._lista.delete(0, tk.END)

        for est in estado.estudiantes:
            self._lista.insert(
            tk.END,
            f"{est.nombre}"
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
        self._lista = tk.Listbox(
            self, bg=COLORS["bg"], fg=COLORS["text"],
            font=("Segoe UI", 10), height=6, relief="flat",
            selectbackground=COLORS["accent"],
        )
        self._lista.pack(fill="x", padx=20, pady=6)

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
                estado.gestor.asignar_docente_a_asignatura(docente, asig)

            carrera_sel = self._cb_carrera.get()
            carrera = next((c for c in estado.carreras if c.nombre_carrera == carrera_sel), None)
            if carrera:
                carrera.agregar_asignatura(asig)

            estado.gestor.registrar_asignatura(asig)
            estado.asignaturas.append(asig)
            guardar_datos()
            self._lista.insert(tk.END, f"  {asig.nombre} — {asig.creditos} créditos")
            messagebox.showinfo("OK", f"Asignatura '{asig.nombre}' registrada.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _validar_sistema(self):
        if not estado.gestor:
            messagebox.showwarning("Sistema", "Primero inicia el sistema en la pestaña Inicio.")
            return False
        return True

    def refrescar(self):
        self._cb_docente["values"] = [d.nombre for d in estado.docentes]
        self._cb_carrera["values"] = [c.nombre_carrera for c in estado.carreras]


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
        lbl(self, "Paralelos registrados", bold=True).pack()
        self._lista = tk.Listbox(
            self, bg=COLORS["bg"], fg=COLORS["text"],
            font=("Segoe UI", 10), height=5, relief="flat",
            selectbackground=COLORS["accent"],
        )
        self._lista.pack(fill="x", padx=20, pady=6)

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

            modalidad = Modalidad(
                id_modalidad=len(estado.paralelos)+1,
                tipo=self._cb_modalidad.get(),
                descripcion="Modalidad del paralelo",
                duracion_horas=2,
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
            estado.gestor.registrar_paralelo(paralelo)

            sede_sel = self._cb_sede.get()
            sede = next((s for s in estado.sedes if s.nombre_sede == sede_sel), None)
            if sede:
                sede.agregar_paralelo(paralelo)

            estado.paralelos.append(paralelo)
            estado.modalidades.append(modalidad)
            estado.horarios.append(horario)
            guardar_datos()
            self._lista.insert(tk.END, f"  {paralelo.codigo} — {asignatura.nombre} | {docente.nombre} | {horario.dia} {horario.hora_inicio}-{horario.hora_fin}")
            messagebox.showinfo("OK", f"Paralelo '{paralelo.codigo}' creado.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _validar_sistema(self):
        if not estado.gestor:
            messagebox.showwarning("Sistema", "Primero inicia el sistema en la pestaña Inicio.")
            return False
        return True

    def refrescar(self):
        self._cb_docente["values"] = [d.nombre for d in estado.docentes]
        self._cb_sede["values"] = [s.nombre_sede for s in estado.sedes]
        self._cb_asignatura["values"] = [a.nombre for a in estado.asignaturas]

        self._lista.delete(0, tk.END)
        for paralelo in estado.paralelos:
            asignatura = paralelo.asignatura.nombre if paralelo.asignatura else "Sin asignatura"
            horario = paralelo.horario
            self._lista.insert(
                tk.END,
                f"{paralelo.codigo} — {asignatura} | {paralelo.docente.nombre} | {horario.dia} {horario.hora_inicio}-{horario.hora_fin}"
            )


# TAB 7 — MATRÍCULA

class TabMatricula(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS["bg"])
        self._construir()

    def _construir(self):
        lbl(self, "Matrícula de Estudiantes", bold=True, size=12).pack(pady=(16, 8))

        # --- Sección: Matricular en paralelo ---
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

        separador(self)

        # --- Sección: Registrar carrera + oferta ---
        lbl(self, "📋 Registrar Carrera y Oferta", bold=True).pack(pady=(4, 6))

        f2 = frame(self)
        f2.pack(pady=4)

        lbl(f2, "ID Carrera").grid(row=0, column=0, sticky="w", pady=3)
        self._e_id_car = entry(f2, width=10)
        self._e_id_car.insert(0, "1")
        self._e_id_car.grid(row=0, column=1, sticky="w", pady=3, padx=8)

        lbl(f2, "Nombre carrera").grid(row=1, column=0, sticky="w", pady=3)
        self._e_nom_car = entry(f2)
        self._e_nom_car.insert(0, "Ingeniería en Sistemas")
        self._e_nom_car.grid(row=1, column=1, pady=3, padx=8)

        lbl(f2, "Facultad").grid(row=2, column=0, sticky="w", pady=3)
        self._e_fac = entry(f2)
        self._e_fac.insert(0, "Ciencias Informáticas")
        self._e_fac.grid(row=2, column=1, pady=3, padx=8)

        lbl(f2, "Cupos totales").grid(row=3, column=0, sticky="w", pady=3)
        self._e_cupos_car = entry(f2, width=10)
        self._e_cupos_car.insert(0, "40")
        self._e_cupos_car.grid(row=3, column=1, sticky="w", pady=3, padx=8)

        lbl(f2, "Puntaje mínimo").grid(row=4, column=0, sticky="w", pady=3)
        self._e_pmin = entry(f2, width=10)
        self._e_pmin.insert(0, "600")
        self._e_pmin.grid(row=4, column=1, sticky="w", pady=3, padx=8)

        lbl(f2, "Puntaje máximo").grid(row=5, column=0, sticky="w", pady=3)
        self._e_pmax = entry(f2, width=10)
        self._e_pmax.insert(0, "1000")
        self._e_pmax.grid(row=5, column=1, sticky="w", pady=3, padx=8)

        lbl(f2, "Sede").grid(row=6, column=0, sticky="w", pady=3)
        self._cb_sede_car = combo(f2, [])
        self._cb_sede_car.grid(row=6, column=1, pady=3, padx=8)

        btn(f2, "➕ Crear Carrera y Oferta", self._crear_carrera_oferta,
            color=COLORS["warning"]).grid(row=7, column=0, columnspan=2, pady=10)

        separador(self)

        # --- Sección: Matricular en carrera ---
        lbl(self, "🎓 Inscribir en Carrera vía Oferta", bold=True).pack(pady=(4, 6))
        f3 = frame(self)
        f3.pack(pady=4)

        lbl(f3, "Estudiante").grid(row=0, column=0, sticky="w", pady=3)
        self._cb_est_car = combo(f3, [])
        self._cb_est_car.grid(row=0, column=1, pady=3, padx=8)

        lbl(f3, "Puntaje obtenido").grid(row=1, column=0, sticky="w", pady=3)
        self._e_puntaje = entry(f3, width=10)
        self._e_puntaje.insert(0, "750")
        self._e_puntaje.grid(row=1, column=1, sticky="w", pady=3, padx=8)

        btn(f3, "✅ Inscribir en Carrera", self._matricular_carrera,
            color=COLORS["success"]).grid(row=2, column=0, columnspan=2, pady=10)

    def _matricular_paralelo(self):
        if not self._validar_sistema(): return
        try:
            est_n = self._cb_est_par.get()
            par_c = self._cb_par.get()
            est = next((e for e in estado.estudiantes if e.nombre == est_n), None)
            par = next((p for p in estado.paralelos if p.codigo == par_c), None)
            if not est or not par:
                messagebox.showwarning("Faltan datos", "Selecciona estudiante y paralelo.")
                return
            estado.gestor.asignar_estudiante_a_paralelo(est, par)
            messagebox.showinfo("OK", f"'{est.nombre}' matriculado en paralelo '{par.codigo}'.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

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
            puntaje = float(self._e_puntaje.get())
            oferta = estado.ofertas[-1]
            estado.gestor.matricular_en_carrera(est, oferta, puntaje)
            messagebox.showinfo("OK", f"Inscripción procesada para '{est.nombre}'.")
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def _validar_sistema(self):
        if not estado.gestor:
            messagebox.showwarning("Sistema", "Primero inicia el sistema en la pestaña Inicio.")
            return False
        return True

    def refrescar(self):
        self._cb_est_par["values"] = [e.nombre for e in estado.estudiantes]
        self._cb_par["values"] = [p.codigo for p in estado.paralelos]
        self._cb_est_car["values"] = [e.nombre for e in estado.estudiantes]
        self._cb_sede_car["values"] = [s.nombre_sede for s in estado.sedes]


# TAB 8 — CALIFICAR

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

            estado.gestor.calificar_estudiante(
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
        if not estado.gestor:
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
            reporte = estado.gestor.generar_reporte_calificaciones(estudiante)
            mostrar_texto("Reporte de calificaciones", reporte.contenido_completo)
        else:
            messagebox.showwarning("Usuario", "Esta opción solo es para estudiantes.")

    def _rep_mi_docente(self):
        if not self._validar_sistema():
            return

        docente = estado.usuario_actual

        if isinstance(docente, Docente):
            reporte = estado.gestor.generar_reporte_docente(docente)
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

        reporte = estado.gestor.generar_reporte_calificaciones(est)
        mostrar_texto("Reporte de calificaciones", reporte.contenido_completo)

    def _rep_docente(self):
        if not self._validar_sistema():
            return

        doc_n = self._cb_doc.get()
        doc = next((d for d in estado.docentes if d.nombre == doc_n), None)

        if not doc:
            messagebox.showwarning("Faltan datos", "Selecciona un docente.")
            return

        reporte = estado.gestor.generar_reporte_docente(doc)
        mostrar_texto("Reporte de docente", reporte.contenido_completo)

    def _rep_sede(self):
        if not self._validar_sistema():
            return

        sede_n = self._cb_sede.get()
        sede = next((s for s in estado.sedes if s.nombre_sede == sede_n), None)

        if not sede:
            messagebox.showwarning("Faltan datos", "Selecciona una sede.")
            return

        reporte = estado.gestor.generar_reporte_sede(sede)
        mostrar_texto("Reporte de sede", reporte.contenido_completo)

    def _listar(self):
        if not self._validar_sistema():
            return

        estado.gestor.listar_todos_reportes()

    def _validar_sistema(self):
        if not estado.gestor:
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
            reporte = estado.gestor.generar_reporte_docente(docente)
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

        estado.gestor.resumen_sistema()

    def _cerrar_periodo(self):
        if not self._validar_sistema():
            return

        if not estado.periodos:
            messagebox.showwarning("Sin periodos", "No hay periodos activos registrados.")
            return

        periodo = estado.periodos[-1]
        estado.gestor.cerrar_periodo(periodo)
        messagebox.showinfo("OK", f"Periodo '{periodo.semestre}' cerrado.")

    def _validar_sistema(self):
        if not estado.gestor:
            messagebox.showwarning("Sistema", "Primero inicia el sistema.")
            return False
        return True

    def refrescar(self):
        usuario = estado.usuario_actual

        if isinstance(usuario, Administrador):
            self._actualizar()


# ENTRY POINT

if __name__ == "__main__":
    cargar_datos()
    iniciar_sistema_automatico()

    login = LoginWindow()
    login.mainloop()