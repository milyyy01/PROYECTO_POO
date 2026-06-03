from abc import ABC, abstractmethod
import random
import string

class Usuario(ABC):
    def __init__(self, id, nombre, correo, contrasena, rol, telefono):
        self.id = id
        self.nombre = nombre
        self._correo = correo
        self.__contrasena = contrasena
        self._rol = rol
        self.telefono = telefono
        self.__codigo_recuperacion = None
    
    @property
    def correo(self):
        return self._correo
    
    @correo.setter
    def correo(self, nuevo_correo):
        if '@' not in nuevo_correo:
            raise ValueError("El correo es inválido.")
        self._correo = nuevo_correo 
        
    @property
    def rol(self):
        return self._rol
        
    @property
    def contrasena(self):
        raise AttributeError("La contraseña no se puede acceder directamente.")
    
    @contrasena.setter
    def contrasena(self, nueva_contrasena):
        if len(nueva_contrasena) < 6:  
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        if not any(caracter.isupper() for caracter in nueva_contrasena):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula.")
        self.__contrasena = nueva_contrasena
        
# Métodos concretos: 

    def iniciar_sesion(self, correo, contrasena):
        if correo == self._correo and contrasena == self.__contrasena: 
            print(f"¡Inicio de sesión exitoso! Bienvenido, {self.nombre}")
            return True
        else: 
            print("Correo o contraseña incorrectos. Inténtalo de nuevo.")
            return False

    def cerrar_sesion(self):
        print(f"¡Hasta luego, {self.nombre}! Has cerrado sesión.")
        
    def registrarse(self):
        print(f"¡Registro exitoso! Bienvenido, {self.nombre}")
        
    def editar_perfil(self, nombre = None, correo = None, telefono = None):
        if nombre:
            self.nombre = nombre
        if correo: 
            self.correo = correo
        if telefono:
            self.telefono = telefono 
        print("Perfil actualizado con éxito.")
        
    def solicitar_recuperacion_contrasena(self, correo):
        if correo != self._correo:
            print("El correo ingresado no coincide.")
            return False
        self.__codigo_recuperacion = self.__generar_codigo()
        print(f"Código de recuperación generado: {self.__codigo_recuperacion}")
        return True
        
    def verificar_codigo(self, codigo):
        if self.__codigo_recuperacion is None:
            print("No se ha generado ningún código de recuperación.")
            return False
        if codigo != self.__codigo_recuperacion:
            print("Código de recuperación incorrecto.")
            return False
        else:
            print("Código de recuperación verificado exitosamente.")
            return True
        
    def cambiar_contrasena(self, codigo, nueva_contrasena):
        if not self.verificar_codigo(codigo):
            return False 
        self.contrasena = nueva_contrasena
        self.__codigo_recuperacion = None
        print("Contraseña actualizada con éxito.")
        return True
    
    def __generar_codigo(self):
        caracteres = string.ascii_uppercase + string.digits
        return "".join(random.choices(caracteres, k=6))
    
    
# Métodos abstractos: 
    
    @abstractmethod
    def ver_materias(self):
        pass
    
    @abstractmethod
    def ver_calificaciones(self):
        pass
    
    def __str__(self):
        return f"Usuario(id={self.id}, nombre='{self.nombre}', correo='{self._correo}', rol='{self._rol}', telefono='{self.telefono}')"
    
    
        
        