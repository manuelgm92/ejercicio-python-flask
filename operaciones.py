from conexion import obtener_conexion
from datetime import datetime, timezone
from contextlib import closing


def extraer_usuario(name):
    with closing(obtener_conexion()) as conexion:
        with conexion.cursor() as cursor:
            try:
                query = "SELECT password FROM usuarios WHERE user_name = %s"
                cursor.execute(query, (name,))
                resultado = cursor.fetchone()
                if resultado:
                    return resultado[0]
                return None
            
            except Exception as error:
                print("Error: ", error)
                return None


def crear_usuario(name, password):
    with closing(obtener_conexion()) as conexion:
        with conexion.cursor() as cursor:
            try:
                query_comprobar_si_existe_user = "SELECT user_name, password FROM usuarios WHERE user_name = %s"
                cursor.execute(query_comprobar_si_existe_user, (name,))
                usuario_existente = cursor.fetchall()

                if usuario_existente:
                    return "Ya existe un usuario con ese nombre."
                else:
                    query = "INSERT INTO usuarios (user_name, password) VALUES (%s, %s)"
                    valores = (name, password)
                    cursor.execute(query, valores)
                    conexion.commit()
                    return "Usuario creado con éxito"
            except Exception as error:
                print("Error: ", error)
                conexion.rollback()
                return None
            
def mostrar_frases(name=None):
    with closing(obtener_conexion()) as conexion:
        with conexion.cursor() as cursor:
            try:
                if name is None:
                    query = "SELECT frase FROM frases"
                    params = None
                else:
                    query = """
                        SELECT frase 
                        FROM frases f
                        JOIN usuarios u ON u.user_id = f.user_id                   
                        WHERE user_name = %s
                        """
                    params = (name,)
                
                if params is not None:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                resultado = cursor.fetchall()
                resultado_frases = [frase[0] for frase in resultado]
                return resultado_frases
            
            except Exception as error:
                print("Error: ", error)
                return []
                            
    
def agregar_frase(frase, usuario):
    with closing(obtener_conexion()) as conexion:
        with conexion.cursor() as cursor:
            try:
                query_usuario = "SELECT user_id FROM usuarios WHERE user_name = %s"
                cursor.execute(query_usuario, (usuario,))  
                resultado_user_id = cursor.fetchone()
                user_id = resultado_user_id[0]
                
                query_frase = "INSERT INTO frases (user_id, frase) VALUES (%s, %s)"
                valores = (user_id, frase)
                cursor.execute(query_frase, valores)
                
                conexion.commit()
                print("Frase agregada con éxito.")
                
            except Exception as error:
                print("Error: ", error)
                conexion.rollback()
                print("Se ha ejecutado rollback(). La base de datos vuelve al estado anterior.")


def registrar_inicio_sesion(usuario):
    with closing(obtener_conexion()) as conexion:
        with conexion.cursor() as cursor:
            try:
                ahora = datetime.now(timezone.utc)
                query = "INSERT INTO accesos (usuario, inicio_sesion) VALUES (%s, %s) RETURNING id;"
                params = (usuario, ahora)
                cursor.execute(query, params)
                
                id_sesion = cursor.fetchone()[0]
                conexion.commit()
                print("Inicio de sesión registrado")
                return id_sesion
                
            except Exception as error:
                print("Error: ", error)
                conexion.rollback()
                print("Se ha ejecutado rollback(). La base de datos vuelve al estado anterior.")
                return None

                
def registrar_fin_sesion(id_sesion, tipo_cierre):
    with closing(obtener_conexion()) as conexion:
        with conexion.cursor() as cursor:
            try:
                ahora = datetime.now(timezone.utc)
                params = (ahora, tipo_cierre, id_sesion)
                query = "UPDATE accesos SET fin_sesion = %s, tipo_cierre = %s WHERE id = %s;" 
                cursor.execute(query, params)
                conexion.commit()
                print("Fin de sesión registrado")
                
            except Exception as error:
                print("Error: ", error)
                conexion.rollback()
                print("Se ha ejecutado rollback(). La base de datos vuelve al estado anterior.")
                return None
                


def mostrar_accesos():
    with closing(obtener_conexion()) as conexion:
        with conexion.cursor() as cursor:
            try:
                query = "SELECT usuario, inicio_sesion, fin_sesion, tipo_cierre FROM accesos ORDER BY inicio_sesion DESC"
                cursor.execute(query)
                resultado = cursor.fetchall()
                return (resultado)
                
            except Exception as error:
                print("Error: ", error)
                return []
            

