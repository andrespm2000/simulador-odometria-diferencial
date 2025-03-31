import sys
import math
from PySide6 import QtCore, QtWidgets, QtGui

class SimulationWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(500, 500)
        self.setStyleSheet("background-color: black; border: 1px solid black;")
        self.robot_position = QtCore.QPointF(40, 450)  # Center of the widget
        self.robot_angle = 0  # Angle in degrees

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        painter.fillRect(self.rect(), QtGui.QColor("black"))

        # Draw grid
        grid_size = 50
        pen = QtGui.QPen(QtGui.QColor("green"))
        pen.setWidth(1)
        painter.setPen(pen)
        for x in range(0, self.width(), grid_size):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), grid_size):
            painter.drawLine(0, y, self.width(), y)

        # Draw robot (triangle)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("blue")))
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))

        # Calculate triangle vertices
        size = 15
        angle_rad = math.radians(self.robot_angle)
        center = self.robot_position

        # Define the triangle relative to its center
        points = [
            QtCore.QPointF(size, 0),  # Front vertex
            QtCore.QPointF(-size / 2, -size / 2),  # Bottom-left vertex
            QtCore.QPointF(-size / 2, size / 2),  # Bottom-right vertex
        ]

        # Rotate the points around the center
        rotated_points = []
        for point in points:
            rotated_x = point.x() * math.cos(angle_rad) - point.y() * math.sin(angle_rad)
            rotated_y = point.x() * math.sin(angle_rad) + point.y() * math.cos(angle_rad)
            rotated_points.append(center + QtCore.QPointF(rotated_x, rotated_y))

        # Create the triangle polygon
        triangle = QtGui.QPolygonF(rotated_points)

        painter.drawPolygon(triangle)

class MainWindow(QtWidgets.QMainWindow):

    orientacionRobot = 0
    recorridoRobot = 0
    textoLog = f"Orientacion: {orientacionRobot}\nRecorrido: {recorridoRobot}\n"
    controlInfo = "W: mueve 1 unidad por segundo hacia adelante\nA: mueve 1 unidad por segundo hacia izquierda\nS: mueve 1 unidad por segundo hacia atras\nD: mueve 1 unidad por segundo hacia derecha\nQ: gira 1 grado por segundo hacia izquierda\nE: gira 1 grado por segundo hacia derecha\nR: reinicia la posicion y orientacion\nP: simula error"


    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simulador odometria")

        # Central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.simulation_widget = SimulationWidget()

        # Layout for the central widget
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        rightLayout = QtWidgets.QVBoxLayout(central_widget)

        # Upper-right square with text
        self.infoSquare = QtWidgets.QLabel(self.controlInfo,alignment=QtCore.Qt.AlignLeft)
        self.infoSquare.setAlignment(QtCore.Qt.AlignCenter)
        self.infoSquare.setFixedSize(300, 200)
        self.infoSquare.setStyleSheet("border: 1px solid black; background-color: lightgray;")

        # Right sidebar for logs
        self.log_sidebar = QtWidgets.QLabel(self.textoLog,alignment=QtCore.Qt.AlignLeft)
        self.log_sidebar.setFixedSize(300, 400)
        self.log_sidebar.setStyleSheet("border: 1px solid black; background-color: lightgray;")

        # Add widgets to the layout
        rightLayout.addWidget(self.infoSquare, alignment=QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        rightLayout.addWidget(self.log_sidebar)

        main_layout.addWidget(self.simulation_widget)
        main_layout.addLayout(rightLayout)

    def keyPressEvent(self, event):
            key = event.key()
            step = 5  # Movement step size
            angle_step = 1  # Rotation step size in degrees

            if key == QtCore.Qt.Key_W:  # Move forward
                self.simulation_widget.robot_position += QtCore.QPointF(
                    step * math.cos(math.radians(self.simulation_widget.robot_angle)),
                    step * math.sin(math.radians(self.simulation_widget.robot_angle))
                )
            elif key == QtCore.Qt.Key_S:  # Move backward
                self.simulation_widget.robot_position -= QtCore.QPointF(
                    step * math.cos(math.radians(self.simulation_widget.robot_angle)),
                    step * math.sin(math.radians(self.simulation_widget.robot_angle))
                )
            elif key == QtCore.Qt.Key_A:  # Move left
                self.simulation_widget.robot_position += QtCore.QPointF(
                    step * math.sin(math.radians(self.simulation_widget.robot_angle)),
                    -step * math.cos(math.radians(self.simulation_widget.robot_angle))
                )
            elif key == QtCore.Qt.Key_D:  # Move right
                self.simulation_widget.robot_position -= QtCore.QPointF(
                    step * math.sin(math.radians(self.simulation_widget.robot_angle)),
                    -step * math.cos(math.radians(self.simulation_widget.robot_angle))
                )
             # Rotación hacia la izquierda Q
            elif key == QtCore.Qt.Key_Q:  
                self.simulation_widget.robot_angle -= angle_step
            # Rotación hacia la derecha E
            elif key == QtCore.Qt.Key_E:  
                self.simulation_widget.robot_angle += angle_step
            elif key == QtCore.Qt.Key_R:  # Reset position and orientation
                self.simulation_widget.robot_position = QtCore.QPointF(40, 450)
                self.simulation_widget.robot_angle = 0

            # Update the simulation widget
            self.simulation_widget.update()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    main_window = MainWindow()
    main_window.resize(800, 600)
    main_window.show()

    sys.exit(app.exec())