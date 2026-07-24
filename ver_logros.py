import sqlite3
import os

# Ruta a la base correcta
db_path = os.path.join("instance", "notas.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ver los primeros logros
cursor.execute("SELECT materia, estudiante_id, periodo, descripcion FROM logro LIMIT 5;")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
