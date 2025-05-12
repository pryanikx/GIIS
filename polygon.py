import numpy as np
import asyncio
import platform
from matplotlib.patches import Rectangle

class PolygonEditor:
    def __init__(self):
        self.points = []
        self.segment_points = []
        self.normals = []
        self.hull_graham = []
        self.hull_jarvis = []
        self.intersections = []
        self.fill_color = 'black'
        self.pixel_map = np.zeros((100, 100, 3), dtype=np.uint8) + 255  # Белый фон

    def setup_plot(self, ax, cell_size):
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

    def plot_point(self, ax, x, y, color="purple", size=3):
        ax.plot(x, y, 'o', color=color, markersize=size)

    def plot_line(self, ax, p1, p2, color="blue"):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color)

    def redraw_polygon(self, ax, close=False):
        for i in range(len(self.points) - 1):
            self.plot_line(ax, self.points[i], self.points[i + 1], color="blue")
        if close and len(self.points) >= 3:
            self.plot_line(ax, self.points[-1], self.points[0], color="blue")
        for p in self.points:
            self.plot_point(ax, p[0], p[1])

    def draw_segment(self, ax):
        if len(self.segment_points) == 2:
            self.plot_line(ax, self.segment_points[0], self.segment_points[1], color="cyan")
            for p in self.segment_points:
                self.plot_point(ax, p[0], p[1], color="black")

    def is_convex_polygon(self, points):
        if len(points) < 3:
            return False
        n = len(points)
        sign = 0
        for i in range(n):
            p1 = points[i]
            p2 = points[(i + 1) % n]
            p3 = points[(i + 2) % n]
            cross = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])
            if cross != 0:
                if sign == 0:
                    sign = np.sign(cross)
                elif sign != np.sign(cross):
                    return False
        return True

    def is_self_intersecting(self, points):
        n = len(points)
        if n < 4:
            return False
        for i in range(n):
            p1 = points[i]
            p2 = points[(i + 1) % n]
            for j in range(i + 2, n + i - 1):
                q1 = points[j % n]
                q2 = points[(j + 1) % n]
                if self.find_intersection(p1, p2, q1, q2):
                    return True
        return False

    def get_inner_normals(self, points):
        n = len(points)
        normals = []
        centroid = np.mean(points, axis=0)
        for i in range(n):
            p1 = np.array(points[i])
            p2 = np.array(points[(i + 1) % n])
            edge = p2 - p1
            normal = np.array([-edge[1], edge[0]])
            mid_point = (p1 + p2) / 2
            to_centroid = centroid - mid_point
            if np.dot(to_centroid, normal) < 0:
                normal = -normal
            normal = normal / np.linalg.norm(normal) * 10
            normals.append((mid_point, normal))
        return normals

    def show_normals(self, ax):
        self.normals = self.get_inner_normals(self.points)
        for mid_point, normal in self.normals:
            end_point = mid_point + normal
            ax.plot([mid_point[0], end_point[0]], [mid_point[1], end_point[1]], color="green")

    def orientation(self, p, q, r):
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if val == 0:
            return 0
        return 1 if val > 0 else -1

    async def graham_hull(self, ax, debug=False):
        if len(self.points) < 3:
            return False
        points = sorted(self.points)
        n = len(points)
        stack = []
        if debug:
            self.setup_plot(ax, 10)
            self.redraw_polygon(ax, close=True)
            ax.figure.canvas.draw()
            ax.figure.canvas.flush_events()
            await asyncio.sleep(0.4)
        for i in range(n):
            while len(stack) > 1 and self.orientation(stack[-2], stack[-1], points[i]) != -1:
                stack.pop()
                if debug:
                    self.setup_plot(ax, 10)
                    self.redraw_polygon(ax, close=True)
                    for j in range(len(stack) - 1):
                        self.plot_line(ax, stack[j], stack[j + 1], color="purple")
                    ax.figure.canvas.draw()
                    ax.figure.canvas.flush_events()
                    await asyncio.sleep(0.4)
            stack.append(points[i])
            if debug:
                self.setup_plot(ax, 10)
                self.redraw_polygon(ax, close=True)
                for j in range(len(stack) - 1):
                    self.plot_line(ax, stack[j], stack[j + 1], color="purple")
                ax.figure.canvas.draw()
                ax.figure.canvas.flush_events()
                await asyncio.sleep(0.4)
        lower = stack[:]
        stack = []
        for i in range(n - 1, -1, -1):
            while len(stack) > 1 and self.orientation(stack[-2], stack[-1], points[i]) != -1:
                stack.pop()
                if debug:
                    self.setup_plot(ax, 10)
                    self.redraw_polygon(ax, close=True)
                    for j in range(len(lower) - 1):
                        self.plot_line(ax, lower[j], lower[j + 1], color="purple")
                    for j in range(len(stack) - 1):
                        self.plot_line(ax, stack[j], stack[j + 1], color="purple")
                    ax.figure.canvas.draw()
                    ax.figure.canvas.flush_events()
                    await asyncio.sleep(0.4)
            stack.append(points[i])
            if debug:
                self.setup_plot(ax, 10)
                self.redraw_polygon(ax, close=True)
                for j in range(len(lower) - 1):
                    self.plot_line(ax, lower[j], lower[j + 1], color="purple")
                for j in range(len(stack) - 1):
                    self.plot_line(ax, stack[j], stack[j + 1], color="purple")
                ax.figure.canvas.draw()
                ax.figure.canvas.flush_events()
                await asyncio.sleep(0.4)
        stack.pop()
        self.hull_graham = lower + stack
        for i in range(len(self.hull_graham)):
            self.plot_line(ax, self.hull_graham[i], self.hull_graham[(i + 1) % len(self.hull_graham)], color="purple")
        return True

    async def jarvis_hull(self, ax, debug=False):
        if len(self.points) < 3:
            return False
        n = len(self.points)
        hull = []
        l = min(range(n), key=lambda i: (self.points[i][0], self.points[i][1]))
        p = l
        if debug:
            self.setup_plot(ax, 10)
            self.redraw_polygon(ax, close=True)
            ax.figure.canvas.draw()
            ax.figure.canvas.flush_events()
            await asyncio.sleep(0.4)
        while True:
            hull.append(self.points[p])
            q = (p + 1) % n
            for i in range(n):
                if self.orientation(self.points[p], self.points[i], self.points[q]) == -1:
                    q = i
            p = q
            if debug:
                self.setup_plot(ax, 10)
                self.redraw_polygon(ax, close=True)
                for i in range(len(hull) - 1):
                    self.plot_line(ax, hull[i], hull[i + 1], color="orange")
                ax.figure.canvas.draw()
                ax.figure.canvas.flush_events()
                await asyncio.sleep(0.4)
            if p == l:
                break
        self.hull_jarvis = hull
        for i in range(len(self.hull_jarvis)):
            self.plot_line(ax, self.hull_jarvis[i], self.hull_jarvis[(i + 1) % len(self.hull_jarvis)], color="orange")
        return True

    def find_intersection(self, p1, p2, q1, q2):
        def on_segment(p, q, r):
            return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
                    q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))

        o1 = self.orientation(p1, p2, q1)
        o2 = self.orientation(p1, p2, q2)
        o3 = self.orientation(q1, q2, p1)
        o4 = self.orientation(q1, q2, p2)

        if o1 != o2 and o3 != o4:
            denom = ((p1[0] - p2[0]) * (q1[1] - q2[1]) - (p1[1] - p2[1]) * (q1[0] - q2[0]))
            if denom == 0:
                return None
            t = ((p1[0] - q1[0]) * (q1[1] - q2[1]) - (p1[1] - q1[1]) * (q1[0] - q2[0])) / denom
            u = -((p1[0] - p2[0]) * (p1[1] - q1[1]) - (p1[1] - p2[1]) * (p1[0] - q1[0])) / denom
            if 0 <= t <= 1 and 0 <= u <= 1:
                x = p1[0] + t * (p2[0] - p1[0])
                y = p1[1] + t * (p2[1] - p1[1])
                return (x, y)
            return None

        if o1 == 0 and o2 == 0 and o3 == 0 and o4 == 0:
            if on_segment(p1, q1, p2) or on_segment(p1, q2, p2) or on_segment(q1, p1, q2) or on_segment(q1, p2, q2):
                if on_segment(p1, q1, p2):
                    return q1
                if on_segment(p1, q2, p2):
                    return q2
                if on_segment(q1, p1, q2):
                    return p1
                if on_segment(q1, p2, q2):
                    return p2
            return None
        return None

    async def find_intersections(self, ax, debug=False):
        if len(self.segment_points) != 2:
            return False
        if len(self.points) < 2:
            return False
        self.intersections = []
        segment_p1, segment_p2 = self.segment_points
        n = len(self.points)
        for i in range(n):
            poly_p1 = self.points[i]
            poly_p2 = self.points[(i + 1) % n]
            intersection = self.find_intersection(segment_p1, segment_p2, poly_p1, poly_p2)
            if intersection:
                self.intersections.append(intersection)
                self.plot_point(ax, intersection[0], intersection[1], color="yellow", size=5)
                if debug:
                    ax.figure.canvas.draw()
                    ax.figure.canvas.flush_events()
                    await asyncio.sleep(0.4)
        return bool(self.intersections)

    async def is_point_inside(self, point, ax, debug=False):
        if len(self.points) < 3:
            return False
        x, y = point
        n = len(self.points)
        inside = False
        j = n - 1
        if debug:
            self.setup_plot(ax, 10)
            self.redraw_polygon(ax, close=True)
            self.plot_point(ax, x, y, color="red", size=5)
            ax.figure.canvas.draw()
            ax.figure.canvas.flush_events()
            await asyncio.sleep(0.4)
        for i in range(n):
            if ((self.points[i][1] > y) != (self.points[j][1] > y)) and \
               (x < (self.points[j][0] - self.points[i][0]) * (y - self.points[i][1]) / \
                (self.points[j][1] - self.points[i][1] + 1e-10) + self.points[i][0]):
                inside = not inside
                if debug:
                    self.plot_line(ax, self.points[i], self.points[j], color="red")
                    ax.figure.canvas.draw()
                    ax.figure.canvas.flush_events()
                    await asyncio.sleep(0.4)
            j = i
        if debug and inside:
            self.plot_point(ax, x, y, color="green", size=5)
            ax.figure.canvas.draw()
            ax.figure.canvas.flush_events()
            await asyncio.sleep(0.4)
        return inside

    def update_pixel_map(self, x, y, color):
        x, y = int(x), int(y)
        if 0 <= x < 100 and 0 <= y < 100:
            if color == "black":
                self.pixel_map[y, x] = [0, 0, 0]
            elif color == "green":
                self.pixel_map[y, x] = [0, 255, 0]
            elif color == "blue":
                self.pixel_map[y, x] = [0, 0, 255]
            elif color == "yellow":
                self.pixel_map[y, x] = [255, 255, 0]
            elif color == "purple":
                self.pixel_map[y, x] = [128, 0, 128]
            else:
                self.pixel_map[y, x] = [255, 255, 255]

    def get_pixel_color(self, x, y):
        x, y = int(x), int(y)
        if 0 <= x < 100 and 0 <= y < 100:
            pixel = self.pixel_map[y, x]
            if np.array_equal(pixel, [0, 0, 0]):
                return "black"
            elif np.array_equal(pixel, [0, 255, 0]):
                return "green"
            elif np.array_equal(pixel, [0, 0, 255]):
                return "blue"
            elif np.array_equal(pixel, [255, 255, 0]):
                return "yellow"
            elif np.array_equal(pixel, [128, 0, 128]):
                return "purple"
        return "white"

    def draw_line_on_pixel_map(self, p1, p2, color):
        x1, y1 = p1
        x2, y2 = p2
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            self.update_pixel_map(x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    async def basic_scanline(self, ax, debug=False):
        if len(self.points) < 3:
            return False
        min_y = min(p[1] for p in self.points)
        max_y = max(p[1] for p in self.points)
        edges = []
        for i in range(len(self.points)):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            if p1[1] != p2[1]:
                if p1[1] < p2[1]:
                    edges.append((p1, p2))
                else:
                    edges.append((p2, p1))
        for y in range(int(min_y), int(max_y) + 1):
            intersections = []
            for edge in edges:
                p1, p2 = edge
                if p1[1] <= y < p2[1]:
                    dx = p2[0] - p1[0]
                    dy = p2[1] - p1[1]
                    x = p1[0] + dx * (y - p1[1]) / dy
                    intersections.append(x)
                    if debug:
                        self.plot_point(ax, x, y, color="red", size=3)
                        ax.figure.canvas.draw()
                        ax.figure.canvas.flush_events()
                        await asyncio.sleep(0.4)
            intersections.sort()
            for j in range(0, len(intersections), 2):
                if j + 1 >= len(intersections):
                    break
                x_start = int(intersections[j])
                x_end = int(intersections[j + 1])
                for x in range(x_start, x_end + 1):
                    self.update_pixel_map(x, y, self.fill_color)
                    if debug:
                        ax.plot(x, y, 's', color=self.fill_color, markersize=3)
                        ax.figure.canvas.draw()
                        ax.figure.canvas.flush_events()
                        await asyncio.sleep(0.4)
        # Сплошная заливка в конце
        ax.fill([p[0] for p in self.points], [p[1] for p in self.points], color=self.fill_color)
        return True

    async def scanline_fill(self, ax, debug=False):
        if len(self.points) < 3:
            return False
        min_y = min(p[1] for p in self.points)
        max_y = max(p[1] for p in self.points)
        edges = []
        for i in range(len(self.points)):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            if p1[1] != p2[1]:
                edges.append((p1, p2))
        edge_table = []
        for edge in edges:
            p1, p2 = edge
            if p1[1] < p2[1]:
                ymin, ymax = p1[1], p2[1]
                x = p1[0]
            else:
                ymin, ymax = p2[1], p1[1]
                x = p2[0]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            inv_m = dx / dy if dy != 0 else 0
            edge_table.append((ymin, ymax, x, inv_m))
        edge_table.sort(key=lambda e: e[0])
        active_edges = []
        y = int(min_y)
        while y <= int(max_y) and (active_edges or edge_table):
            while edge_table and edge_table[0][0] <= y:
                active_edges.append(edge_table.pop(0))
                if debug:
                    self.setup_plot(ax, 10)
                    self.redraw_polygon(ax, close=True)
                    for edge in active_edges:
                        self.plot_point(ax, edge[2], y, color="red", size=3)
                    ax.figure.canvas.draw()
                    ax.figure.canvas.flush_events()
                    await asyncio.sleep(0.4)
            active_edges = [e for e in active_edges if e[1] > y]
            active_edges.sort(key=lambda e: e[2])
            for i in range(0, len(active_edges), 2):
                x_start = int(active_edges[i][2])
                x_end = int(active_edges[i + 1][2]) if i + 1 < len(active_edges) else x_start
                for x in range(x_start, x_end + 1):
                    self.update_pixel_map(x, y, self.fill_color)
                    if debug:
                        ax.plot(x, y, 's', color=self.fill_color, markersize=3)
                        ax.figure.canvas.draw()
                        ax.figure.canvas.flush_events()
                        await asyncio.sleep(0.4)
            for i in range(len(active_edges)):
                ymin, ymax, x, inv_m = active_edges[i]
                active_edges[i] = (ymin, ymax, x + inv_m, inv_m)
            y += 1
        # Сплошная заливка в конце
        ax.fill([p[0] for p in self.points], [p[1] for p in self.points], color=self.fill_color)
        return True

    async def flood_fill(self, ax, debug=False):
        if len(self.points) < 3:
            return False
        center_x = sum(p[0] for p in self.points) // len(self.points)
        center_y = sum(p[1] for p in self.points) // len(self.points)
        target_color = self.get_pixel_color(center_x, center_y)
        if target_color == self.fill_color:
            return False
        stack = [(center_x, center_y)]
        visited = set()
        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            if 0 <= x < 100 and 0 <= y < 100 and self.get_pixel_color(x, y) == target_color:
                self.update_pixel_map(x, y, self.fill_color)
                if debug:
                    ax.plot(x, y, 's', color=self.fill_color, markersize=3)
                    ax.figure.canvas.draw()
                    ax.figure.canvas.flush_events()
                    await asyncio.sleep(0.4)
                stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
        # Сплошная заливка в конце
        ax.fill([p[0] for p in self.points], [p[1] for p in self.points], color=self.fill_color)
        return True

    async def scanline_flood_fill(self, ax, debug=False):
        if len(self.points) < 3:
            return False
        center_x = sum(p[0] for p in self.points) // len(self.points)
        center_y = sum(p[1] for p in self.points) // len(self.points)
        target_color = self.get_pixel_color(center_x, center_y)
        if target_color == self.fill_color:
            return False
        stack = [(center_x, center_y)]
        while stack:
            x, y = stack.pop()
            left_x = x
            while left_x >= 0 and self.get_pixel_color(left_x, y) == target_color:
                left_x -= 1
            left_x += 1
            span_above = False
            span_below = False
            current_x = left_x
            while current_x < 100 and self.get_pixel_color(current_x, y) == target_color:
                self.update_pixel_map(current_x, y, self.fill_color)
                if debug:
                    ax.plot(current_x, y, 's', color=self.fill_color, markersize=3)
                    ax.figure.canvas.draw()
                    ax.figure.canvas.flush_events()
                    await asyncio.sleep(0.4)
                if y > 0:
                    if not span_above and self.get_pixel_color(current_x, y - 1) == target_color:
                        stack.append((current_x, y - 1))
                        span_above = True
                    elif span_above and self.get_pixel_color(current_x, y - 1) != target_color:
                        span_above = False
                if y < 99:
                    if not span_below and self.get_pixel_color(current_x, y + 1) == target_color:
                        stack.append((current_x, y + 1))
                        span_below = True
                    elif span_below and self.get_pixel_color(current_x, y + 1) != target_color:
                        span_below = False
                current_x += 1
        # Сплошная заливка в конце
        ax.fill([p[0] for p in self.points], [p[1] for p in self.points], color=self.fill_color)
        return True

    async def draw_polygon(self, points, segment_points, cell_size, ax, mode="По умолчанию", fill_color="black", debug=False):
        self.points = points
        self.segment_points = segment_points
        self.fill_color = fill_color
        self.pixel_map = np.zeros((100, 100, 3), dtype=np.uint8) + 255
        for i in range(len(self.points)):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            self.draw_line_on_pixel_map(p1, p2, "blue")
        self.setup_plot(ax, cell_size)
        self.redraw_polygon(ax, close=True)
        if self.is_self_intersecting(self.points):
            print("Предупреждение: полигон самопересекающийся")
        if mode == "Нормали":
            self.show_normals(ax)
        elif mode == "Грэхем":
            await self.graham_hull(ax, debug=debug)
        elif mode == "Джарвис":
            await self.jarvis_hull(ax, debug=debug)
        elif mode == "Пересечения":
            self.draw_segment(ax)
            await self.find_intersections(ax, debug=debug)
        elif mode == "Простая развертка":
            await self.basic_scanline(ax, debug=debug)
        elif mode == "Развертка с активными ребрами":
            await self.scanline_fill(ax, debug=debug)
        elif mode == "Заливка с затравкой":
            await self.flood_fill(ax, debug=debug)
        elif mode == "Построчная заливка":
            await self.scanline_flood_fill(ax, debug=debug)
        elif mode == "Проверка точки":
            if len(segment_points) != 1:
                print("Ошибка: для проверки точки требуется ровно одна точка")
                return
            await self.is_point_inside(segment_points[0], ax, debug=debug)
        elif mode == "По умолчанию":
            self.draw_segment(ax)