import tkinter as tk
import math


class CircleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Moving Point on Circle")
        self.canvas_size = 600
        self.radius = 200
        self.angle = 0
        self.speed = 0.15  # Измените это значение, чтобы изменить скорость
        self.center = (self.canvas_size // 2, self.canvas_size // 2)

        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg='white')
        self.canvas.pack()

        # Рисуем окружность
        self.canvas.create_oval(
            self.center[0] - self.radius,
            self.center[1] - self.radius,

            self.center[0] + self.radius,
            self.center[1] + self.radius
        )

        self.point = self.canvas.create_oval(0, 0, 40, 40, fill='blue')

        self.update_position()

    def update_position(self):
        x = self.center[0] + self.radius * math.cos(self.angle)
        y = self.center[1] + self.radius * math.sin(self.angle)

        self.canvas.coords(self.point, x - 5, y - 5, x + 5, y + 5)

        self.angle += self.speed
        if self.angle >= 2 * math.pi:
            self.angle = 0

        self.root.after(50, self.update_position)  # обновляем каждые 50 мс


if __name__ == "__main__":
    root = tk.Tk()
    app = CircleApp(root)
    root.mainloop()