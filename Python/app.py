from PyQt6 import QtWidgets, QtCore
import pyqtgraph as pg
import numpy as np
import Funciones
from PyQt6.QtWidgets import QHeaderView

def generar_eje_x(array_y, intervalo_segundos=5):
    n = len(array_y)
    return [i * intervalo_segundos for i in range(n)]

class SensorReportTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Layout principal vertical
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        # --- Gráfica grande arriba ---
        self.plot_widget = pg.PlotWidget(title="Tendencia X,Y,Z")
        self.plot_widget.setBackground("#D3D3D3")
        main_layout.addWidget(self.plot_widget)

        # Configurar ejes en negro
        self.plot_widget.getAxis("left").setPen(pg.mkPen("#000000", width=2))
        self.plot_widget.getAxis("bottom").setPen(pg.mkPen("#000000", width=2))
        self.plot_widget.getAxis("left").setTextPen(pg.mkPen("#000000"))
        self.plot_widget.getAxis("bottom").setTextPen(pg.mkPen("#000000"))

        self.plot_x = self.plot_widget.plot(pen=pg.mkPen(color=(255, 0, 0), width=2), name="X")
        self.plot_y = self.plot_widget.plot(pen=pg.mkPen(color=(0, 255, 0), width=2), name="Y")
        self.plot_z = self.plot_widget.plot(pen=pg.mkPen(color=(0, 0, 255), width=2), name="Z")
      
        # --- Layout horizontal abajo ---
        bottom_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(bottom_layout)
        bottom_layout.setContentsMargins(20, 10, 20, 10)

        # --- Layout vertical para tabla de incidentes/datos ---
        data_layout = QtWidgets.QVBoxLayout()
        data_title = QtWidgets.QLabel("Tabla de Incidentes")
        data_title.setStyleSheet("font-weight: bold; font-size: 14pt;")
        data_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        data_layout.addWidget(data_title)

        # Tabla de incidentes
        self.new_table = QtWidgets.QTableWidget()
        self.new_table.setColumnCount(4)
        self.new_table.setRowCount(3)
        self.new_table.setHorizontalHeaderLabels(["Fecha", "Valor X", "Valor Y", "Valor Z"])
        self.new_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.new_table.setMinimumWidth(400)

        # Limitar altura para mostrar solo 3 filas
        fila_altura = self.new_table.verticalHeader().defaultSectionSize()
        self.new_table.setMaximumHeight(fila_altura * 3 + 2)

        # Alineación: expandir horizontalmente pero altura fija
        self.new_table.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                     QtWidgets.QSizePolicy.Policy.Fixed)

        # Activar scroll vertical
        self.new_table.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)

        data_layout.addWidget(self.new_table)
        bottom_layout.addLayout(data_layout)

        # Espacio entre tablas
        bottom_layout.addSpacing(50)

        # --- Layout vertical para tabla de estadísticas ---
        stats_layout = QtWidgets.QVBoxLayout()
        stats_title = QtWidgets.QLabel("Tabla de Estadísticas")
        stats_title.setStyleSheet("font-weight: bold; font-size: 14pt;")
        stats_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(stats_title)

        # Tabla de estadísticas
        self.stats_table = QtWidgets.QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setRowCount(3)
        self.stats_table.setHorizontalHeaderLabels(["Eje", "Promedio", "Máximo", "Mínimo"])
        self.stats_table.setVerticalHeaderLabels(["", "", ""])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.stats_table.setMinimumWidth(400)
        stats_layout.addWidget(self.stats_table)

        bottom_layout.addLayout(stats_layout)

        # Actualizar datos
        self.actualizar_reporte()

    def actualizar_reporte(self):
        dia = "2025-11-22"

        # Obtener datos de X, Y, Z
        x_data = Funciones.obtener_dia_x(dia)
        y_data = Funciones.obtener_dia_y(dia)
        z_data = Funciones.obtener_dia_z(dia)

        if x_data and y_data and z_data:
            # Gráfica
            time_axis = generar_eje_x(x_data, intervalo_segundos=5)
            self.plot_x.setData(time_axis, x_data)
            self.plot_y.setData(time_axis, y_data)
            self.plot_z.setData(time_axis, z_data)

            # Tabla de estadísticas
            stats = [
                ("X", np.mean(x_data), np.max(x_data), np.min(x_data)),
                ("Y", np.mean(y_data), np.max(y_data), np.min(y_data)),
                ("Z", np.mean(z_data), np.max(z_data), np.min(z_data)),
            ]

            for i, row in enumerate(stats):
                self.stats_table.setItem(i, 0, QtWidgets.QTableWidgetItem(row[0]))
                for j, val in enumerate(row[1:], 1):
                    item = QtWidgets.QTableWidgetItem(f"{val:.2f}")
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    self.stats_table.setItem(i, j, item)

        # --- Llenar tabla de incidentes ---
        incidentes = Funciones.obtener_incidentes(dia)  # Lista de tuplas: [(fecha, x, y, z), ...]
        self.new_table.setRowCount(len(incidentes))

        for i, fila in enumerate(incidentes):
            for j, valor in enumerate(fila):
                item = QtWidgets.QTableWidgetItem(str(valor))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.new_table.setItem(i, j, item)


# -------------------- Código principal --------------------
app = QtWidgets.QApplication([])
main_window = QtWidgets.QMainWindow()
main_window.setWindowTitle("Dashboard Sensores")
main_window.resize(1200, 700)

tabs = QtWidgets.QTabWidget()
main_window.setCentralWidget(tabs)

sensor_tab = SensorReportTab()
tabs.addTab(sensor_tab, "Reporte Sensor")

main_window.show()
app.exec()
