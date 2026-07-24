import sqlite3

# Crear conexión y cursor
conn = sqlite3.connect('notas.db')
c = conn.cursor()

# Crear tabla de estudiantes
c.execute('''
CREATE TABLE estudiante (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    grado TEXT
)
''')

# Crear tabla de materias
c.execute('''
CREATE TABLE materia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_materia TEXT NOT NULL
)
''')

# Crear tabla de notas
c.execute('''
CREATE TABLE nota (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id INTEGER,
    materia_id INTEGER,
    periodo INTEGER,
    nota REAL,
    FOREIGN KEY (estudiante_id) REFERENCES estudiante(id),
    FOREIGN KEY (materia_id) REFERENCES materia(id)
)
''')

# Crear tabla de logros
c.execute('''
CREATE TABLE logro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estudiante_id INTEGER,
    materia TEXT,
    periodo INTEGER,
    descripcion TEXT,
    FOREIGN KEY (estudiante_id) REFERENCES estudiante(id)
)
''')

# Insertar datos de prueba
# Estudiantes
c.execute("INSERT INTO estudiante (nombre, grado) VALUES ('Juan Perez', '5°')")
c.execute("INSERT INTO estudiante (nombre, grado) VALUES ('Ana Gomez', '5°')")

# Materias
c.execute("INSERT INTO materia (nombre_materia) VALUES ('Matemáticas')")
c.execute("INSERT INTO materia (nombre_materia) VALUES ('Lengua')")
c.execute("INSERT INTO materia (nombre_materia) VALUES ('Ciencias')")

# Notas
c.execute("INSERT INTO nota (estudiante_id, materia_id, periodo, nota) VALUES (1, 1, 1, 4.5)")
c.execute("INSERT INTO nota (estudiante_id, materia_id, periodo, nota) VALUES (1, 2, 1, 3.7)")
c.execute("INSERT INTO nota (estudiante_id, materia_id, periodo, nota) VALUES (2, 1, 1, 4.0)")

# Logros
c.execute("INSERT INTO logro (estudiante_id, materia, periodo, descripcion) VALUES (1, 'Matemáticas', 1, 'Excelente participación')")
c.execute("INSERT INTO logro (estudiante_id, materia, periodo, descripcion) VALUES (1, 'Lengua', 1, 'Buen progreso')")
c.execute("INSERT INTO logro (estudiante_id, materia, periodo, descripcion) VALUES (2, 'Matemáticas', 1, 'Muy buen desempeño')")

# Guardar y cerrar
conn.commit()
conn.close()

print("Base de datos creada y datos de prueba insertados ✅")
