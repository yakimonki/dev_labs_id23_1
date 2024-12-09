import sys
import json
import random
import math
from PyQt6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QPushButton, QSlider, QLabel, QHBoxLayout, QComboBox, QDialog
)
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import QTimer, Qt, QRect


class Drop:
    def __init__(self, x, y, config):
        self.x = x
        self.y = y
        self.speed = config['speed']
        self.angle = config.get('angle', 0)
        self.length = random.uniform(10, 20)

    def update(self, dt):
        self.y += self.speed * dt * math.cos(math.radians(self.angle))
        self.x += self.speed * dt * math.sin(math.radians(self.angle))


class Cloud:
    def __init__(self, x, y, width, height, config, shape="Прямоугольник"):
        self.x = int(x)
        self.y = int(y)
        self.width = config.get("default_width", int(width))
        self.height = config.get("default_height", int(height))
        self.config = config
        self.shape = shape
        self.density = config['default_drops']
        self.min_speed = config['min_speed']
        self.max_speed = config['max_speed']
        self.min_angle = config['min_angle']
        self.max_angle = config['max_angle']
        self.angle = 0
        self.drops = []

    def create_drop(self):
        drop_x = random.uniform(self.x, self.x + self.width)
        drop_y = self.y + self.height / 2 + random.uniform(-self.height / 4, self.height / 4)
        speed = random.uniform(self.min_speed, self.max_speed)
        return Drop(drop_x, drop_y, {'speed': speed, 'angle': self.angle})

    def update(self, dt, screen_height):
        for drop in self.drops:
            drop.update(dt)
        self.drops = [drop for drop in self.drops if drop.y <= screen_height]
        if len(self.drops) < self.density:
            self.drops.append(self.create_drop())

    def adjust_drops(self, new_density):
        self.density = new_density

    def set_angle(self, angle):
        self.angle = angle
        for drop in self.drops:
            drop.angle = angle

    def draw(self, painter):
        painter.setBrush(QColor(105, 105, 105))
        if self.shape == "Прямоугольник":
            painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
        elif self.shape == "Овал":
            painter.drawEllipse(int(self.x), int(self.y), int(self.width), int(self.height))
        elif self.shape == "Кучевые":
            self.draw_cumulus(painter)
        elif self.shape == "Слоистые":
            self.draw_stratus(painter)

    def draw_cumulus(self, painter):
        painter.drawEllipse(int(self.x), int(self.y + self.height * 0.4), int(self.width * 0.5), int(self.height * 0.6))
        painter.drawEllipse(int(self.x + self.width * 0.3), int(self.y), int(self.width * 0.7), int(self.height * 0.7))
        painter.drawEllipse(int(self.x + self.width * 0.6), int(self.y + self.height * 0.4),
                            int(self.width * 0.5), int(self.height * 0.6))

    def draw_stratus(self, painter):
        painter.drawRect(int(self.x), int(self.y + self.height * 0.2), int(self.width), int(self.height * 0.2))
        painter.drawRect(int(self.x), int(self.y + self.height * 0.5), int(self.width), int(self.height * 0.2))


class RainWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.width = 1200
        self.height = 800
        self.clouds = [Cloud(200, 50, config['default_width'], config['default_height'], self.config)]
        self.selected_cloud = None
        self.dragging = False
        self.initUI()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(16)

    def initUI(self):
        self.setGeometry(100, 100, self.width, self.height)
        self.setWindowTitle('Симуляция дождя с облаками')

    def mousePressEvent(self, event):
        self.selected_cloud = None
        for cloud in self.clouds:
            if QRect(int(cloud.x), int(cloud.y), int(cloud.width), int(cloud.height)).contains(
                    int(event.position().x()), int(event.position().y())):
                self.selected_cloud = cloud
                self.dragging = True
                break

    def mouseMoveEvent(self, event):
        if self.dragging and self.selected_cloud:
            self.selected_cloud.x = int(event.position().x() - self.selected_cloud.width // 2)
            self.selected_cloud.y = int(event.position().y() - self.selected_cloud.height // 2)
            self.update()

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(25, 25, 112))

        for cloud in self.clouds:
            cloud.draw(painter)

        if self.selected_cloud:
            pen = QPen(QColor(255, 255, 255, 128))
            pen.setWidth(3)
            painter.setPen(pen)

            if self.selected_cloud.shape == "Прямоугольник":
                painter.drawRect(self.selected_cloud.x, self.selected_cloud.y,
                                 self.selected_cloud.width, self.selected_cloud.height)
            elif self.selected_cloud.shape == "Овал":
                painter.drawEllipse(self.selected_cloud.x, self.selected_cloud.y,
                                    self.selected_cloud.width, self.selected_cloud.height)
            elif self.selected_cloud.shape == "Кучевые":
                self.draw_cumulus_outline(painter, self.selected_cloud)
            elif self.selected_cloud.shape == "Слоистые":
                self.draw_stratus_outline(painter, self.selected_cloud)

        pen = QPen(Qt.GlobalColor.white)
        pen.setWidth(2)
        painter.setPen(pen)

        for cloud in self.clouds:
            for drop in cloud.drops:
                x_end = drop.x + drop.length * math.sin(math.radians(drop.angle))
                y_end = drop.y + drop.length * math.cos(math.radians(drop.angle))
                painter.drawLine(int(drop.x), int(drop.y), int(x_end), int(y_end))

    def draw_cumulus_outline(self, painter, cloud):
        painter.drawEllipse(int(cloud.x), int(cloud.y + cloud.height * 0.4),
                            int(cloud.width * 0.5), int(cloud.height * 0.6))
        painter.drawEllipse(int(cloud.x + cloud.width * 0.3), int(cloud.y),
                            int(cloud.width * 0.7), int(cloud.height * 0.7))
        painter.drawEllipse(int(cloud.x + cloud.width * 0.6), int(cloud.y + cloud.height * 0.4),
                            int(cloud.width * 0.5), int(cloud.height * 0.6))

    def draw_stratus_outline(self, painter, cloud):
        painter.drawRect(int(cloud.x), int(cloud.y + cloud.height * 0.2),
                         int(cloud.width), int(cloud.height * 0.2))
        painter.drawRect(int(cloud.x), int(cloud.y + cloud.height * 0.5),
                         int(cloud.width), int(cloud.height * 0.2))

    def update_simulation(self):
        for cloud in self.clouds:
            cloud.update(1 / 60, self.height)
        self.repaint()


class CloudEditDialog(QDialog):
    def __init__(self, selected_cloud):
        super().__init__()
        self.selected_cloud = selected_cloud
        self.setWindowTitle("Редактировать тучку")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.shape_selector = QComboBox()
        self.shape_selector.addItems(["Прямоугольник", "Овал", "Кучевые", "Слоистые"])
        self.shape_selector.setCurrentText(self.selected_cloud.shape)
        self.shape_selector.currentTextChanged.connect(self.change_shape)
        layout.addWidget(QLabel("Форма тучки:"))
        layout.addWidget(self.shape_selector)

        self.angle_slider = QSlider(Qt.Orientation.Horizontal)
        self.angle_slider.setRange(self.selected_cloud.config['min_angle'], self.selected_cloud.config['max_angle'])
        self.angle_slider.setValue(self.selected_cloud.angle)
        self.angle_slider.valueChanged.connect(self.change_angle)
        layout.addWidget(QLabel("Угол наклона капель (градусы):"))
        layout.addWidget(self.angle_slider)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(self.selected_cloud.config['min_speed'], self.selected_cloud.config['max_speed'])
        self.speed_slider.setValue((self.selected_cloud.min_speed + self.selected_cloud.max_speed) // 2)
        self.speed_slider.valueChanged.connect(self.change_speed)
        layout.addWidget(QLabel("Скорость капель:"))
        layout.addWidget(self.speed_slider)

        self.density_slider = QSlider(Qt.Orientation.Horizontal)
        self.density_slider.setRange(self.selected_cloud.config['min_drops'], self.selected_cloud.config['max_drops'])
        self.density_slider.setValue(self.selected_cloud.density)
        self.density_slider.valueChanged.connect(self.change_density)
        layout.addWidget(QLabel("Плотность капель:"))
        layout.addWidget(self.density_slider)

        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(self.selected_cloud.config['min_width'], self.selected_cloud.config['max_width'])
        self.width_slider.setValue(self.selected_cloud.width)
        self.width_slider.valueChanged.connect(self.change_width)
        layout.addWidget(QLabel("Ширина облака:"))
        layout.addWidget(self.width_slider)

        self.height_slider = QSlider(Qt.Orientation.Horizontal)
        self.height_slider.setRange(self.selected_cloud.config['min_height'], self.selected_cloud.config['max_height'])
        self.height_slider.setValue(self.selected_cloud.height)
        self.height_slider.valueChanged.connect(self.change_height)
        layout.addWidget(QLabel("Высота облака:"))
        layout.addWidget(self.height_slider)

        self.setLayout(layout)

    def change_shape(self, shape):
        self.selected_cloud.shape = shape

    def change_angle(self, value):
        self.selected_cloud.set_angle(value)

    def change_density(self, value):
        self.selected_cloud.adjust_drops(value)

    def change_speed(self, value):
        self.selected_cloud.min_speed = value - 5
        self.selected_cloud.max_speed = value + 5

    def change_width(self, value):
        self.selected_cloud.width = value

    def change_height(self, value):
        self.selected_cloud.height = value


class SettingsDialog(QDialog):
    def __init__(self, rain_widget):
        super().__init__()
        self.rain_widget = rain_widget
        self.setWindowTitle("Настройки")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        add_cloud_btn = QPushButton('Добавить тучку')
        add_cloud_btn.clicked.connect(self.add_cloud)
        layout.addWidget(add_cloud_btn)

        remove_cloud_btn = QPushButton('Удалить тучку')
        remove_cloud_btn.clicked.connect(self.remove_cloud)
        layout.addWidget(remove_cloud_btn)

        self.setLayout(layout)

    def add_cloud(self):
        self.rain_widget.clouds.append(Cloud(100, 100, self.rain_widget.config['default_width'], self.rain_widget.config['default_height'], self.rain_widget.config))

    def remove_cloud(self):
        if self.rain_widget.clouds:
            self.rain_widget.clouds.pop()


class ControlPanel(QWidget):
    def __init__(self, rain_widget):
        super().__init__()
        self.rain_widget = rain_widget
        self.initUI()

    def initUI(self):
        self.setFixedHeight(40)
        layout = QHBoxLayout()

        settings_btn = QPushButton('Настройки')
        settings_btn.setFixedSize(80, 30)
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)

        edit_btn = QPushButton('Редактировать')
        edit_btn.setFixedSize(120, 30)
        edit_btn.clicked.connect(self.open_edit_dialog)
        layout.addWidget(edit_btn)

        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        self.setLayout(layout)

    def open_settings(self):
        settings_dialog = SettingsDialog(self.rain_widget)
        settings_dialog.exec()

    def open_edit_dialog(self):
        if self.rain_widget.selected_cloud:
            edit_dialog = CloudEditDialog(self.rain_widget.selected_cloud)
            edit_dialog.exec()


if __name__ == '__main__':
    with open('file/config2.json', 'r') as config_file:
        config = json.load(config_file)

    app = QApplication(sys.argv)

    rain_widget = RainWidget(config)
    control_panel = ControlPanel(rain_widget)

    main_layout = QVBoxLayout()
    main_layout.addWidget(rain_widget)
    main_layout.addWidget(control_panel)

    main_window = QWidget()
    main_window.setLayout(main_layout)
    main_window.resize(1200, 850)
    main_window.setWindowTitle('Симуляция дождя с облаками')
    main_window.show()

    sys.exit(app.exec())
