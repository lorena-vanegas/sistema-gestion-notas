from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import io
import sqlite3



def get_db_connection():
    conn = sqlite3.connect('instance/notas.db')
    conn.row_factory = sqlite3.Row
    return conn



# --- CONFIGURACIÓN DE LA BASE DE DATOS --- #
import os

app = Flask(__name__, instance_relative_config=True)

# Ruta base del proyecto
base_dir = os.path.abspath(os.path.dirname(__file__))

# Ruta completa a la base existente
db_path = os.path.join(base_dir, "instance", "notas.db")

# Mensajes de depuración para ver si apunta a la correcta
print("📍 Ruta esperada de la base:", db_path)
print("📂 ¿Existe la base?:", os.path.exists(db_path))

# Configuración de SQLAlchemy con la ruta correcta
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)



# Clave secreta para sesiones
app.secret_key = "mi_clave_secreta_super_segura_12345"

# 🔧 Configuración correcta de la base de datos
db_path = os.path.join(app.instance_path, "notas.db")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/notas.db'

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


from datetime import datetime

@app.context_processor
def inject_now():
    return {'now': datetime.now}





class Docente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    asignatura = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), nullable=True)
    telefono = db.Column(db.String(20), nullable=False)
# -------------------
# Modelo Estudiante
# -------------------
class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    tipo_documento = db.Column(db.String(50), nullable=False)
    numero_documento = db.Column(db.String(50), unique=True, nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(50))
    grado = db.Column(db.String(20), nullable=False)
    sede = db.Column(db.String(100))
    genero = db.Column(db.String(20))
    estrato = db.Column(db.String(10))
    sisben = db.Column(db.String(10))
    eps = db.Column(db.String(100))
    tipo_sangre = db.Column(db.String(5))
    discapacidad = db.Column(db.String(10))
    cual_discapacidad = db.Column(db.String(200))
    
    # CREAR TABLAS
with app.app_context():
    db.create_all()
    # Agregar columna si no existe (SQLite solo permite agregar columnas, no borrar)
    try:
        db.engine.execute("ALTER TABLE estudiante ADD COLUMN horas_por_semana INTEGER DEFAULT 0;")
    except:
        pass  # ya existe, no hace nada
class Materia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_materia= db.Column(db.String(100), nullable=False)
    horas_por_semana = db.Column(db.Integer, nullable=False)

class Logro(db.Model):
    __tablename__ = "logro"

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(200), nullable=False)
    materia = db.Column(db.String(100), nullable=False)
    periodo = db.Column(db.String(20), nullable=False)  # Ej: "1", "2", "3"
    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiante.id"))
    estudiante = db.relationship("Estudiante", backref="logros")

    
class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiante.id'), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'), nullable=False)
    periodo = db.Column(db.Integer, nullable=False)  # 1, 2, 3
    nota = db.Column(db.Float, nullable=False)

    estudiante = db.relationship('Estudiante', backref=db.backref('notas', lazy=True))
    materia = db.relationship('Materia', backref=db.backref('notas', lazy=True))
    
    @property
    def desempeño(self):
        if 1.0 <= self.nota <= 2.9:
            return "Bajo"
        elif 3.0 <= self.nota <= 3.9:
            return "Básico"
        elif 4.0 <= self.nota <= 4.5:
            return "Alto"
        elif 4.6 <= self.nota <= 5.0:
            return "Superior"
        else:
            return "N/A"
    
    
    
# -------------------
# Ruta Home
# ------------------

@app.route("/")
def index():
    if "usuario" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/home")
def home():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("home.html")
    
    # 🔹 Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        contraseña = request.form["contraseña"]
        if usuario == "admin" and contraseña == "1234":  # ejemplo
            session["usuario"] = usuario
            flash("Bienvenido ✅")
            return redirect(url_for("home"))
        else:
            flash("Usuario o contraseña incorrectos ❌")
    return render_template("login.html")

# 🔹 Logout
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Has cerrado sesión ✅")
    return redirect(url_for("login"))

# -------------------
# Ruta Estudiantes
# -------------------
# 📌 LISTAR ESTUDIANTES
@app.route("/estudiantes")
def listar_estudiantes():
    if "usuario" not in session:
        return redirect(url_for("login"))
    estudiantes = Estudiante.query.all()
    return render_template("estudiantes.html", estudiantes=estudiantes)

@app.route("/estudiantes/agregar", methods=["GET", "POST"])
def agregar_estudiante():
    if request.method == "POST":
        try:
            from datetime import datetime

            nombre = request.form["nombre"]
            apellido = request.form["apellido"]
            tipo_documento = request.form["tipo_documento"]
            numero_documento = request.form["numero_documento"]

            # convertir fecha
            fecha_str = request.form["fecha_nacimiento"]
            fecha_nacimiento = datetime.strptime(fecha_str, "%Y-%m-%d").date()

            direccion = request.form.get("direccion")
            telefono = request.form.get("telefono")
            grado = request.form["grado"]
            sede = request.form.get("sede")
            genero = request.form["genero"]
            estrato = request.form.get("estrato")
            sisben = request.form.get("sisben")
            eps = request.form.get("eps")
            tipo_sangre = request.form["tipo_sangre"]
            discapacidad = request.form["discapacidad"]
            cual_discapacidad = request.form.get("cual_discapacidad")

            nuevo = Estudiante(
                nombre=nombre,
                apellido=apellido,
                tipo_documento=tipo_documento,
                numero_documento=numero_documento,
                fecha_nacimiento=fecha_nacimiento,
                direccion=direccion,
                telefono=telefono,
                grado=grado,
                sede=sede,
                genero=genero,
                estrato=estrato,
                sisben=sisben,
                eps=eps,
                tipo_sangre=tipo_sangre,
                discapacidad=discapacidad,
                cual_discapacidad=cual_discapacidad,
            )
            db.session.add(nuevo)
            db.session.commit()
            flash("✅ Estudiante agregado correctamente")
            return redirect(url_for("listar_estudiantes"))
        except Exception as e:
            flash(f"❌ Error al guardar estudiante: {e}")

    return render_template("estudiantes.html")



# 📌 EDITAR ESTUDIANTE
@app.route("/estudiantes/editar/<int:id>", methods=["GET", "POST"])
def editar_estudiante(id):
    estudiante = Estudiante.query.get_or_404(id)
    if request.method == "POST":
        estudiante.nombre = request.form["nombre"]
        estudiante.apellido = request.form["apellido"]
        estudiante.tipo_documento = request.form["tipo_documento"]
        estudiante.numero_documento = request.form["numero_documento"]
        fecha_str = request.form["fecha_nacimiento"]
        estudiante.fecha_nacimiento = datetime.strptime(fecha_str, "%Y-%m-%d").date() 
        estudiante.direccion = request.form["direccion"]
        estudiante.telefono = request.form["telefono"]
        estudiante.grado = request.form["grado"]
        estudiante.sede = request.form["sede"]
        estudiante.genero = request.form["genero"]
        estudiante.estrato = request.form["estrato"]
        estudiante.sisben = request.form["sisben"]
        estudiante.eps = request.form["eps"]
        estudiante.tipo_sangre = request.form["tipo_sangre"]
        estudiante.discapacidad = request.form["discapacidad"]
        estudiante.cual_discapacidad = request.form["cual_discapacidad"]

        db.session.commit()
        return redirect(url_for("listar_estudiantes"))

    # 👇 aquí pasamos estudiante al template
    return render_template("editar_estudiante.html", estudiante=estudiante)


# 📌 ELIMINAR ESTUDIANTE
@app.route("/estudiantes/eliminar/<int:id>")
def eliminar_estudiante(id):
    if "usuario" not in session:
        return redirect(url_for("login"))
    estudiante = Estudiante.query.get_or_404(id)
    db.session.delete(estudiante)
    db.session.commit()
    flash("🗑️ Estudiante eliminado correctamente")
    return redirect(url_for("listar_estudiantes"))



# --------------------
# DOCENTES
# --------------------
@app.route("/docentes", methods=["GET", "POST"])
def docentes():
    if "usuario" not in session:
        return redirect(url_for("login"))

    # Agregar nuevo docente
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        asignatura = request.form["asignatura"]
        correo = request.form.get("correo")
        telefono = request.form.get("telefono")

        nuevo_docente = Docente(
            nombre=nombre,
            apellido=apellido,
            asignatura=asignatura,
            correo=correo,
            telefono=telefono
        )
        db.session.add(nuevo_docente)
        db.session.commit()
        flash("✅ Docente agregado correctamente")
        return redirect(url_for("docentes"))

    # Mostrar lista de docentes
    docentes_lista = Docente.query.all()
    return render_template("docentes.html", docentes=docentes_lista)


@app.route("/docentes")
def listar_docentes():
    if "usuario" not in session:   # protección de login
        return redirect(url_for("login"))
    docentes = Docente.query.all()
    return render_template("docentes.html", docentes=docentes)


@app.route("/docentes/eliminar/<int:id>")
def eliminar_docente(id):
    if "usuario" not in session:
        return redirect(url_for("login"))
    docente = Docente.query.get_or_404(id)
    db.session.delete(docente)
    db.session.commit()
    flash("🗑️ Docente eliminado correctamente")
    return redirect(url_for("listar_docentes"))


@app.route("/docentes/editar/<int:id>", methods=["GET", "POST"])
def editar_docente(id):
    if "usuario" not in session:
        return redirect(url_for("login"))
        
    docente = Docente.query.get_or_404(id)

    if request.method == "POST":
        docente.nombre = request.form["nombre"]
        docente.apellido = request.form["apellido"]
        docente.correo = request.form["correo"]
        docente.telefono = request.form["telefono"]
        docente.asignatura = request.form["asignatura"]

        db.session.commit()
        flash("Docente actualizado correctamente ✅")
        return redirect(url_for("listar_docentes"))

    return render_template("editar_docente.html", docente=docente)


# -------------------------------
# Materias
# -------------------------------

@app.route("/materias")
def listar_materias():
    materias = Materia.query.all()
    return render_template("materias.html", materias=materias)

@app.route("/materias/agregar", methods=["GET", "POST"])
def agregar_materia():
    if request.method == "POST":
        nombre_materia = request.form["nombre_materia"]
        horas_por_semana = int(request.form["horas_por_semana"])
        
        
        nueva = Materia(nombre_materia=nombre_materia, horas_por_semana=horas_por_semana)
        db.session.add(nueva)
        db.session.commit()
        flash("✅ Materia agregada correctamente")
        return redirect(url_for("listar_materias"))
    
    return render_template("agregar_materia.html")

@app.route("/materias/editar/<int:id>", methods=["GET", "POST"])
def editar_materia(id):
    materia = Materia.query.get_or_404(id)
    if request.method == "POST":
        materia.nombre_materia = request.form["nombre_materia"]
        materia.horas_por_semana = int(request.form["horas_por_semana"])
        db.session.commit()
        flash("✏️ Materia actualizada correctamente")
        return redirect(url_for("listar_materias"))
    return render_template("editar_materia.html", materia=materia)

@app.route("/materias/eliminar/<int:id>")
def eliminar_materia(id):
    materia = Materia.query.get_or_404(id)
    db.session.delete(materia)
    db.session.commit()
    flash("🗑️ Materia eliminada correctamente")
    return redirect(url_for("listar_materias"))


# -------------------------------
# Logros
# -------------------------------

# 👉 Listar y agregar logros
@app.route('/logros', methods=['GET', 'POST'])
def listar_logros():
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        materia = request.form['materia']
        periodo = request.form['periodo']

        nuevo = Logro(descripcion=descripcion, materia=materia, periodo=periodo)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('listar_logros'))

    logros = Logro.query.all()
    return render_template('logros.html', logros=logros)

# 👉 Editar logro
@app.route('/logros/editar/<int:id>', methods=['GET', 'POST'])
def editar_logro(id):
    logro = Logro.query.get_or_404(id)

    if request.method == 'POST':
        logro.descripcion = request.form['descripcion']
        logro.materia = request.form['materia']
        logro.periodo = request.form['periodo']
        db.session.commit()
        return redirect(url_for('listar_logros'))

    return render_template('editar_logro.html', logro=logro)

# 👉 Eliminar logro
@app.route('/logros/eliminar/<int:id>')
def eliminar_logro(id):
    logro = Logro.query.get_or_404(id)
    db.session.delete(logro)
    db.session.commit()
    return redirect(url_for('listar_logros'))

# -------------------------------
# Notas
# -------------------------------
# ----------------- NOTAS -----------------
@app.route("/notas")
def listar_notas():
    notas = Nota.query.all()
    estudiantes = Estudiante.query.all()
    materias = Materia.query.all()
    return render_template("notas.html", notas=notas, estudiantes=estudiantes, materias=materias)


@app.route("/notas/agregar", methods=["GET", "POST"])
def agregar_nota():
    estudiantes = Estudiante.query.all()
    materias = Materia.query.all()

    if request.method == "POST":
        estudiante_id = int(request.form["estudiante_id"])
        materia_id = int(request.form["materia_id"])
        periodo = int(request.form["periodo"])
        nota_valor = float(request.form["nota"])

        # Guardar nota
        nueva_nota = Nota(
            estudiante_id=estudiante_id,
            materia_id=materia_id,
            periodo=periodo,
            nota=nota_valor
        )
        db.session.add(nueva_nota)
        db.session.commit()

        flash("✅ Nota agregada correctamente.")
        return redirect(url_for("listar_notas"))

    return render_template("notas.html", estudiantes=estudiantes, materias=materias)


@app.route("/editar_nota/<int:id>", methods=["GET", "POST"])
def editar_nota(id):
    conn = get_db_connection()

    # Buscar la nota junto con los datos del estudiante y materia
    nota = conn.execute("""
        SELECT n.id, n.estudiante_id, n.materia_id, n.periodo, n.nota,
            e.nombre AS nombre_estudiante, e.apellido AS apellido_estudiante,
            m.nombre_materia AS nombre_materia, n.periodo, n.nota
        FROM nota n
        JOIN estudiante e ON n.estudiante_id = e.id
        JOIN materia m ON n.materia_id = m.id
        WHERE n.id = ?
    """, (id,)).fetchone()

    estudiantes = conn.execute("SELECT * FROM estudiante").fetchall()
    materias = conn.execute("SELECT * FROM materia").fetchall()

    if request.method == "POST":
        estudiante_id = request.form["estudiante_id"]
        materia_id = request.form["materia_id"]
        periodo = request.form["periodo"]
        nueva_nota = float(request.form["nota"])

        conn.execute("""
            UPDATE nota
            SET estudiante_id = ?, materia_id = ?, periodo = ?, nota = ?
            WHERE id = ?
        """, (estudiante_id, materia_id, periodo, nueva_nota, id))
        conn.commit()
        conn.close()

        return redirect(url_for("listar_notas"))

    conn.close()
    return render_template("editar_nota.html", nota=nota, estudiantes=estudiantes, materias=materias)




@app.route("/eliminar_nota/<int:id>")
def eliminar_nota(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM nota WHERE id = ?", (id,))  # ← corregido aquí también
    conn.commit()
    conn.close()
    return redirect(url_for("listar_notas"))


#reportessssss

from flask import render_template, request, send_file
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from datetime import datetime

# --- 1️⃣ Página principal de reportes ---
@app.route('/reportes', methods=['GET', 'POST'])
def reportes():
    conn = get_db_connection()
    estudiantes = conn.execute("SELECT * FROM estudiante").fetchall()
    conn.close()

    selected_estudiante = request.form.get('estudiante_id')
    periodo = request.form.get('periodo')

    return render_template(
        'reportes.html',
        estudiantes=estudiantes,
        selected_estudiante=selected_estudiante,
        periodo=periodo
    )


from datetime import datetime


from flask import render_template
from datetime import datetime
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('instance/notas.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/reporte_estudiante/<int:estudiante_id>/<int:periodo>')
def reporte_estudiante(estudiante_id, periodo):
    conn = get_db_connection()

    # Traer estudiante
    estudiante = conn.execute(
        'SELECT * FROM estudiante WHERE id = ?',
        (estudiante_id,)
    ).fetchone()

    # Traer materias, notas y logros generales
    datos_raw = conn.execute('''
        SELECT 
            m.nombre_materia AS materia,
            n.nota AS nota,
            COALESCE(l.descripcion, '') AS logro
        FROM materia m
        LEFT JOIN nota n 
            ON n.materia_id = m.id 
            AND n.estudiante_id = ?
            AND n.periodo = ?
        LEFT JOIN logro l
            ON l.materia = m.nombre_materia
            AND l.periodo = ?
        ORDER BY m.nombre_materia
    ''', (estudiante_id, periodo, periodo)).fetchall()

    conn.close()

    # Convertir a lista de diccionarios y agregar desempeño
    datos = []
    for fila in datos_raw:
        nota = fila['nota'] if fila['nota'] is not None else 0
        
        if nota <= 2.9:
            desempeño = "Bajo"
        elif nota <= 3.9:
            desempeño = "Básico"
        elif nota <= 4.5:
            desempeño = "Alto"
        else:
            desempeño = "Superior"
        
        datos.append({
            'materia': fila['materia'],
            'nota': nota,
            'logro': fila['logro'],
            'desempeño': desempeño
        })

    # Promedio
    promedio = round(sum([fila['nota'] for fila in datos]) / len(datos), 2) if datos else 0

    # Fecha de generación
    fecha_generacion = datetime.now().strftime("%d/%m/%Y")

    # Renderizar template
    return render_template(
        "reporte_estudiante.html",
        estudiante=estudiante,
        datos=datos,  # <-- usamos esta variable en el template
        periodo=periodo,
        fecha_generacion=fecha_generacion,
        promedio=promedio
    )



# --- 3️⃣ Descargar PDF del reporte ---
@app.route("/descargar_pdf/<int:estudiante_id>/<periodo>")
def descargar_pdf(estudiante_id, periodo):
    conn = get_db_connection()

    estudiante = conn.execute(
        "SELECT * FROM estudiante WHERE id = ?", (estudiante_id,)
    ).fetchone()

    if not estudiante:
        conn.close()
        return "❌ Estudiante no encontrado", 404

    if periodo == "final":
        datos = conn.execute('''
        SELECT 
            m.nombre_materia AS materia,
            ROUND(AVG(n.nota), 1) AS nota,
            '-' AS logro
        FROM nota n
        JOIN materia m ON n.materia_id = m.id
        WHERE n.estudiante_id = ?
        GROUP BY m.nombre_materia
    ''', (estudiante_id,)).fetchall()
    else:
        datos = conn.execute('''
        SELECT 
            m.nombre_materia AS materia,
            COALESCE(l.descripcion, 'Sin logro') AS logro,
            n.nota AS nota
        FROM nota n
        JOIN materia m ON n.materia_id = m.id
        LEFT JOIN logro l 
            ON (l.materia = CAST(m.id AS TEXT) OR l.materia = m.nombre_materia)
            AND l.periodo = n.periodo
            AND l.estudiante_id = n.estudiante_id
        WHERE n.estudiante_id = ? AND n.periodo = ?
    ''', (estudiante_id, periodo)).fetchall()


    conn.close()

    # Crear PDF en memoria
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título
    elements.append(Paragraph(f"<b>REPORTE ACADÉMICO - PERIODO {periodo.upper()}</b>", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Estudiante:</b> {estudiante['nombre']} {estudiante['apellido']} &nbsp;&nbsp;&nbsp; <b>Grado:</b> {estudiante['grado']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y')}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Tabla
    data = [["Materia", "Logro", "Nota", "Desempeño"]]

    for fila in nota:
        nota = fila["nota"]
        logro = fila["descripcion"]
        if nota < 3:
            desempeño = "Bajo"
        elif nota < 4:
            desempeño = "Básico"
        elif nota <= 4.5:
            desempeño = "Alto"
        else:
            desempeño = "Superior"
        data.append([fila["nombre_materia"], logro, nota, desempeño])

    table = Table(data, colWidths=[130, 240, 60, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(table)

    elements.append(Spacer(1, 40))
    elements.append(Paragraph("<b>Firma Docente Director:</b> ____________________", styles["Normal"]))
    elements.append(Paragraph("<b>Firma Rector(a):</b> ____________________", styles["Normal"]))

    pdf.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="reporte_estudiante.pdf", mimetype="application/pdf")






if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

