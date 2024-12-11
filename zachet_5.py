import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QSpinBox, QLabel
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor


class SolarEclipseSimulation(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Симуляция солнечного затмения")
        self.setGeometry(100, 100, 800, 400)

        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)

        self.luna_x = 0
        self.speed = 1
        self.luna_radius = 50
        self.distance = 200

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel(self)
        layout.addWidget(self.label)

        control_layout = QHBoxLayout()

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(1)
        self.speed_slider.valueChanged.connect(self.update_speed)
        control_layout.addWidget(QLabel("Скорость:"))
        control_layout.addWidget(self.speed_slider)

        self.radius_spinbox = QSpinBox()
        self.radius_spinbox.setRange(10, 200)
        self.radius_spinbox.setValue(50)
        self.radius_spinbox.valueChanged.connect(self.update_radius)
        control_layout.addWidget(QLabel("Радиус Луны:"))
        control_layout.addWidget(self.radius_spinbox)

        self.distance_slider = QSlider(Qt.Horizontal)
        self.distance_slider.setRange(50, 400)
        self.distance_slider.setValue(200)
        self.distance_slider.valueChanged.connect(self.update_distance)
        control_layout.addWidget(QLabel("Расстояние:"))
        control_layout.addWidget(self.distance_slider)

        layout.addLayout(control_layout)

        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Запуск анимации")
        self.start_button.clicked.connect(self.start_animation)
        button_layout.addWidget(self.start_button)

        self.reset_button = QPushButton("Сброс")
        self.reset_button.clicked.connect(self.reset_parameters)
        button_layout.addWidget(self.reset_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def update_speed(self):
        self.speed = self.speed_slider.value()

    def update_radius(self):
        self.luna_radius = self.radius_spinbox.value()
        self.update()

    def update_distance(self):
        self.distance = self.distance_slider.value()
        self.update()

    def start_animation(self):
        self.timer.start(16)

    def reset_parameters(self):
        self.timer.stop()
        self.luna_x = 0
        self.speed_slider.setValue(1)
        self.radius_spinbox.setValue(50)
        self.distance_slider.setValue(200)
        self.update()

    def update_position(self):
        self.luna_x += self.speed
        if self.luna_x > self.width():
            self.luna_x = -self.luna_radius * 2
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        sun_x = self.width() // 2
        sun_y = self.height() // 2
        sun_radius = 100

        painter.setBrush(QColor(255, 223, 0))
        painter.drawEllipse(sun_x - sun_radius, sun_y - sun_radius, sun_radius * 2, sun_radius * 2)

        luna_y = sun_y + self.distance - self.height() // 2
        painter.setBrush(QColor(50, 50, 50))
        painter.drawEllipse(self.luna_x, luna_y - self.luna_radius, self.luna_radius * 2, self.luna_radius * 2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SolarEclipseSimulation()
    window.show()
    sys.exit(app.exec_())
