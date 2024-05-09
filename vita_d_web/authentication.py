from django.contrib.auth.backends import BaseBackend
from django.db import connection
from .models import Usuario

class SQLAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        print(f"Usuario ingresado en formulario: {username}")
        user = self.get_user_by_username(username)
        if user and user.password == password:
            print(f"Usuario {username} autenticado exitosamente")
            return user
        print(f"Autenticación fallida para el usuario {username}")
        return None
    
    def get_user(self, user_id):
        user = self.get_user_by_id(user_id)
        return user

    def get_user_by_username(self, username):
        sql = "SELECT * FROM usuarios WHERE username = %s"
        with connection.cursor() as cursor:
            cursor.execute(sql, [username])
            result = cursor.fetchone()
            print("Usuario DB:", result)
        if result:
            print(f"Usuario encontrado en la base de datos: {result}")
            return self.create_user_instance(result)
        print(f"No se encontró al usuario {username} en la base de datos")
        return None

    def get_user_by_id(self, user_id):
        sql = "SELECT * FROM usuarios WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(sql, [user_id])
            result = cursor.fetchone()
        if result:
            return self.create_user_instance(result)
        return None

    def create_user_instance(self, row):
        # Asumiendo que la estructura de la fila es (id, username, password, email, ...)
        user = Usuario(id=row[0], username=row[1], password=row[2], email=row[3])
        # Asegúrate de que la estructura de la fila coincida con la estructura de tu tabla
        return user
