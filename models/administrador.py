from models.usuario import Usuario

class Administrador(Usuario):
    def __init__(self, id, nombre, correo, contrasena, telefono, nivel_autoridad, departamento_asignado):
        super().__init__(id, nombre, correo, contrasena, rol="Administrador", telefono=telefono)
        self._nivel_autoridad = nivel_autoridad
        self.departamento_asignado = departamento_asignado
        self.__historial_acciones = []
        self._cupos_gestionados = 0
        
    @property
    def nivel_autoridad(self):
        return self._nivel_autoridad
    
    @property
    def cupos_gestionados(self):
        return self._cupos_gestionados
    
    @property
    def historial_acciones(self):
        return list(self.__historial_acciones) #retorna copia, no referencia
    
# Métodos abstractos implementados:

    def ver_materias(self):
        print(f"Admin: {self.nombre} tiene acceso a la lista completa de materias en el sistema.")
        self.__registrar_accion("Visualizó materias")
        
    def ver_calificaciones(self):
        print(f"Admin: {self.nombre} tiene acceso a la lista completa de calificaciones en el sistema.")
        self.__registrar_accion("Visualizó calificaciones")
        
# Métodos concretos de Administrador:

    def validar_registro_docente(self, nombre_docente):
        print(f"Registro del docente {nombre_docente} validado exitosamente.")
        self.__registrar_accion(f"Validó registro del docente {nombre_docente}")
        return True 
    
    def bloquear_usuario(self, usuario):
        print(f"Usuario {usuario.nombre} bloqueado exitosamente.")
        self.__registrar_accion(f"Bloqueó al usuario: {usuario.nombre}")
        
    # Sobrecarga simulada: resetear contraseña con o sin notificación
    
    def resetear_contrasena(self, usuario, nueva_contrasena, notificar = True):
        usuario.contrasena = nueva_contrasena 
        if notificar:
            print(f"Contraseña de {usuario.nombre} reseteada. "
                  f"Notificación enviada a {usuario.correo}")
        else:
            print(f"Contraseña de {usuario.nombre} reseteada sin notificación.")
        self.__registrar_accion(f"Reseteó contraseña de {usuario.nombre}")
    
    def crear_periodo_academico(self, fecha_inicio, fecha_fin, semestre):
        print(f"Periodo académico creado: {semestre}({fecha_inicio} - {fecha_fin}).")
        self.__registrar_accion(f"Creó periodo académico {semestre}")
        
    def cerrar_periodo_academico(self, periodo):
        periodo.culminar_periodo()
        print(f"Periodo académico {periodo.semestre} cerrado exitosamente.")
        self.__registrar_accion(f"Cerró periodo académico {periodo.semestre}")
        
    def gestionar_cupos(self, cantidad):
        self._cupos_gestionados += cantidad
        print(f"Total de cupos gestionados: {self._cupos_gestionados}")
        self.__registrar_accion(f"Gestión de {cantidad} cupos. Total gestionados: {self._cupos_gestionados}")
        
    def asignar_carga_horaria(self, docente, horas):
        docente._agregar_horas(horas)
        print(f"{horas} horas asignadas a {docente.nombre}. Total horas: {docente.horas_asignadas}")
        self.__registrar_accion(f"Asignó {horas} horas a {docente.nombre}")
        
# Métodos internos:

    def __registrar_accion(self, accion):
        self.__historial_acciones.append(accion)
        
    def __str__(self):
        return (f"[Administrador] {self.nombre} - "
                f"Autoridad: {self._nivel_autoridad} - "
                f"Departamento: {self.departamento_asignado} - "
                f"Cupos gestionados: {self._cupos_gestionados}")
        
        
        
        