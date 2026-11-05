from flask import Flask, render_template, request, redirect, url_for, session, flash
from operaciones import mostrar_frases, extraer_usuario, crear_usuario, agregar_frase, mostrar_accesos, registrar_inicio_sesion, registrar_fin_sesion
import os, bcrypt, time
from datetime import timedelta
from dotenv import load_dotenv
from functools import wraps
from wtforms import Form, StringField, PasswordField
from wtforms.validators import InputRequired, Length, EqualTo, Regexp

class FormularioRegistro(Form):

    # Usuario obligatorio, entre 5 y 20 caracteres, sin espacios
    usuario = StringField("Nombre de usuario",                                  #El texto introducido al crear la instancia de cada objeto será la clade del objeto json de errores
              validators = [InputRequired(message="El usuario es obligatorio"),
                            Length(min=5, max=20, message="El usuario debe tener entre 5 y 20 caracteres"),
                            Regexp(r"^[A-Za-z0-9_]{5,20}$", message="Solo se permiten letras, números y guiones bajos")])

    # Contraseña de al menos 8 caracteres
    password = PasswordField("Contraseña",
               validators=[ InputRequired(message="La contraseña es obligatoria"),
                            Length(min=8, max=72, message="La contraseña debe tener al menos 8 caracteres")])

    # Confirmación de contraseña
    confirmar_password = PasswordField("Confirmar contraseña", 
                         validators=[InputRequired(message="Debe confirmar la contraseña"),
                                     EqualTo("password", message="Las contraseñas no coinciden")])

class FormularioFrases(Form):
    nueva_frase = StringField("Frases", validators=[
        InputRequired(message="La frase está vacía"),
        Length(min=10, max=100, message="La frase debe tener entre 10 y 100 caracteres")])

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("clave_secreta")
app.permanent_session_lifetime = timedelta(minutes=30)

def login_required(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if "usuario" not in session:
            flash("Debe iniciar sesión para acceder.")
            return redirect(url_for("inicio"))
        return f(*args, **kwargs)
    return decorada

@app.before_request
def controlar_inactividad():
    if request.endpoint in ("static", "logout"):
        return
    if "usuario" in session:
        ahora = time.time()
        if ahora - session.get("ultima_actividad", ahora) > session.get("tiempo_max", 60):
            if "id_sesion" in session:
                registrar_fin_sesion(session["id_sesion"], tipo_cierre="inactividad")
            session.clear()
            flash("La sesión ha expirado por inactividad.", "error")
            return redirect(url_for("inicio"))
        session["ultima_actividad"] = ahora
        session["tiempo_max"] = int(os.getenv("TIEMPO_MAX_INACTIVIDAD", 60)) 


# ----------------------------------
# Login
# ----------------------------------

@app.route("/")
@app.route("/login", methods=['GET','POST'])
def inicio():    
    if request.method == 'POST':
        usuario = request.form.get("usuario", "")
        contrasenia = request.form.get("passwd", "")
        
        contrasenia_bytes = contrasenia.encode("utf-8")
        stored_hash_bd = extraer_usuario(usuario)
        if not stored_hash_bd:
            flash("Usuario o contraseña incorrectos")
            return redirect(url_for("inicio"))
        
        
        stored_hash_bd_bytes = stored_hash_bd.encode("utf-8")
        
        if bcrypt.checkpw(contrasenia_bytes, stored_hash_bd_bytes):
            session.clear()
            
            session.permanent = True
            session["usuario"] = usuario
            flash("Ha iniciado sesión correctamente.")
            
            id_sesion = registrar_inicio_sesion(usuario)
            if id_sesion is not None:
                session["id_sesion"] = id_sesion
                
            session["tiempo_max"] = int(os.getenv("TIEMPO_MAX_INACTIVIDAD", 60))
            session["ultima_actividad"] = time.time()
            return redirect(url_for("perfil"))
        
        else:
            flash("Usuario o contraseña incorrectos")
            return redirect(url_for("inicio"))
                    
    if "usuario" in session:
        return redirect(url_for("perfil"))

    return render_template("index.html")


# ----------------------------------
# Registro de usuarios
# ----------------------------------

@app.route("/registro", methods=['GET','POST'])
def registro():
    
    if request.method == "GET":
        return render_template("registro.html")
    
    formulario = FormularioRegistro(request.form)
    
    if request.method == 'POST':
        if not formulario.validate():
            for campo, errores in formulario.errors.items():
                for error in errores:
                    flash(f"{error}", "error")
            return redirect(url_for("registro"))
            
            # return {"resultado": "Datos incorrectos", "errores": formulario.errors}
        
        # usuario = formulario.usuario.data
        # passwd = formulario.password.data
        # confirmar_password = formulario.confirmar_password.data
        
        usuario = request.form.get("usuario", "")
        password =  request.form.get("password", "")
        # confirmar_password = request.form.get("passwd_verificar", "") 
        
        if extraer_usuario(usuario):
            flash("El usuario ya existe.")
            return redirect(url_for("registro"))
        
        password_bytes = password.encode("utf-8")
        password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())        
        password_decode = password_hash.decode("utf-8")
                
        crear_usuario(usuario, password_decode)
        
        flash("¡Te has registrado con éxito! Ya puedes iniciar sesión.", "exito")
        return redirect(url_for("inicio"))
    
            
    return render_template("registro.html")

@app.route("/perfil", methods=['GET'])
@login_required
def perfil():
    
    usuario_actual = session["usuario"]
    sesiones = None
    
    if usuario_actual == "admin":
        frases_usuario= mostrar_frases()
        sesiones = mostrar_accesos()
    else:  
        frases_usuario = mostrar_frases(usuario_actual)
    
    return render_template("perfil.html", usuario=usuario_actual, frases=frases_usuario, sesiones=sesiones)

@app.route("/nueva_frase", methods=['POST'])
@login_required
def nueva_frase():
    
    formulario = FormularioFrases(request.form)
    if not formulario.validate():
        flash("La frase debe tener entre 10 y 100 caracteres.", "error")
        return redirect(url_for("perfil"))
    
    texto_frase =  formulario.nueva_frase.data 
    
    usuario_actual = session["usuario"]
    agregar_frase(texto_frase, usuario_actual)
    flash("Frase añadida con éxito", "nueva frase")
    
    return redirect(url_for("perfil"))
    
@app.route("/logout")
def logout():
    if "id_sesion" in session:
        registrar_fin_sesion(session["id_sesion"], tipo_cierre="voluntaria")
    session.clear()
    flash("Ha cerrado sesión con éxito", "cierre de sesión")
    return redirect(url_for("inicio"))

if __name__ == "__main__":
    app.run()