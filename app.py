from flask import Flask, render_template, request, redirect, url_for, session, flash
from operaciones import mostrar_frases, inicializar_tablas, extraer_usuario, crear_usuario, agregar_frase
    
app = Flask(__name__)
app.secret_key = "clave_secreta"

inicializar_tablas()

@app.route("/")
@app.route("/login", methods=['GET','POST'])
def inicio():
    if request.method == 'POST':
        usuario = request.form.get("usuario")
        contrasenia = request.form.get("passwd")

        passwd_extraida = extraer_usuario(usuario)
        
        if passwd_extraida:
            if passwd_extraida == contrasenia:
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

        passwd_extraida = extraer_usuario(nuevo_usuario)
        
        if not passwd_extraida:
            if contrasenia == verificar_contrasenia:
                crear_usuario(nuevo_usuario, contrasenia)
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
    if usuario_actual == "admin":
        frases_usuario= mostrar_frases()
    else:  
        frases_usuario = mostrar_frases(usuario_actual)
    return render_template("perfil.html", usuario=usuario_actual, frases=frases_usuario)

@app.route("/nueva_frase", methods=['GET'])
def nueva_frase():
    nueva_frase = request.args.get("nueva_frase")
    usuario_actual = session["usuario"]
    agregar_frase(nueva_frase, usuario_actual)
    
    flash("Frase añadida con éxito", "nueva frase")
    
    return redirect(url_for("perfil"))
    
@app.route("/logout")
def logout():
    session.clear()
    flash("Ha cerrado sesión con éxito", "cierre de sesión")
    return redirect(url_for("inicio"))

if __name__ == "__main__":
    app.run()