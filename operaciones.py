from conexion import obtener_conexion

def inicializar_tablas():
    try:
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute("""
                                CREATE TABLE IF NOT EXISTS usuarios (
                                user_id serial,
                                user_name varchar(20) NOT NULL,
                                password varchar(20) NOT NULL,
                                PRIMARY KEY (user_id)
                                );
                                """)

                cursor.execute("""
                                CREATE TABLE IF NOT EXISTS frases (
                                frase_id serial,
                                user_id integer NOT NULL,
                                frase varchar(100) NOT NULL,
                                PRIMARY KEY (frase_id)
                                );
                                """)
                conexion.commit()
        print("tablas listas")
    except Exception as error:
        print("Error: " , error)

def extraer_usuario(name):
    with obtener_conexion() as conexion:
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

def crear_usuario(name, password):
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            # query_select = "SELECT * FROM usuarios"
            # cursor.execute(query_select)
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
            
def mostrar_frases(name=None):
    with obtener_conexion() as conexion:
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
    
def agregar_frase(frase, usuario):
    with obtener_conexion() as conexion:
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