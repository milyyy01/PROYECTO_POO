from models.usuario import Usuario

class Estudiante(Usuario):
    def __init__(self, id, nombre, correo, contrasena, telefono, fecha_matricula, sede, carrera, estado_academico = "Activo"):
        super().__init__(id, nombre, correo, contrasena, rol="Estudiante", telefono=telefono)
        self.fecha_matricula = fecha_matricula
        self.__promedio = 0.0
        self.estado_academico = estado_academico
        self.sede = sede
        self.carrera = carrera
        self.__tareas_enviadas = []
        self.__materias = []
        self.__calificaciones = {}
        
    @property
    def promedio(self):
        return self.__promedio
    
# Métodos abstractos implementados:

    def ver_materias(self):
        if not self.__materias:
            print("No estás inscrito en ninguna materia.")
            return
        else: 
            print("Materias inscritas:")
            for materia in self.__materias:
                print(f"-- {materia}")
                
    def ver_calificaciones(self):
        if not self.__calificaciones:
            print("No tienes calificaciones registradas por el momento.")
            return
        else:
            print("Calificaciones:")
            for materia, calificacion in self.__calificaciones.items():
                print(f"{materia}: {calificacion}")
                
# Métodos concretos de Estudiante:

    def enviar_tarea(self, tarea):
        self.__tareas_enviadas.append(tarea)
        print("Tarea enviada exitosamente.")

    def anular_entrega(self, tarea):
        if tarea in self.__tareas_enviadas:
            self.__tareas_enviadas.remove(tarea)
            print("Entrega anulada exitosamente.")
        else:
            print("No se encontró la tarea en tus entregas.")

    def consultar_asignaturas(self, asignatura):
        print(f"Consultando información de la asignatura: {asignatura}")

    def descargar_material(self, material):
        print(f"{material} descargado exitosamente.")

    def agregar_comentarios(self, comentario):
        print(f"Comentario agregado exitosamente: {comentario}")
    
# Métodos internos:

    def _agregar_materia(self, materia):
        self.__materias.append(materia)
        
    def _registrar_calificacion(self, materia, nota):
        self.__calificaciones[materia] = nota
        self.__actualizar_promedio()
        
    def __actualizar_promedio(self):
        if self.__calificaciones:
            self.__promedio = sum(self.__calificaciones.values()) / len(self.__calificaciones)
           
    def __str__(self):
        return (f"[Estudiante] {self.nombre} - Carrera: {self.carrera} - "
                f"Sede: {self.sede} - Promedio: {self.__promedio:.2f}")

    