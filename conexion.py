import psycopg2
import os
import dotenv

dotenv.load_dotenv() 

url = os.getenv('DB_HOST') 
puerto = os.getenv('DB_PORT')
usuario = os.getenv('DB_USER')
database = os.getenv('DB_DATABASE')
passwd = os.getenv('DB_PASSWORD')

def obtener_conexion():
    try:
        return psycopg2.connect(host=url, port=puerto, dbname=database, user=usuario, password=passwd)

    except Exception as error:
        print("Error al conectar o interactuar con la base de datos:", error)
        raise