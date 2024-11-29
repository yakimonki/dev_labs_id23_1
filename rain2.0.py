import sys
import json
import random
from PyQt6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QPushButton, QSlider, QLabel, QHBoxLayout, QComboBox, QDialog
)
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import QTimer, Qt, QRect


class Drop:
    def __init__(self, x, y, config):
        self.x = x
        self.y = y
        self.speed = random.uniform(config['min_speed'], config['max_speed'])
        self.length = random.uniform(config['min_length'], config['max_length'])

    def update(self, dt, width, height):
        self.y += self.speed * dt
        if self.y > height:
            self.y = 0
            self.x = random.uniform(0, width)


class Cloud:
    def __init__(self, x, y, width, height, config, shape="Прямоугольник"):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.config = config
        self.shape = shape
        self.density = config['default_drops']
        self.drops = [self.create_drop() for _ in range(self.density)]

    def create_drop(self):
        drop_x = random.uniform(self.x, self.x + self.width)
        drop_y = random.uniform(self.y, self.y + self.height)
        return Drop(drop_x, drop_y, self.config)

    def update(self, dt, screen_width, screen_height):
        for drop in self.drops:
            drop.update(dt, screen_width, screen_height)

    def adjust_drops(self, new_density):
        if new_density > len(self.drops):
            self.drops.extend(self.create_drop() for _ in range(new_density - len(self.drops)))
        elif new_density < len(self.drops):
            self.drops = self.drops[:new_density]

    def draw(self, painter):
        painter.setBrush(QColor(200, 200, 200, 150))
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
        self.clouds = [Cloud(200, 50, 200, 50, self.config)]
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
        painter.fillRect(self.rect(), QColor(*self.config['background_color']))

        for cloud in self.clouds:
            cloud.draw(painter)

        if self.selected_cloud:
            pen = QPen(Qt.GlobalColor.red)
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawRect(self.selected_cloud.x, self.selected_cloud.y,
                             self.selected_cloud.width, self.selected_cloud.height)

        pen = QPen(QColor(*self.config['drop_color']))
        pen.setWidth(2)
        painter.setPen(pen)

        for cloud in self.clouds:
            for drop in cloud.drops:
                x_end = drop.x
                y_end = drop.y + drop.length
                painter.drawLine(int(drop.x), int(drop.y), int(x_end), int(y_end))

    def update_simulation(self):
        for cloud in self.clouds:
            cloud.update(1 / 60, self.width, self.height)
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

        self.density_slider = QSlider(Qt.Orientation.Horizontal)
        self.density_slider.setRange(10, 200)
        self.density_slider.setValue(self.selected_cloud.density)
        self.density_slider.valueChanged.connect(self.change_density)
        layout.addWidget(QLabel("Плотность капель:"))
        layout.addWidget(self.density_slider)

        self.setLayout(layout)

    def change_shape(self, shape):
        self.selected_cloud.shape = shape

    def change_density(self, value):
        self.selected_cloud.adjust_drops(value)


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
        self.rain_widget.clouds.append(Cloud(100, 100, 200, 50, self.rain_widget.config))

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
