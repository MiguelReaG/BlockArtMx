# app.py
import os
import hashlib
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from flask import send_from_directory
import smtplib
from email.message import EmailMessage


from blockchain import Blockchain

# ----------------- Configuración básica -----------------

app = Flask(__name__)
app.secret_key = "super_secret_key_para_demo"  # cámbiala

# MySQL 
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "baldrat"          
app.config["MYSQL_DB"] = "registro_ip_blockchain"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# Blockchain
blockchain = Blockchain()

# Carpeta de subida de archivos
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------- Configuración de correo -----------------

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = "blockartmx@gmail.com"    
EMAIL_PASS = "thgwoznfwrleffqd"

ADMIN_EMAIL = EMAIL_USER

# ----------------- Helpers -----------------

def hash_contraseña(plaintext):
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Necesitas iniciar sesión.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


def calcular_hash_archivo(ruta_completa):
    sha = hashlib.sha256()
    with open(ruta_completa, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()

def enviar_correo_bienvenida(destinatario, nombre):
    """
    Envía un correo HTML de bienvenida al usuario
    y una copia oculta al admin de BlockArtMx.
    """
    msg = EmailMessage()
    msg["Subject"] = "🎨 Bienvenido a BlockArtMx – Registro exitoso"
    msg["From"] = f"BlockArtMx <{EMAIL_USER}>"
    msg["To"] = destinatario

    LOGO_URL = "https://raw.githubusercontent.com/MiguelReaG/BlockArtMx/main/blockartmx_Logo.png"  # pon aquí la URL pública de tu logo

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f7; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">

            <div style="text-align: center;">
                <img src="{LOGO_URL}" alt="BlockArtMx" style="width: 150px; margin-bottom: 20px;">
            </div>

            <h2 style="color: #111827; text-align: center;">Bienvenido a BlockArtMx 🎉</h2>

            <p>Hola <strong>{nombre}</strong>,</p>

            <p>
                Tu cuenta ha sido registrada correctamente en <strong>BlockArtMx</strong>, 
                la plataforma donde puedes proteger tus obras digitales usando tecnología blockchain.
            </p>

            <h3 style="color:#1f2937;">¿Qué puedes hacer ahora?</h3>
            <ul>
                <li>📁 Registrar nuevas obras digitales (imágenes, música, PDFs y más).</li>
                <li>🔐 Obtener una prueba criptográfica de autoría (hash + bloque blockchain).</li>
                <li>🧾 Consultar tu biblioteca personal de obras registradas.</li>
                <li>🔍 Verificar integridad y detectar alteraciones en segundos.</li>
            </ul>

            <p>
                Este correo se generó de manera automática como parte del proyecto 
                de Criptografía. Si no fuiste tú quien creó la cuenta,
                puedes ignorar este mensaje.
            </p>

            <br>
            <p style="text-align:center; color:#6b7280;">
                — Equipo de BlockArtMx<br>
                Sistema de Registro de Propiedad Intelectual en Blockchain
            </p>

        </div>
    </body>
    </html>
    """

    texto_plano = f"""
Bienvenido a BlockArtMx

Hola {nombre},

Tu cuenta se registró correctamente en BlockArtMx.

Ahora puedes:
- Iniciar sesión.
- Registrar tus obras digitales.
- Obtener evidencia criptográfica (hash + bloque blockchain).
- Verificar la integridad de tus archivos.

Saludos,
Equipo BlockArtMx
"""

    msg.set_content(texto_plano)
    msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"[EMAIL] Correo HTML enviado a {destinatario} (copia a admin {ADMIN_EMAIL})")
    except Exception as e:
        print(f"[EMAIL] Error al enviar correo: {e}")
   
def enviar_correo_admin_nuevo_usuario(id_usuario, nombre, correo, ip_cliente):
    """
    Notifica al admin que se ha registrado un nuevo usuario en BlockArtMx.
    """
    msg = EmailMessage()
    msg["Subject"] = "👤 Nuevo usuario registrado en BlockArtMx"
    msg["From"] = f"BlockArtMx <{EMAIL_USER}>"
    msg["To"] = ADMIN_EMAIL

    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cuerpo_texto = f"""
Nuevo usuario registrado en BlockArtMx

ID de usuario: {id_usuario}
Nombre: {nombre}
Correo: {correo}
Fecha/hora de registro: {fecha_registro}
IP (aprox): {ip_cliente or 'No disponible'}

Este mensaje se genera automáticamente como parte del sistema de auditoría del proyecto.
"""

    cuerpo_html = f"""
<html>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f7; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.08);">
    <h2 style="margin-top:0; color:#111827;">Nuevo usuario registrado en BlockArtMx</h2>

    <p><strong>ID de usuario:</strong> {id_usuario}</p>
    <p><strong>Nombre:</strong> {nombre}</p>
    <p><strong>Correo:</strong> {correo}</p>
    <p><strong>Fecha/hora de registro:</strong> {fecha_registro}</p>
    <p><strong>IP (aprox):</strong> {ip_cliente or 'No disponible'}</p>

    <hr style="margin: 1.5rem 0; border:none; border-top:1px solid #e5e7eb;">

    <p style="font-size: 0.85rem; color:#6b7280;">
      Este correo forma parte del mecanismo de auditoría del proyecto de Criptografía.
    </p>
  </div>
</body>
</html>
"""

    msg.set_content(cuerpo_texto)
    msg.add_alternative(cuerpo_html, subtype="html")

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"[EMAIL] Notificación de nuevo usuario enviada al admin ({ADMIN_EMAIL})")
    except Exception as e:
        print(f"[EMAIL] Error al enviar correo al admin: {e}")

#--------------Correo Obra Registrada----------------

def enviar_correo_obra_registrada(destinatario, nombre_autor, titulo_obra,
                                  id_obra, hash_archivo, id_bloque,
                                  url_archivo, es_imagen):
    """
    Envía un correo al autor cuando registra una nueva obra en BlockArtMx.
    Incluye hash, ID de bloque y vista previa si es imagen.
    """
    msg = EmailMessage()
    msg["Subject"] = f"✅ Tu obra '{titulo_obra}' ha sido registrada en BlockArtMx"
    msg["From"] = f"BlockArtMx <{EMAIL_USER}>"
    msg["To"] = destinatario

    LOGO_URL = "https://raw.githubusercontent.com/MiguelReaG/BlockArtMx/main/blockartmx_Logo.png"  # usa la misma que en el otro correo

    # Versión texto plano (fallback)
    texto_plano = f"""
Hola {nombre_autor},

Tu obra '{titulo_obra}' ha sido registrada correctamente en BlockArtMx.

Detalles:
- ID de la obra: {id_obra}
- Hash del archivo: {hash_archivo}
- ID de bloque en la blockchain: {id_bloque}
- Enlace al archivo: {url_archivo}

Puedes ingresar a la aplicación web para ver más detalles y verificar la integridad de tus obras.

Saludos,
Equipo BlockArtMx
"""

    # Versión HTML
    preview_html = ""
    if es_imagen:
        preview_html = f"""
        <div style="margin-top: 15px; text-align:center;">
            <p style="font-size:0.9rem; color:#6b7280; margin-bottom:8px;">
                Vista previa de la obra:
            </p>
            <img src="{url_archivo}" alt="Vista previa de la obra"
                 style="max-width: 100%; max-height: 300px; border-radius: 8px; border:1px solid #e5e7eb;">
        </div>
        """
    else:
        preview_html = f"""
        <p style="margin-top: 15px;">
            Puedes abrir el archivo desde este enlace:
            <a href="{url_archivo}" target="_blank">{url_archivo}</a>
        </p>
        """

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f7; padding: 20px;">
      <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.08);">

        <div style="text-align:center;">
            <img src="{LOGO_URL}" alt="BlockArtMx" style="width: 140px; margin-bottom: 16px;">
        </div>

        <h2 style="margin-top:0; color:#111827; text-align:center;">
            Tu obra ha sido registrada en BlockArtMx 🎨
        </h2>

        <p>Hola <strong>{nombre_autor}</strong>,</p>

        <p>
            Tu obra <strong>'{titulo_obra}'</strong> ha sido registrada correctamente en
            <strong>BlockArtMx</strong>. Estos son los detalles técnicos de la certificación:
        </p>

        <ul>
            <li><strong>ID de la obra:</strong> {id_obra}</li>
            <li><strong>Hash del archivo:</strong> <code style="font-size:0.8rem;">{hash_archivo}</code></li>
            <li><strong>ID de bloque en la blockchain:</strong> {id_bloque}</li>
        </ul>

        {preview_html}

        <p style="margin-top: 20px;">
            Esta información te sirve como evidencia criptográfica de autoría,
            ya que el hash del archivo y el bloque en la cadena permiten detectar
            cualquier alteración futura del contenido.
        </p>

        <p style="font-size:0.85rem; color:#6b7280; margin-top: 20px; text-align:center;">
            — Equipo BlockArtMx<br>
            Sistema de Registro de Propiedad Intelectual en Blockchain
        </p>

      </div>
    </body>
    </html>
    """

    msg.set_content(texto_plano)
    msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"[EMAIL] Correo de obra registrada enviado a {destinatario}")
    except Exception as e:
        print(f"[EMAIL] Error al enviar correo de obra registrada: {e}")


# ----------------- Rutas de autenticación -----------------


@app.route("/")
def index():
    # Mostrar cadena para efectos demo
    cadena = blockchain.mostrar_cadena()
    return render_template("index.html", cadena=cadena)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        contraseña = request.form["contraseña"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", (correo,))
        existe = cur.fetchone()
        if existe:
            flash("El correo ya está registrado.", "danger")
            return redirect(url_for("register"))

        contraseña_hash = hash_contraseña(contraseña)
        cur.execute(
            "INSERT INTO usuarios (nombre, correo, contraseña_hash) VALUES (%s, %s, %s)",
            (nombre, correo, contraseña_hash),
        )
        mysql.connection.commit()

        # Enviar correo de bienvenida (no bloqueante para la app, pero sí dentro de try)
        enviar_correo_bienvenida(correo, nombre)

        flash("Usuario registrado. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("login"))


    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        contraseña = request.form["contraseña"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
        user = cur.fetchone()

        if user and user["contraseña_hash"] == hash_contraseña(contraseña):
            session["user_id"] = user["id_usuario"]
            session["user_nombre"] = user["nombre"]
            session["user_rol"] = user["rol"]
            flash("Sesión iniciada.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Correo o contraseña incorrectos.", "danger")
            return redirect(url_for("login"))

    # SIEMPRE que sea GET (o cualquier caso que no entre al POST)
    # regresamos el template:
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("index"))


# ----------------- Rutas del creador -----------------


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/obras/nueva", methods=["GET", "POST"])
@login_required
def nueva_obra():
    if request.method == "POST":
        titulo = request.form["titulo"]
        descripcion = request.form.get("descripcion", "")
        tipo = request.form.get("tipo", "")
        fecha_creacion = request.form.get("fecha_creacion")

        archivo = request.files.get("archivo")
        if not archivo or archivo.filename == "":
            flash("Debes seleccionar un archivo de la obra.", "danger")
            return redirect(url_for("nueva_obra"))

        if not allowed_file(archivo.filename):
            flash("Tipo de archivo no permitido.", "danger")
            return redirect(url_for("nueva_obra"))

        filename_seguro = secure_filename(archivo.filename)
        # Opcional: subcarpeta por usuario
        subdir = os.path.join(app.config["UPLOAD_FOLDER"], f"user_{session['user_id']}")
        os.makedirs(subdir, exist_ok=True)

        filename_seguro = secure_filename(archivo.filename)

        # Ruta RELATIVA para la BD (siempre con / para que funcione en la URL)
        ruta_relativa = f"user_{session['user_id']}/{filename_seguro}"

        # Ruta FÍSICA en disco (aquí sí usamos os.path.join con la carpeta real)
        ruta_fisica = os.path.join(subdir, filename_seguro)

        # Guardar archivo
        archivo.save(ruta_fisica)

        # Hash usando ruta_fisica
        hash_archivo = calcular_hash_archivo(ruta_fisica)



        # 2) Insertar en DB primero
        cur = mysql.connection.cursor()
        cur.execute(
            """
            INSERT INTO obras (id_usuario, titulo, descripcion, tipo, fecha_creacion, ruta_archivo, hash_archivo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session["user_id"],
                titulo,
                descripcion,
                tipo,
                fecha_creacion,
                ruta_relativa,  
                hash_archivo,
            ),
        )

        mysql.connection.commit()
        id_obra = cur.lastrowid

        # 3) Crear bloque en la blockchain
        datos_bloque = (
            f"AutorID: {session['user_id']} | ObraID: {id_obra} | "
            f"Titulo: {titulo} | HashArchivo: {hash_archivo}"
        )
        bloque = blockchain.agregar_bloque(datos_bloque)

        # 4) Actualizar la obra con el id del bloque
        cur.execute(
            "UPDATE obras SET id_bloque_blockchain = %s WHERE id_obra = %s",
            (bloque.id, id_obra),
        )
        mysql.connection.commit()

        # 5) Obtener datos del autor para el correo
        cur.execute(
            "SELECT nombre, correo FROM usuarios WHERE id_usuario = %s",
            (session["user_id"],),
        )
        autor = cur.fetchone()
        nombre_autor = autor["nombre"]
        correo_autor = autor["correo"]

        # 6) Construir URL absoluta del archivo para el correo
        url_archivo = url_for("ver_archivo", ruta=ruta_relativa, _external=True)

        # 7) Detectar si el archivo es imagen para la miniatura
        ext = filename_seguro.lower().rsplit(".", 1)[-1]
        es_imagen = ext in ["png", "jpg", "jpeg", "gif"]

        # 8) Enviar correo de confirmación de obra registrada
        enviar_correo_obra_registrada(
            destinatario=correo_autor,
            nombre_autor=nombre_autor,
            titulo_obra=titulo,
            id_obra=id_obra,
            hash_archivo=hash_archivo,
            id_bloque=bloque.id,
            url_archivo=url_archivo,
            es_imagen=es_imagen,
        )

        flash("Obra registrada y anclada en la blockchain.", "success")
        return redirect(url_for("mis_obras"))

    return render_template("nueva_obra.html")


@app.route("/obras/mias")
@login_required
def mis_obras():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM obras WHERE id_usuario = %s ORDER BY creado_en DESC",
        (session["user_id"],),
    )
    obras = cur.fetchall()
    return render_template("mis_obras.html", obras=obras)


@app.route("/obras/<int:id_obra>")
@login_required
def detalle_obra(id_obra):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT o.*, u.nombre AS autor_nombre "
        "FROM obras o JOIN usuarios u ON o.id_usuario = u.id_usuario "
        "WHERE id_obra = %s",
        (id_obra,),
    )
    obra = cur.fetchone()
    if not obra:
        flash("Obra no encontrada.", "warning")
        return redirect(url_for("mis_obras"))

    bloque = None
    if obra["id_bloque_blockchain"]:
        bloque = blockchain.obtener_bloque_por_id(obra["id_bloque_blockchain"])

    return render_template("detalle_obra.html", obra=obra, bloque=bloque)

@app.route("/uploads/<path:ruta>")
def ver_archivo(ruta):
    """
    Sirve archivos desde la carpeta de uploads.
    'ruta' es algo como: user_3/imagen.png
    """
    return send_from_directory(app.config["UPLOAD_FOLDER"], ruta)




# ----------------- Verificación pública -----------------


@app.route("/verificar", methods=["GET", "POST"])
def verificar():
    obra = None
    bloque = None
    es_valida_cadena = None
    errores_cadena = []
    resultado_archivo = None

    if request.method == "POST":
        id_obra = request.form.get("id_obra")
        archivo = request.files.get("archivo")

        if id_obra:
            try:
                id_obra_int = int(id_obra)
            except ValueError:
                flash("El ID de la obra debe ser un número.", "danger")
                return redirect(url_for("verificar"))

            cur = mysql.connection.cursor()
            cur.execute(
                "SELECT o.*, u.nombre AS autor_nombre "
                "FROM obras o JOIN usuarios u ON o.id_usuario = u.id_usuario "
                "WHERE id_obra = %s",
                (id_obra_int,),
            )
            obra = cur.fetchone()
            if obra and obra["id_bloque_blockchain"]:
                bloque = blockchain.obtener_bloque_por_id(obra["id_bloque_blockchain"])

            # Verificar archivo si fue subido
            if archivo and archivo.filename != "":
                if not allowed_file(archivo.filename):
                    flash("Tipo de archivo no permitido.", "danger")
                else:
                    # Guardar temporalmente o leer en memoria
                    filename_seguro = secure_filename(archivo.filename)
                    temp_path = os.path.join(app.config["UPLOAD_FOLDER"], filename_seguro)
                    archivo.save(temp_path)
                    hash_subido = calcular_hash_archivo(temp_path)
                    os.remove(temp_path)

                    if obra and hash_subido == obra["hash_archivo"]:
                        resultado_archivo = "OK"
                    else:
                        resultado_archivo = "NO"

            # Verificar integridad de toda la cadena
            es_valida_cadena, errores_cadena = blockchain.verificar_cadena()

    return render_template(
        "verificar.html",
        obra=obra,
        bloque=bloque,
        es_valida_cadena=es_valida_cadena,
        errores_cadena=errores_cadena,
        resultado_archivo=resultado_archivo,
    )


# ----------------- Simulación de ataque -----------------


@app.route("/simular_ataque", methods=["GET", "POST"])
@login_required
def simular_ataque():
    # opcional: podrías restringirlo a rol admin
    cadena = blockchain.mostrar_cadena()
    if request.method == "POST":
        id_bloque = int(request.form["id_bloque"])
        ok = blockchain.simular_ataque_modificando_bloque(id_bloque)
        if ok:
            flash(f"Bloque {id_bloque} alterado (ataque simulado).", "warning")
        else:
            flash("No se encontró ese bloque.", "danger")
        return redirect(url_for("simular_ataque"))

    return render_template("simular_ataque.html", cadena=cadena)


if __name__ == "__main__":
    app.run(debug=True)
