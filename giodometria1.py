import sys
import math
from PySide6 import QtCore, QtWidgets, QtGui

# Características físicas del robot
DIAMETRO_RUEDA_L = 6.5  # cm
DIAMETRO_RUEDA_R = 6.5  # cm
SEPARACION_RUEDAS = 13.0  # cm
RESOLUCION_ENCODER = 360  # pulsos por vuelta
PULSO_CM_L = (math.pi * DIAMETRO_RUEDA_L) / RESOLUCION_ENCODER
PULSO_CM_R = (math.pi * DIAMETRO_RUEDA_R) / RESOLUCION_ENCODER

class SimulationWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(500, 500)
        self.setStyleSheet("background-color: black; border: 1px solid black;")
        self.robot_position = QtCore.QPointF(40, 450)
        self.robot_angle = 0  # grados
        self.trail = [self.robot_position]

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor("black"))

        grid_size = 50
        pen = QtGui.QPen(QtGui.QColor("green"))
        pen.setWidth(1)
        painter.setPen(pen)
        for x in range(0, self.width(), grid_size):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), grid_size):
            painter.drawLine(0, y, self.width(), y)

        # Dibuja el rastro
        if len(self.trail) > 1:
            pen = QtGui.QPen(QtGui.QColor("white"))
            pen.setWidth(2)
            painter.setPen(pen)
            for i in range(len(self.trail) - 1):
                painter.drawLine(self.trail[i], self.trail[i + 1])

        # Dibuja el robot (triángulo)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("blue")))
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))

        size = 15
        angle_rad = math.radians(self.robot_angle)
        center = self.robot_position

        points = [
            QtCore.QPointF(size, 0),
            QtCore.QPointF(-size / 2, -size / 2),
            QtCore.QPointF(-size / 2, size / 2),
        ]

        rotated_points = []
        for point in points:
            rotated_x = point.x() * math.cos(angle_rad) - point.y() * math.sin(angle_rad)
            rotated_y = point.x() * math.sin(angle_rad) + point.y() * math.cos(angle_rad)
            rotated_points.append(center + QtCore.QPointF(rotated_x, rotated_y))

        triangle = QtGui.QPolygonF(rotated_points)
        painter.drawPolygon(triangle)

    def move_by_encoders(self, left_ticks, right_ticks, simulate_error=False):
        dl = left_ticks * PULSO_CM_L
        dr = right_ticks * PULSO_CM_R

        if simulate_error:
            dr *= 0.7  # simula deslizamiento de una rueda

        dc = (dl + dr) / 2.0
        dtheta = (dr - dl) / SEPARACION_RUEDAS  # en radianes

        angle_rad = math.radians(self.robot_angle)
        new_angle = angle_rad + dtheta

        dx = dc * math.cos(new_angle)
        dy = dc * math.sin(new_angle)

        new_pos = self.robot_position + QtCore.QPointF(dx, dy)
        if 0 < new_pos.x() < self.width() and 0 < new_pos.y() < self.height():
            self.robot_position = new_pos
            self.robot_angle = math.degrees(new_angle) % 360
            self.trail.append(self.robot_position)

    def reset(self):
        self.robot_position = QtCore.QPointF(40, 450)
        self.robot_angle = 0
        self.trail = [self.robot_position]
        self.update()

class MainWindow(QtWidgets.QMainWindow):

    orientacionRobot = 0
    recorridoRobot = 0
    textoLog = f"Orientacion: {orientacionRobot}\nRecorrido: {recorridoRobot}\n"
    controlInfo = """W: mueve 1 unidad por segundo hacia adelante\nA: mueve 1 unidad por segundo hacia izquierda\nS: mueve 1 unidad por segundo hacia atras\nD: mueve 1 unidad por segundo hacia derecha\nQ: gira 1 grado por segundo hacia izquierda\nE: gira 1 grado por segundo hacia derecha\nR: reinicia la posicion y orientacion\nP: simula error"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador odometria")

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.simulation_widget = SimulationWidget()

        main_layout = QtWidgets.QHBoxLayout(central_widget)
        rightLayout = QtWidgets.QVBoxLayout()

        self.infoSquare = QtWidgets.QLabel(self.controlInfo, alignment=QtCore.Qt.AlignLeft)
        self.infoSquare.setAlignment(QtCore.Qt.AlignTop)
        self.infoSquare.setFixedSize(300, 200)
        self.infoSquare.setWordWrap(True)
        self.infoSquare.setStyleSheet("border: 1px solid black; background-color: lightgray; font-size: 14px;")

        self.log_sidebar = QtWidgets.QLabel(self.textoLog, alignment=QtCore.Qt.AlignLeft)
        self.log_sidebar.setFixedSize(300, 400)
        self.log_sidebar.setWordWrap(True)
        self.log_sidebar.setStyleSheet("border: 1px solid black; background-color: lightgray; font-size: 14px;")

        rightLayout.addWidget(self.infoSquare, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        rightLayout.addWidget(self.log_sidebar)

        main_layout.addWidget(self.simulation_widget)
        main_layout.addLayout(rightLayout)

    def actualizar_log(self):
        self.orientacionRobot = round(self.simulation_widget.robot_angle, 2)
        self.textoLog = f"Orientacion: {self.orientacionRobot:.2f}\u00b0\nRecorrido: {self.recorridoRobot:.2f} cm\n"
        self.log_sidebar.setText(self.textoLog)

    def keyPressEvent(self, event):
        key = event.key()
        step = 5  # Movimiento en píxeles
        angle_step = 1  # Paso de rotación en grados

        moved = False  # Indicador de si se movió el robot

        # Cálculo de la dirección
        rad = math.radians(self.simulation_widget.robot_angle)
        dx = step * math.cos(rad)
        dy = step * math.sin(rad)

        # Movimiento con encoders (W, S, A, D, Q, E, P, R)
        if key == QtCore.Qt.Key_W:
            new_pos = self.simulation_widget.robot_position + QtCore.QPointF(dx, dy)
            if 0 < new_pos.x() < self.simulation_widget.width() and 0 < new_pos.y() < self.simulation_widget.height():
                self.simulation_widget.move_by_encoders(10, 10)
                self.recorridoRobot += ((10 * PULSO_CM_R + 10 * PULSO_CM_L) / 2)
                moved = True
        elif key == QtCore.Qt.Key_S:
            new_pos = self.simulation_widget.robot_position - QtCore.QPointF(dx, dy)
            if 0 < new_pos.x() < self.simulation_widget.width() and 0 < new_pos.y() < self.simulation_widget.height():
                self.simulation_widget.move_by_encoders(-10, -10)
                self.recorridoRobot += ((10 * PULSO_CM_R + 10 * PULSO_CM_L) / 2)
                moved = True
        elif key == QtCore.Qt.Key_A:
            new_pos = self.simulation_widget.robot_position + QtCore.QPointF(-step * math.sin(rad), step * math.cos(rad))
            if 0 < new_pos.x() < self.simulation_widget.width() and 0 < new_pos.y() < self.simulation_widget.height():
                self.simulation_widget.move_by_encoders(-10, 10)
                moved = True
        elif key == QtCore.Qt.Key_D:
            new_pos = self.simulation_widget.robot_position + QtCore.QPointF(step * math.sin(rad), -step * math.cos(rad))
            if 0 < new_pos.x() < self.simulation_widget.width() and 0 < new_pos.y() < self.simulation_widget.height():
                self.simulation_widget.move_by_encoders(10, -10)
                moved = True
        elif key == QtCore.Qt.Key_Q:
            new_pos = self.simulation_widget.robot_position + QtCore.QPointF(step * math.sin(rad), -step * math.cos(rad))
            if 0 < new_pos.x() < self.simulation_widget.width() and 0 < new_pos.y() < self.simulation_widget.height():
                self.simulation_widget.move_by_encoders(10, 3)
                self.recorridoRobot += ((3 * PULSO_CM_L + 10 * PULSO_CM_R) / 2)
                moved = True
        elif key == QtCore.Qt.Key_E:
            new_pos = self.simulation_widget.robot_position + QtCore.QPointF(-step * math.sin(rad), step * math.cos(rad))
            if 0 < new_pos.x() < self.simulation_widget.width() and 0 < new_pos.y() < self.simulation_widget.height():
                self.simulation_widget.move_by_encoders(3, 10)
                self.recorridoRobot += ((10 * PULSO_CM_L + 3 * PULSO_CM_R) / 2)
                moved = True
        elif key == QtCore.Qt.Key_P:
            new_pos = self.simulation_widget.robot_position + QtCore.QPointF(dx, dy)
            if 0 < new_pos.x() < self.simulation_widget.width() and 0 < new_pos.y() < self.simulation_widget.height():
                self.simulation_widget.move_by_encoders(10, 10, simulate_error=True)
                self.recorridoRobot += ((10 * PULSO_CM_R + 10 * PULSO_CM_L) / 2)
                moved = True
        # Reset del robot (R)
        elif key == QtCore.Qt.Key_R:
            self.simulation_widget.reset()
            self.recorridoRobot = 0

        # Si el robot se movió, actualiza la posición
        if moved:
            self.simulation_widget.update()

        # Actualización del log y la interfaz de la simulación
        self.actualizar_log()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    main_window = MainWindow()
    main_window.resize(800, 600)
    main_window.show()
    sys.exit(app.exec())
