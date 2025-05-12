import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

class LineDrawer:
    def create_empty_plot(self):
        """Create an empty matplotlib plot."""
        fig, ax = plt.subplots()
        ax.set_aspect("equal")
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        return fig, ax

    def plot_pixel(self, ax, x, y, cell_size, alpha=1.0):
        """Plot a pixel as a rectangle with optional transparency."""
        if alpha > 0:
            rect = Rectangle(
                (x * cell_size, y * cell_size),
                cell_size,
                cell_size,
                color=(0, 0, 0, alpha),
                ec="none"
            )
            ax.add_patch(rect)

    def setup_plot(self, ax, cell_size):
        """Initialize the plot with a grid."""
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

    def dda_line(self, x0, y0, x1, y1, cell_size, ax, debug=False):
        """Draw a line using the DDA algorithm."""
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy)) or 1
        dx = dx / steps
        dy = dy / steps
        x = x0 + 0.5 * (1 if dx > 0 else -1 if dx < 0 else 0)
        y = y0 + 0.5 * (1 if dy > 0 else -1 if dy < 0 else 0)

        self.plot_pixel(ax, int(x), int(y), cell_size)
        if debug:
            ax.figure.canvas.draw()
            ax.figure.canvas.flush_events()

        for _ in range(int(steps)):
            x += dx
            y += dy
            self.plot_pixel(ax, int(x), int(y), cell_size)
            if debug:
                ax.figure.canvas.draw()
                ax.figure.canvas.flush_events()

    def bresenham_line(self, x0, y0, x1, y1, cell_size, ax, debug=False):
        """Draw a line using Bresenham's algorithm."""
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        x, y = x0, y0

        self.plot_pixel(ax, x, y, cell_size)
        if debug:
            ax.figure.canvas.draw()
            ax.figure.canvas.flush_events()

        if dx > dy:
            err = 2 * dy - dx
            while x != x1:
                x += sx
                if err >= 0:
                    y += sy
                    err -= 2 * dx
                err += 2 * dy
                self.plot_pixel(ax, x, y, cell_size)
                if debug:
                    ax.figure.canvas.draw()
                    ax.figure.canvas.flush_events()
        else:
            err = 2 * dx - dy
            while y != y1:
                y += sy
                if err >= 0:
                    x += sx
                    err -= 2 * dy
                err += 2 * dx
                self.plot_pixel(ax, x, y, cell_size)
                if debug:
                    ax.figure.canvas.draw()
                    ax.figure.canvas.flush_events()

    def wu_line(self, x0, y0, x1, y1, cell_size, ax, debug=False):
        """Draw a line using Wu's anti-aliasing algorithm."""
        x0, y0, x1, y1 = float(x0), float(y0), float(x1), float(y1)
        steep = abs(y1 - y0) > abs(x1 - x0)

        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = y1 - y0
        gradient = dy / dx if dx != 0 else 1

        xpxl1 = int(x0 + 0.5)
        xpxl2 = int(x1 + 0.5)
        intery = y0 + gradient * (xpxl1 - x0)

        for x in range(xpxl1, xpxl2 + 1):
            alpha1 = 1 - (intery % 1)
            alpha2 = intery % 1
            if steep:
                self.plot_pixel(ax, int(intery), x, cell_size, alpha1)
                self.plot_pixel(ax, int(intery) + 1, x, cell_size, alpha2)
            else:
                self.plot_pixel(ax, x, int(intery), cell_size, alpha1)
                self.plot_pixel(ax, x, int(intery) + 1, cell_size, alpha2)
            if debug:
                ax.figure.canvas.draw()
                ax.figure.canvas.flush_events()
            intery += gradient

    def draw_line(self, method, x0, y0, x1, y1, cell_size, fig, ax):
        """Draw a line using the specified method."""
        self.setup_plot(ax, cell_size)
        match method:
            case 1:
                self.dda_line(x0, y0, x1, y1, cell_size, ax)
            case 2:
                self.bresenham_line(x0, y0, x1, y1, cell_size, ax)
            case 3:
                self.wu_line(x0, y0, x1, y1, cell_size, ax)
            case _:
                self.dda_line(x0, y0, x1, y1, cell_size, ax)

    def start_debug(self, method, x0, y0, x1, y1, cell_size, fig, ax):
        """Draw a line in debug mode with step-by-step visualization."""
        self.setup_plot(ax, cell_size)
        match method:
            case 1:
                self.dda_line(x0, y0, x1, y1, cell_size, ax, debug=True)
            case 2:
                self.bresenham_line(x0, y0, x1, y1, cell_size, ax, debug=True)
            case 3:
                self.wu_line(x0, y0, x1, y1, cell_size, ax, debug=True)
            case _:
                self.dda_line(x0, y0, x1, y1, cell_size, ax, debug=True)