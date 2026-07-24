from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    tipo_documento = db.Column(db.String(50), nullable=False)
    numero_documento = db.Column(db.String(50), nullable=False, unique=True)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    direccion = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(50), nullable=False)
    grado = db.Column(db.String(50), nullable=False)
    sede = db.Column(db.String(100), nullable=False)
    genero = db.Column(db.String(20), nullable=False)
    estrato = db.Column(db.String(20), nullable=False)
    sisben = db.Column(db.String(20), nullable=False)
    eps = db.Column(db.String(100), nullable=False)
    tipo_sangre = db.Column(db.String(10), nullable=False)
    discapacidad = db.Column(db.String(2), nullable=False)  # "SI" o "NO"
    cual_discapacidad = db.Column(db.String(150), nullable=True)




