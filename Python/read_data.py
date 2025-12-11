import sqlite3
from tabulate import tabulate
import Funciones
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM medidas")
filas = cursor.fetchall()

# Obtener nombres de columnas
columnas = [desc[0] for desc in cursor.description]

# Mostrar en tabla
print(tabulate(filas, headers=columnas, tablefmt="grid"))
Funciones.mostrar_usuarios()
conn.close()
