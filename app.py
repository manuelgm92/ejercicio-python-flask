from flask import Flask, render_template, request, redirect, url_for, session, flash
from ficheros import comprobar_ficheros, extraer_contenido, add_contenido, actualizar_contenido

app = Flask(__name__)
app.secret_key = "clave_secreta"
ruta_usuarios = "usuarios.txt"
ruta_frases = "frases.txt"
usuarios = {}
frases_usuarios = {}

comprobar_ficheros(ruta_usuarios)
comprobar_ficheros(ruta_frases)
extraer_contenido(ruta_usuarios, usuarios)
extraer_contenido(ruta_frases, frases_usuarios)

@app.route("/")
@app.route("/login", methods=['GET','POST'])
def inicio():
    if request.method == 'POST':
        usuario = request.form.get("usuario")
        contrasenia = request.form.get("passwd")
        
        if usuario in usuarios:
            if usuarios[usuario] == contrasenia:
                session["usuario"] = usuario
                return redirect(url_for("perfil"))
            else:
                return render_template("index.html", error="Contraseña incorrecta.")
        else:
            return render_template("index.html", error="Credenciales incorrectas.")
        
    if "usuario" in session:
        return redirect(url_for("perfil"))

    return render_template("index.html")

@app.route("/registro", methods=['GET','POST'])
def registro():
    if request.method == 'POST':
        nuevo_usuario = request.form.get("usuario")
        contrasenia = request.form.get("passwd")
        verificar_contrasenia = request.form.get("passwd_verificar")

        if nuevo_usuario not in usuarios:
            if contrasenia == verificar_contrasenia:
                usuarios[nuevo_usuario] = contrasenia
                add_contenido(ruta_usuarios, nuevo_usuario, contrasenia)
                flash("¡Te has registrado con éxito! Ya puedes iniciar sesión.", "exito")
                return redirect(url_for("inicio"))
            else:
                flash("Las contraseñas no coinciden.")
                return redirect(url_for("registro"))
        else:
            flash("El usuario ya existe.")
            return redirect(url_for("registro"))
            
    return render_template("registro.html")

@app.route("/perfil", methods=['GET'])
def perfil():
    if not "usuario" in session:
        return redirect(url_for("inicio"))
    usuario_actual = session["usuario"]
    frases_usuario = []
    for k, v in frases_usuarios.items():
        if usuario_actual == v:
            frases_usuario.append(k)
    
    return render_template("perfil.html", usuario=usuario_actual, frases=frases_usuario)

@app.route("/nueva_frase", methods=['GET'])
def nueva_frase():
    nueva_frase = request.args.get("nueva_frase")
    usario_actual = session["usuario"]
    frases_usuarios[nueva_frase] = usario_actual
    actualizar_contenido(ruta_frases, frases_usuarios)
    flash("Frase añadida con éxito", "nueva frase")
    
    return redirect(url_for("perfil"))
    
@app.route("/logout")
def logout():
    session.clear()
    flash("Ha cerrado sesión con éxito", "cierre de sesión")
    return redirect(url_for("inicio"))

if __name__ == "__main__":
    app.run()