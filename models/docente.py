from models.usuario import Usuario

class Docente(Usuario):
    def __init__(self, id, nombre, correo, contrasena, telefono, titulo, especialidad, nivel):
        super().__init__(id, nombre, correo, contrasena, rol="Docente", telefono=telefono)
        self.titulo = titulo
        self.especialidad = especialidad
        self.nivel = nivel
        self._horas_asignadas = 0
        self.__paralelos = []
        self.__materias_asignadas = []
        self.__calificaciones_registradas = {}
        
    @property
    def horas_asignadas(self):
        return self._horas_asignadas
    
# Métodos abstractos implementados:

    def ver_materias(self):
        if not self.__materias_asignadas:
            print("No tienes materias asignadas por el momento.")
            return
        else: 
            print("Materias asignadas:")
            for materia in self.__materias_asignadas:
                print(f"-- {materia}")
    
    def ver_calificaciones(self):
        if not self.__calificaciones_registradas:
            print("No has registrado calificaciones por el momento.")
            return
        else:
            print("Calificaciones registradas:")
            for estudiante, materias in self.__calificaciones_registradas.items():
                for materia, nota in materias.items():
                    print(f"{estudiante} - {materia}: {nota}")
                    
# Métodos concretos de Docente:

    def impartir_clase(self, materia, paralelo):
        print(f"{self.nombre} impartiendo clase de {materia} en el paralelo {paralelo}.")
    
    def asignar_horario(self, dia, hora_entrada, hora_salida):
        print(f"Horario asignado para {self.nombre}: {dia} de {hora_entrada} a {hora_salida}.")
        
    def calificar(self, estudiante, materia, nota, comentario = None):
        if estudiante not in self.__calificaciones_registradas:
            self.__calificaciones_registradas[estudiante] = {}
        self.__calificaciones_registradas[estudiante][materia] = nota
        
        if comentario:
            print(f"Calificación registrada para {estudiante} en {materia}: {nota}. Comentario: {comentario}")
        else:
            print(f"Calificación registrada para {estudiante} en {materia}: {nota}.")
            
    def marcar_asistencia(self, estudiante, presente):
        estado = "Presente" if presente else "Ausente"
        print(f"Asistencia de {estudiante}: {estado}.")
        
    def subir_material(self, materia, material):
        print(f"Se subió archivo '{material}' para la materia {materia}.")
        
    def ver_paralelos(self):
        if not self.__paralelos:
            print(f"{self.nombre} no tiene paralelos asignados por el momento.")
            return
        else:
            print(f"Paralelos asignados a {self.nombre}:")
            for paralelo in self.__paralelos:
                print(f"- {paralelo}")
                
# Métodos internos:

    def _asignar_materia(self, materia):
            self.__materias_asignadas.append(materia)

    def _asignar_paralelo(self, paralelo):
            self.__paralelos.append(paralelo)
            
    def _agregar_horas(self, horas):
            self._horas_asignadas += horas
            
    def __str__(self):
            return (f"[Docente] {self.nombre} - Título: {self.titulo} - "
                    f"Especialidad: {self.especialidad} - Horas Asignadas: {self._horas_asignadas}")