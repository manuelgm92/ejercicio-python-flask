import os

def comprobar_ficheros(ruta):
    if not os.path.exists(ruta):
        with open(ruta, "w") as f:
            f.write("")
            
def extraer_contenido(ruta, diccionario):
    with open(ruta, "r") as f:
        lineas = f.readlines()
        
        for linea in lineas:
            k, v = linea.strip().split(":")
            diccionario[k.strip()] = v.strip()

def add_contenido(ruta, clave, valor):
    with open(ruta, "a") as f:
        f.write(f"{clave}:{valor}\n")

def actualizar_contenido(ruta, diccionario):
    with open(ruta, "w") as f:
        for k,v in diccionario.items():
            f.write(f"{k}:{v}\n")