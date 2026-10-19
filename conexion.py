import psycopg2

host='173.212.252.164',
port=5432,
dbname='bd_manuel_glez',
user='manuel_glez',
password='12345678' 

def obtener_conexion():
    try:
        return psycopg2.connect(
            host=host, port=port, dbname=dbname, user=user, password=password
            )
    except Exception as error:
        print("Error al conectar o interactuar con la base de datos:", error)