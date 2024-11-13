import sys
import json
import random
import math
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import QTimer, Qt

class Drop:
    def __init__(self, width, height, config):
        self.width = width
        self.height = height
        self.x = random.uniform(0, self.width)
        self.y = random.uniform(0, self.height)
        self.speed = random.uniform(config['min_speed'], config['max_speed'])
        self.angle = random.uniform(config['min_angle'], config['max_angle'])
        self.length = random.uniform(config['min_length'], config['max_length'])

    def update(self, dt):
        rad_angle = math.radians(self.angle)
        self.y += self.speed * dt * math.cos(rad_angle)
        self.x += self.speed * dt * math.sin(rad_angle)

        if self.y > self.height:
            self.y = 0
            self.x = random.uniform(0, self.width)
            self.speed = random.uniform(config['min_speed'], config['max_speed'])
            self.angle = random.uniform(config['min_angle'], config['max_angle'])
            self.length = random.uniform(config['min_length'], config['max_length'])


class RainWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.width = 600
        self.height = 600
        self.drops = [Drop(self.width, self.height, self.config) for _ in
                      range(random.randint(self.config['min_drops'], self.config['max_drops']))]
        self.initUI()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(16)  # Запуск таймера с интервалом 16 мс (~60 FPS)

    def initUI(self):
        self.setGeometry(100, 100, self.width, self.height)
        self.setWindowTitle('Rain Simulation')

    def update_simulation(self):
        self.update_drops()
        self.repaint()

    def update_drops(self):
        if random.random() < 0.05 and len(self.drops) < self.config['max_drops']:
            self.drops.append(Drop(self.width, self.height, self.config))
        if random.random() < 0.05 and len(self.drops) > self.config['min_drops']:
            self.drops.pop()

        for drop in self.drops:
            drop.update(1 / 60)  # dt, учитываем, что таймер работает с 60 FPS

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(*self.config['background_color']))

        pen = QPen(QColor(*self.config['drop_color']))
        pen.setWidth(2)
        painter.setPen(pen)

        for drop in self.drops:
            x_end = drop.x + drop.length * math.sin(math.radians(drop.angle))
            y_end = drop.y + drop.length * math.cos(math.radians(drop.angle))
            painter.drawLine(int(drop.x), int(drop.y), int(x_end), int(y_end))


if __name__ == '__main__':
    with open('file/config.json', 'r') as config_file:
        config = json.load(config_file)

    app = QApplication(sys.argv)
    rain_widget = RainWidget(config)
    rain_widget.show()
    sys.exit(app.exec_())
