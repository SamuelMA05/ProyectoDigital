import sys
import serial
import sqlite3
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QTabWidget, QMessageBox
import pyqtgraph as pg

# Importar funciones externas
import Funciones
from Funciones import guardar_medidas, guardar_usuario

# CONFIGURACIÓN
PUERTO = "COM17"
BAUDRATE = 115200
LIMITE = 4000
MAX_POINTS = 200


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medidas del Sensor")
        self.resize(1200, 700)

        # Evitar ventanas repetidas de peligro
        self.peligro_mostrado = False

        # Conectar UART
        try:
            self.arduino = serial.Serial(PUERTO, BAUDRATE, timeout=1)
        except Exception as e:
            print("ERROR: No se pudo conectar al dispositivo:", e)
            sys.exit()

        # ------------------------------
        # Layout principal
        # ------------------------------
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # ------------------------------
        # Pestaña 1: Tiempo real
        # ------------------------------
        self.tab_realtime = QWidget()
        self.tabs.addTab(self.tab_realtime, "Tiempo Real")
        layout_tab = QHBoxLayout()
        self.tab_realtime.setLayout(layout_tab)

        layout_izq = QVBoxLayout()
        layout_tab.addLayout(layout_izq, stretch=3)

        self.combo_dias = QComboBox()
        self.combo_dias.addItem("Seleccionar día")
        self.combo_dias.addItems(self.obtener_dias_bd())
        self.combo_dias.currentTextChanged.connect(self.cambiar_dia_reporte)
        layout_izq.addWidget(self.combo_dias)

        # Gráfico tiempo real
        self.graph = pg.PlotWidget(title="Medidas del Sensor en Tiempo Real")
        self.graph.setBackground("w")
        self.graph.showGrid(x=True, y=True)
        self.graph.addLegend()
        layout_izq.addWidget(self.graph, stretch=1)

        self.time = []
        self.data_x = []
        self.data_y = []
        self.data_z = []
        self.t = 0

        self.line_x = self.graph.plot([], [], name="X", pen=pg.mkPen('r', width=2))
        self.line_y = self.graph.plot([], [], name="Y", pen=pg.mkPen('g', width=2))
        self.line_z = self.graph.plot([], [], name="Z", pen=pg.mkPen('b', width=2))

        # ------------------------------
        # Pestaña 2: Reporte por día
        # ------------------------------
        self.tab_reporte = QWidget()
        self.tabs.addTab(self.tab_reporte, "Reporte del Día")
        self.reporte_layout = QVBoxLayout()
        self.tab_reporte.setLayout(self.reporte_layout)

        self.graph_reporte = pg.PlotWidget(title="Reporte del Día")
        self.graph_reporte.setBackground("w")
        self.graph_reporte.addLegend()
        self.reporte_layout.addWidget(self.graph_reporte)

        self.plot_x_reporte = self.graph_reporte.plot(pen=pg.mkPen('r', width=2), name="X")
        self.plot_y_reporte = self.graph_reporte.plot(pen=pg.mkPen('g', width=2), name="Y")
        self.plot_z_reporte = self.graph_reporte.plot(pen=pg.mkPen('b', width=2), name="Z")

        # ------------------------------
        # Timer UART
        # ------------------------------
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    # =======================================
    # LECTURA UART
    # =======================================
    def update_plot(self):
        if self.arduino.in_waiting > 0:

            raw = self.arduino.readline().decode("utf-8").strip()
            if not raw:
                return

            partes = raw.split(",")
            codigo = partes[0]

            # =======================================
            # Código 2 → Guardar usuario
            # =======================================
            if codigo == "2" and len(partes) == 3:
                ok = guardar_usuario(raw)
                msg = QMessageBox()
                msg.setWindowTitle("Usuario Guardado")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText(f"El usuario '{partes[1]}' fue guardado correctamente.")
                msg.exec()
                return

            # =======================================
            # Código 3 → LOGIN
            # =======================================
            if codigo == "3" and len(partes) == 3:
                ok = Funciones.comprobar_login(raw)
                if ok:
                    self.arduino.write(b"T\n")
                else:
                    self.arduino.write(b"F\n")
                msg = QMessageBox()
                msg.setWindowTitle("Inicio de Sesión")
                if ok:
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setText(f"Inicio de sesión exitoso para el usuario '{partes[1]}'")
                else:
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText("Usuario o contraseña incorrectos")
                msg.exec()
                return

            # =======================================
            # Código 1 → Medidas del sensor
            # =======================================
            if codigo == "1" and len(partes) == 4:
                try:
                    x = float(partes[1])
                    y = float(partes[2])
                    z = float(partes[3])
                except:
                    return

                # Guardar medida y obtener danger
                conn = sqlite3.connect("data.db")
                danger = guardar_medidas(LIMITE, raw, conn)
                conn.close()

                # Mostrar alerta solo una vez si DANGER
                if danger == 1:
                    self.arduino.write(b"4\n")
                    if not self.peligro_mostrado:
                        self.peligro_mostrado = True
                        msg = QMessageBox()
                        msg.setWindowTitle("PELIGRO DE MEDICIÓN")
                        msg.setIcon(QMessageBox.Icon.Critical)
                        msg.setText("⚠️ Se detectó una medición peligrosa.\nRevisa el sensor.")
                        msg.exec()
                else:
                    self.peligro_mostrado = False

                # Actualizar buffers gráfico
                self.data_x.append(x)
                self.data_y.append(y)
                self.data_z.append(z)
                self.time.append(self.t)
                self.t += 1

                if len(self.data_x) > MAX_POINTS:
                    self.data_x.pop(0)
                    self.data_y.pop(0)
                    self.data_z.pop(0)
                    self.time.pop(0)

                self.line_x.setData(self.time, self.data_x)
                self.line_y.setData(self.time, self.data_y)
                self.line_z.setData(self.time, self.data_z)

            # =======================================
            # Código 5 → Cambiar contraseña
            # =======================================
            if codigo == "5" and len(partes) == 3:
                usuario = partes[1]
                nueva_contraseña = partes[2]

                ok = Funciones.cambiar_contraseña(raw)  # raw = "5,usuario,nueva_contraseña"

                if ok:
                    self.arduino.write(b"T\n")
                    msg = QMessageBox()
                    msg.setWindowTitle("Cambio de Contraseña")
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.setText(f"Contraseña de '{usuario}' actualizada correctamente.")
                    msg.exec()
                else:
                    self.arduino.write(b"F\n")
                    msg = QMessageBox()
                    msg.setWindowTitle("Cambio de Contraseña")
                    msg.setIcon(QMessageBox.Icon.Warning)
                    msg.setText(f"No se pudo actualizar la contraseña de '{usuario}'.")
                    msg.exec()
                return

    # =======================================
    # Días almacenados en BD
    # =======================================
    def obtener_dias_bd(self):
        try:
            conn = sqlite3.connect("data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT DATE(timestamp) FROM medidas ORDER BY DATE(timestamp) DESC")
            dias = [row[0] for row in cursor.fetchall()]
        except:
            dias = []
        finally:
            conn.close()

        return dias

    def cambiar_dia_reporte(self, dia):
        if dia != "Seleccionar día":
            self.actualizar_reporte(dia)

    # =======================================
    # Reporte del día
    # =======================================
    def actualizar_reporte(self, dia):
        x_data = Funciones.obtener_dia_x(dia)
        y_data = Funciones.obtener_dia_y(dia)
        z_data = Funciones.obtener_dia_z(dia)

        n = len(x_data)
        time_axis = [i * 5 for i in range(n)]

        self.plot_x_reporte.setData(time_axis, x_data)
        self.plot_y_reporte.setData(time_axis, y_data)
        self.plot_z_reporte.setData(time_axis, z_data)

        self.graph_reporte.setTitle(f"Reporte del Día: {dia}")


# ------------------------------
# INICIAR APP
# ------------------------------
app = QtWidgets.QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
