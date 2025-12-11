import sqlite3
import hashlib
from tabulate import tabulate

# ==========================================================
# HASH PASSWORD
# ==========================================================
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# ==========================================================
# GUARDAR USUARIO
# ==========================================================
def guardar_usuario(line):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    codigo_str, user_id, password = line.split(",")

    try:
        hashed_password = hash_password(password)
        cursor.execute("""
            INSERT INTO usuario (user, password)
            VALUES (?, ?)
        """, (user_id, hashed_password))

        conn.commit()
        print(f"Usuario {user_id} guardado correctamente.")
        return True

    except sqlite3.IntegrityError as e:
        print("Error al guardar usuario:", e)
        return False

    finally:
        conn.close()

# ==========================================================
# MOSTRAR USUARIOS
# ==========================================================
def mostrar_usuarios():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuario")
    registros = cursor.fetchall()
    conn.close()

    if registros:
        print(tabulate(registros, headers=["ID", "User", "Password"], tablefmt="fancy_grid"))
    else:
        print("No hay usuarios registrados.")

# ==========================================================
# VERIFICAR CONTRASEÑA
# ==========================================================
def verificar_contraseña(user_id, password_ingresada):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM usuario WHERE user = ?", (user_id,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        password_guardada = resultado[0]
        if hash_password(password_ingresada) == password_guardada:
            print("Iniciar sesion")
            return True
        else:
            print("Contraseña incorrecto")
            return False
    else:
        print("Usuario no encontrado.")
        return False

# ==========================================================
# CONSULTAS POR DÍA
# ==========================================================
def obtener_dia_x(dia):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT Medidax FROM medidas WHERE DATE(timestamp) = ?", (dia,))
        resultados = cursor.fetchall()
        x_values = [fila[0] for fila in resultados]
    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
        x_values = []
    finally:
        conn.close()
    
    return x_values


def obtener_dia_y(dia):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT Mediday FROM medidas WHERE DATE(timestamp) = ?", (dia,))
        resultados = cursor.fetchall()
        y_values = [fila[0] for fila in resultados]
    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
        y_values = []
    finally:
        conn.close()
    
    return y_values


def obtener_dia_z(dia):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT Medidaz FROM medidas WHERE DATE(timestamp) = ?", (dia,))
        resultados = cursor.fetchall()
        z_values = [fila[0] for fila in resultados]
    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
        z_values = []
    finally:
        conn.close()
    
    return z_values

# ==========================================================
# INCIDENTES (danger=1)
# ==========================================================
def obtener_incidentes(dia):
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, Medidax, Mediday, Medidaz
            FROM medidas
            WHERE DATE(timestamp) = ? AND danger = 1
            ORDER BY timestamp ASC
        """, (dia,))

        resultados = cursor.fetchall()

    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
        resultados = []

    finally:
        conn.close()
    
    return resultados

# ==========================================================
# GUARDAR MEDIDAS — danger se activa si magnitud > 4000
# ==========================================================
def guardar_medidas(limite, line, conn):
    cursor = conn.cursor()
    
    try:
        codigo_str, x_str, y_str, z_str = line.split(",")

        x = float(x_str)
        y = float(y_str)
        z = float(z_str)

        magnitud = (x**2 + y**2 + z**2)**0.5

        danger = 1 if magnitud > limite else 0

        cursor.execute("""
            INSERT INTO medidas (Danger, Medidax, Mediday, Medidaz)
            VALUES (?, ?, ?, ?)
        """, (danger, x, y, z))

        conn.commit()

        print(f"Guardado: X={x} Y={y} Z={z} | Magnitud={magnitud:.2f} | Danger={danger}")

        return danger   # ← ESTA ES LA LÍNEA NUEVA

    except ValueError:
        print("Error al parsear la línea:", line)
        return 0



# ==========================================================
# LOGIN
# ==========================================================
def comprobar_login(line):
    try:
        codigo, user_id, password = line.split(",")
    except:
        print("ERROR: Formato inválido en login:", line)
        return False

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM usuario WHERE user = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        print("Usuario no existe")
        return False

    password_guardada = row[0]

    if hash_password(password) == password_guardada:
        print("Login correcto!")
        return True
    else:
        print("Contraseña incorrecta")
        return False
# ==========================================================
# CAMBIAR CONTRASEÑA
# ==========================================================
def cambiar_contraseña(line):
    """
    Recibe línea desde UART con formato:
    5,usuario,nueva_contraseña
    """
    try:
        codigo, user_id, nueva_pass = line.split(",")
    except ValueError:
        print("Error: Formato inválido. Se esperaba 5,usuario,nueva_contraseña")
        return False

    # Hash de la nueva contraseña
    hashed_pass = hashlib.sha256(nueva_pass.encode('utf-8')).hexdigest()

    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        # Actualizar contraseña
        cursor.execute("""
            UPDATE usuario
            SET password = ?
            WHERE user = ?
        """, (hashed_pass, user_id))

        conn.commit()

        if cursor.rowcount == 0:
            print(f"Usuario '{user_id}' no encontrado.")
            return False
        else:
            print(f"Contraseña de '{user_id}' actualizada correctamente.")
            return True

    except sqlite3.Error as e:
        print("Error en la base de datos:", e)
        return False

    finally:
        conn.close()
