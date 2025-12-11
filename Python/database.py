import sqlite3
from tabulate import tabulate

# Crear o conectar a la base de datos
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

# Crear tabla
cursor.execute("""
CREATE TABLE IF NOT EXISTS medidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Danger REAL,
    Medidax REAL,
    Mediday REAL,
    Medidaz REAL,
    time DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user INTEGER UNIQUE NOT NULL,        
    password TEXT NOT NULL               
)
""")

conn.commit()

conn.close()
