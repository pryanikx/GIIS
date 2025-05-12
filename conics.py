import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import math

class ConicDrawer:
    def plot_pixel(self, ax, x, y, cell_size, alpha=1.0):
        """Отрисовать пиксель как прямоугольник с возможной прозрачностью."""
        if alpha > 0 and 0 <= x <= 100 and 0 <= y <= 100:
            rect = Rectangle(
                (x * cell_size, y * cell_size),
                cell_size,
                cell_size,
                color=(0, 0, 0, alpha),
                ec="none"
            )
            ax.add_patch(rect)

    def setup_plot(self, ax, cell_size):
        """Инициализировать график с сеткой."""
        ax.clear()
        ax.set_aspect("equal")
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)

        ticks = range(0, 101, cell_size)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(range(len(ticks)))
        ax.set_yticklabels(range(len(ticks)))

        for x in range(0, 100, cell_size):
            for y in range(0, 100, cell_size):
                rect = Rectangle((x, y), cell_size, cell_size, fill=False, edgecolor="gray")
                ax.add_patch(rect)

    def circle_bresenham(self, xc, yc, r, cell_size, ax, debug=False):
        """Нарисовать окружность с помощью алгоритма Брезенхема."""
        x = 0
        y = r
        d = 3 - 2 * r

        def plot_circle_points(x, y):
            self.plot_pixel(ax, xc + x, yc + y, cell_size)
            self.plot_pixel(ax, xc - x, yc + y, cell_size)
            self.plot_pixel(ax, xc + x, yc - y, cell_size)
            self.plot_pixel(ax, xc - x, yc - y, cell_size)
            self.plot_pixel(ax, xc + y, yc + x, cell_size)
            self.plot_pixel(ax, xc - y, yc + x, cell_size)
            self.plot_pixel(ax, xc + y, yc - x, cell_size)
            self.plot_pixel(ax, xc - y, yc - x, cell_size)
            if debug:
                ax.figure.canvas.draw()
                ax.figure.canvas.flush_events()

        plot_circle_points(x, y)
        while y >= x:
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            plot_circle_points(x, y)

    def ellipse_bresenham(self, xc, yc, a, b, cell_size, ax, debug=False):
        """Нарисовать эллипс с помощью модифицированного алгоритма Брезенхема."""
        a2 = a * a
        b2 = b * b
        two_a2 = 2 * a2
        two_b2 = 2 * b2
        x = 0
        y = b
        d = b2 - a2 * b + a2 / 4

        def plot_ellipse_points(x, y):
            self.plot_pixel(ax, xc + x, yc + y, cell_size)
            self.plot_pixel(ax, xc - x, yc + y, cell_size)
            self.plot_pixel(ax, xc + x, yc - y, cell_size)
            self.plot_pixel(ax, xc - x, yc - y, cell_size)
            if debug:
                ax.figure.canvas.draw()
                ax.figure.canvas.flush_events()

        plot_ellipse_points(x, y)
        while b2 * x <= a2 * y:
            x += 1
            if d < 0:
                d += b2 * (2 * x + 1)
            else:
                y -= 1
                d += b2 * (2 * x + 1) - a2 * (2 * y - 1)
            plot_ellipse_points(x, y)

        d = b2 * (x + 0.5) * (x + 0.5) + a2 * (y - 1) * (y - 1) - a2 * b2
        while y > 0:
            y -= 1
            if d > 0:
                d += a2 * (-2 * y + 1)
            else:
                x += 1
                d += b2 * (2 * x + 1) + a2 * (-2 * y + 1)
            plot_ellipse_points(x, y)

    def hyperbola(self, xc, yc, a, b, cell_size, ax, debug=False):
        """Нарисовать гиперболу по уравнению y^2 = 2px (где p вычисляется через a, b)."""
        p = b * b / (2 * a)
        x = 0
        y = 0

        def plot_hyperbola_points(x, y):
            self.plot_pixel(ax, xc + x, yc + y, cell_size)
            self.plot_pixel(ax, xc + x, yc - y, cell_size)
            if debug:
                ax.figure.canvas.draw()
                ax.figure.canvas.flush_events()

        plot_hyperbola_points(x, y)

        limit = 50

        delta = 0
        while x < limit:
            delta = y * y - 2 * p * x
            if delta < 0:
                y += 1
            else:
                x += 1
            plot_hyperbola_points(x, y)

    def parabola(self, xc, yc, p, cell_size, ax, debug=False):
        """Нарисовать параболу (x-xc)^2 = 2p(y-yc)."""
        x = 0
        y = 0

        def plot_parabola_points(x, y):
            self.plot_pixel(ax, xc + x, yc + y, cell_size)
            self.plot_pixel(ax, xc - x, yc + y, cell_size)
            if debug:
                ax.figure.canvas.draw()
                ax.figure.canvas.flush_events()

        plot_parabola_points(x, y)

        limit = 50

        delta = 0
        while y < limit:
            delta = x * x - 2 * p * y
            if delta < 0:
                x += 1
            else:
                y += 1
            plot_parabola_points(x, y)

    def draw_conic(self, conic_type, xc, yc, a, b, p, cell_size, fig, ax):
        """Нарисовать линию второго порядка."""
        self.setup_plot(ax, cell_size)
        if conic_type == "Circle":
            self.circle_bresenham(xc, yc, a, cell_size, ax)
        elif conic_type == "Ellipse":
            self.ellipse_bresenham(xc, yc, a, b, cell_size, ax)
        elif conic_type == "Hyperbola":
            self.hyperbola(xc, yc, a, b, cell_size, ax)
        elif conic_type == "Parabola":
            self.parabola(xc, yc, p, cell_size, ax)

    def start_debug(self, conic_type, xc, yc, a, b, p, cell_size, fig, ax):
        """Нарисовать линию второго порядка в режиме отладки."""
        self.setup_plot(ax, cell_size)
        if conic_type == "Circle":
            self.circle_bresenham(xc, yc, a, cell_size, ax, debug=True)
        elif conic_type == "Ellipse":
            self.ellipse_bresenham(xc, yc, a, b, cell_size, ax, debug=True)
        elif conic_type == "Hyperbola":
            self.hyperbola(xc, yc, a, b, cell_size, ax, debug=True)
        elif conic_type == "Parabola":
            self.parabola(xc, yc, p, cell_size, ax, debug=True)