import sqlite3
import os

db_path = os.path.join("instance", "notas.db")

if not os.path.exists(db_path):
    print("❌ No se encontró la base de datos en:", db_path)
else:
    print("📁 Base encontrada:", db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n📋 Tablas en la base de datos:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for t in cursor.fetchall():
        print(" -", t[0])

    print("\n🧱 Columnas por tabla:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for t in cursor.fetchall():
        table_name = t[0]
        print(f"\n📌 {table_name}:")
        cursor.execute(f"PRAGMA table_info({table_name});")
        for col in cursor.fetchall():
            print("   ▫️", col[1])

    conn.close()
