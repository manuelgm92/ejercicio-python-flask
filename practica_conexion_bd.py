import psycopg2

try:
    conexion = psycopg2.connect(
        host='173.212.252.164',
        port=5432,
        dbname='bd_manuel_glez',
        user='manuel_glez',
        password='12345678'
    )
except Exception as err:
    print('Error: ', err)
    
else:
    print("Conectado a la base de datos.")