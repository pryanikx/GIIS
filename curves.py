import numpy as np
from matplotlib.patches import Rectangle

class CurveDrawer:
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

        cell_size = int(max(1, cell_size))
        ticks = range(0, 101, cell_size)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(range(len(ticks)))
        ax.set_yticklabels(range(len(ticks)))

        for x in range(0, 100, cell_size):
            for y in range(0, 100, cell_size):
                rect = Rectangle((x, y), cell_size, cell_size, fill=False, edgecolor="gray")
                ax.add_patch(rect)

    def hermite_curve(self, P1, P4, R1, R4, cell_size, ax, steps=100, debug=False):
        """Нарисовать кривую Эрмита."""
        t = np.linspace(0, 1, steps)
        h00 = 2 * t**3 - 3 * t**2 + 1
        h10 = t**3 - 2 * t**2 + t
        h01 = -2 * t**3 + 3 * t**2
        h11 = t**3 - t**2

        x = h00 * P1[0] + h10 * R1[0] + h01 * P4[0] + h11 * R4[0]
        y = h00 * P1[1] + h10 * R1[1] + h01 * P4[1] + h11 * R4[1]

        curve_points = np.column_stack((x, y))
        for point in curve_points:
            self.plot_pixel(ax, point[0], point[1], cell_size)
            if debug:
                ax.figure.canvas.draw()
                ax.figure.canvas.flush_events()
        return curve_points

    def bezier_curve(self, P1, P2, P3, P4, cell_size, ax, steps=100, debug=False):
        """Нарисовать кривую Безье."""
        t_values = np.linspace(0, 1, steps)
        T = np.column_stack([t_values ** 3, t_values ** 2, t_values, np.ones_like(t_values)])
        bezier_matrix = np.array([
            [-1, 3, -3, 1],
            [3, -6, 3, 0],
            [-3, 3, 0, 0],
            [1, 0, 0, 0]
        ])
        points_matrix = np.array([P1, P2, P3, P4])
        result = T @ bezier_matrix @ points_matrix
        curve_points = result
        for point in curve_points:
            self.plot_pixel(ax, point[0], point[1], cell_size)
            if debug:
                ax.figure.canvas.draw()
                ax.figure.canvas.flush_events()
        return curve_points

    def bspline_curve(self, points, cell_size, ax, steps=50, debug=False):
        """Нарисовать В-сплайн."""
        if len(points) < 4:
            return []
        extended_points = points + points[:3]
        curve_points = []
        for i in range(len(points)):
            segment = np.array(extended_points[i:i + 4])
            t_values = np.linspace(0, 1, steps)
            T = np.column_stack([t_values ** 3, t_values ** 2, t_values, np.ones_like(t_values)])
            basis_matrix = (1/6) * np.array([
                [-1, 3, -3, 1],
                [3, -6, 3, 0],
                [-3, 0, 3, 0],
                [1, 4, 1, 0]
            ])
            result = T @ basis_matrix @ segment
            curve_points.append(result)
        curve_ps = curve_points[0]
        for i in range(1, len(curve_points)):
            curve_ps = np.vstack((curve_ps, curve_points[i]))
        for point in curve_ps:
            self.plot_pixel(ax, point[0], point[1], cell_size)
            if debug:
                ax.figure.canvas.draw()
                ax.figure.canvas.flush_events()
        return curve_ps

    def draw_curve(self, curve_type, points, cell_size, ax):
        """Нарисовать кривую указанного типа."""
        self.setup_plot(ax, cell_size)
        if curve_type == "Hermite":
            if len(points) != 4:
                raise ValueError("Hermite curve requires 2 points and 2 derivatives (4 vectors)")
            P1, P4, R1, R4 = points
            self.hermite_curve(P1, P4, R1, R4, cell_size, ax)
        elif curve_type == "Bezier":
            if len(points) != 4:
                raise ValueError("Bezier curve requires exactly 4 control points")
            P1, P2, P3, P4 = points
            self.bezier_curve(P1, P2, P3, P4, cell_size, ax)
        elif curve_type == "BSpline":
            if len(points) < 4:
                return
            self.bspline_curve(points, cell_size, ax)

    def start_debug(self, curve_type, points, cell_size, ax):
        """Нарисовать кривую в режиме отладки."""
        self.setup_plot(ax, cell_size)
        if curve_type == "Hermite":
            if len(points) != 4:
                raise ValueError("Hermite curve requires 2 points and 2 derivatives (4 vectors)")
            P1, P4, R1, R4 = points
            self.hermite_curve(P1, P4, R1, R4, cell_size, ax, debug=True)
        elif curve_type == "Bezier":
            if len(points) != 4:
                raise ValueError("Bezier curve requires exactly 4 control points")
            P1, P2, P3, P4 = points
            self.bezier_curve(P1, P2, P3, P4, cell_size, ax, debug=True)
        elif curve_type == "BSpline":
            if len(points) < 4:
                return
            self.bspline_curve(points, cell_size, ax, debug=True)