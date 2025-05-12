import math
import heapq
import itertools
import numpy as np
from matplotlib.patches import Rectangle

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Event:
    def __init__(self, x, p, a):
        self.x = x
        self.p = p
        self.a = a
        self.valid = True

class Arc:
    def __init__(self, p, a=None, b=None):
        self.p = p
        self.pprev = a
        self.pnext = b
        self.e = None
        self.s0 = None
        self.s1 = None

class Segment:
    def __init__(self, p):
        self.start = p
        self.end = None
        self.done = False

    def finish(self, p):
        if self.done: return
        self.end = p
        self.done = True

class PriorityQueue:
    def __init__(self):
        self.pq = []
        self.entry_finder = {}
        self.counter = itertools.count()

    def push(self, item):
        if item in self.entry_finder: return
        count = next(self.counter)
        entry = [item.x, count, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.pq, entry)

    def remove_entry(self, item):
        entry = self.entry_finder.pop(item)
        entry[-1] = 'Removed'

    def pop(self):
        while self.pq:
            priority, count, item = heapq.heappop(self.pq)
            if item != 'Removed':
                del self.entry_finder[item]
                return item
        raise KeyError('pop from an empty priority queue')

    def top(self):
        while self.pq:
            priority, count, item = heapq.heappop(self.pq)
            if item != 'Removed':
                del self.entry_finder[item]
                self.push(item)
                return item
        raise KeyError('top from an empty priority queue')

    def empty(self):
        return not self.pq

class VoronoiDelaunay:
    def __init__(self):
        self.output = []  # list of line segments for Voronoi
        self.arc = None  # binary tree for parabola arcs
        self.points = PriorityQueue()  # site events
        self.event = PriorityQueue()  # circle events
        self.x0 = -50.0
        self.x1 = -50.0
        self.y0 = 550.0
        self.y1 = 550.0

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

    def process_voronoi(self, points):
        self.output = []
        self.arc = None
        self.points = PriorityQueue()
        self.event = PriorityQueue()
        self.x0 = -50.0
        self.x1 = -50.0
        self.y0 = 550.0
        self.y1 = 550.0

        for pts in points:
            point = Point(pts[0], pts[1])
            self.points.push(point)
            if point.x < self.x0: self.x0 = point.x
            if point.y < self.y0: self.y0 = point.y
            if point.x > self.x1: self.x1 = point.x
            if point.y > self.y1: self.y1 = point.y

        dx = (self.x1 - self.x0 + 1) / 5.0
        dy = (self.y1 - self.y0 + 1) / 5.0
        self.x0 -= dx
        self.x1 += dx
        self.y0 -= dy
        self.y1 += dy

        while not self.points.empty():
            if not self.event.empty() and (self.event.top().x <= self.points.top().x):
                self.process_event()
            else:
                self.process_point()

        while not self.event.empty():
            self.process_event()

        self.finish_edges()

    def process_point(self):
        p = self.points.pop()
        self.arc_insert(p)

    def process_event(self):
        e = self.event.pop()
        if e.valid:
            s = Segment(e.p)
            self.output.append(s)
            a = e.a
            if a.pprev is not None:
                a.pprev.pnext = a.pnext
                a.pprev.s1 = s
            if a.pnext is not None:
                a.pnext.pprev = a.pprev
                a.pnext.s0 = s
            if a.s0 is not None: a.s0.finish(e.p)
            if a.s1 is not None: a.s1.finish(e.p)
            if a.pprev is not None: self.check_circle_event(a.pprev, e.x)
            if a.pnext is not None: self.check_circle_event(a.pnext, e.x)

    def arc_insert(self, p):
        if self.arc is None:
            self.arc = Arc(p)
        else:
            i = self.arc
            while i is not None:
                flag, z = self.intersect(p, i)
                if flag:
                    flag, zz = self.intersect(p, i.pnext)
                    if (i.pnext is not None) and (not flag):
                        i.pnext.pprev = Arc(i.p, i, i.pnext)
                        i.pnext = i.pnext.pprev
                    else:
                        i.pnext = Arc(i.p, i)
                    i.pnext.s1 = i.s1
                    i.pnext.pprev = Arc(p, i, i.pnext)
                    i.pnext = i.pnext.pprev
                    i = i.pnext
                    seg = Segment(z)
                    self.output.append(seg)
                    i.pprev.s1 = i.s0 = seg
                    seg = Segment(z)
                    self.output.append(seg)
                    i.pnext.s0 = i.s1 = seg
                    self.check_circle_event(i, p.x)
                    self.check_circle_event(i.pprev, p.x)
                    self.check_circle_event(i.pnext, p.x)
                    return
                i = i.pnext
            i = self.arc
            while i.pnext is not None:
                i = i.pnext
            i.pnext = Arc(p, i)
            x = self.x0
            y = (i.pnext.p.y + i.p.y) / 2.0
            start = Point(x, y)
            seg = Segment(start)
            i.s1 = i.pnext.s0 = seg
            self.output.append(seg)

    def check_circle_event(self, i, x0):
        if (i.e is not None) and (i.e.x != self.x0):
            i.e.valid = False
        i.e = None
        if (i.pprev is None) or (i.pnext is None): return
        flag, x, o = self.circle(i.pprev.p, i.p, i.pnext.p)
        if flag and (x > self.x0):
            i.e = Event(x, o, i)
            self.event.push(i.e)

    def circle(self, a, b, c):
        if ((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)) > 0: return False, None, None
        A = b.x - a.x
        B = b.y - a.y
        C = c.x - a.x
        D = c.y - a.y
        E = A * (a.x + b.x) + B * (a.y + b.y)
        F = C * (a.x + c.x) + D * (a.y + c.y)
        G = 2 * (A * (c.y - b.y) - B * (c.x - b.x))
        if G == 0: return False, None, None
        ox = (D * E - B * F) / G
        oy = (A * F - C * E) / G
        x = ox + math.sqrt((a.x - ox) ** 2 + (a.y - oy) ** 2)
        o = Point(ox, oy)
        return True, x, o

    def intersect(self, p, i):
        if i is None: return False, None
        if i.p.x == p.x: return False, None
        a = b = 0.0
        if i.pprev is not None:
            a = self.intersection(i.pprev.p, i.p, p.x).y
        if i.pnext is not None:
            b = self.intersection(i.p, i.pnext.p, p.x).y
        if ((i.pprev is None) or (a <= p.y)) and ((i.pnext is None) or (p.y <= b)):
            py = p.y
            px = ((i.p.x) ** 2 + (i.p.y - py) ** 2 - p.x ** 2) / (2 * i.p.x - 2 * p.x)
            return True, Point(px, py)
        return False, None

    def intersection(self, p0, p1, l):
        p = p0
        if p0.x == p1.x:
            py = (p0.y + p1.y) / 2.0
        elif p1.x == l:
            py = p1.y
        elif p0.x == l:
            py = p0.y
            p = p1
        else:
            z0 = 2.0 * (p0.x - l)
            z1 = 2.0 * (p1.x - l)
            a = 1.0 / z0 - 1.0 / z1
            b = -2.0 * (p0.y / z0 - p1.y / z1)
            c = (p0.y ** 2 + p0.x ** 2 - l ** 2) / z0 - (p1.y ** 2 + p1.x ** 2 - l ** 2) / z1
            py = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
        px = (p.x ** 2 + (p.y - py) ** 2 - l ** 2) / (2 * p.x - 2 * l)
        return Point(px, py)

    def finish_edges(self):
        l = self.x1 + (self.x1 - self.x0) + (self.y1 - self.y0)
        i = self.arc
        while i.pnext is not None:
            if i.s1 is not None:
                p = self.intersection(i.p, i.pnext.p, l * 2.0)
                i.s1.finish(p)
            i = i.pnext

    def process_delaunay(self, points):
        def in_circle(p, a, b, c):
            ax, ay = a[0] - p[0], a[1] - p[1]
            bx, by = b[0] - p[0], b[1] - p[1]
            cx, cy = c[0] - p[0], c[1] - p[1]
            det = (ax ** 2 + ay ** 2) * (bx * cy - by * cx) - (bx ** 2 + by ** 2) * (ax * cy - ay * cx) + (
                        cx ** 2 + cy ** 2) * (ax * by - ay * bx)
            return det > 0

        def find_supertriangle(points):
            min_x = min(x for x, y in points)
            max_x = max(x for x, y in points)
            min_y = min(y for x, y in points)
            max_y = max(y for x, y in points)
            dx, dy = max_x - min_x, max_y - min_y
            max_d = max(dx, dy) * 3
            mid_x, mid_y = (min_x + max_x) / 2, (min_y + max_y) / 2
            return [
                (mid_x - max_d, mid_y - max_d),
                (mid_x + max_d, mid_y - max_d),
                (mid_x, mid_y + max_d)
            ]

        if len(points) < 3:
            return []
        supertri = find_supertriangle(points)
        triangles = [supertri]
        temp_points = points + supertri
        for p in points:
            bad_triangles = []
            for t in triangles:
                if in_circle(p, t[0], t[1], t[2]):
                    bad_triangles.append(t)
            polygon = []
            for t in bad_triangles:
                for i in range(3):
                    edge = (t[i], t[(i + 1) % 3])
                    shared = False
                    for t2 in bad_triangles:
                        if t2 != t and edge[0] in t2 and edge[1] in t2:
                            shared = True
                            break
                    if not shared:
                        polygon.append(edge)
            triangles = [t for t in triangles if t not in bad_triangles]
            for edge in polygon:
                triangles.append([edge[0], edge[1], p])
        triangles = [t for t in triangles if not any(p in supertri for p in t)]
        edges = set()
        for t in triangles:
            edges.add(tuple(sorted([t[0], t[1]])))
            edges.add(tuple(sorted([t[1], t[2]])))
            edges.add(tuple(sorted([t[2], t[0]])))
        return list(edges)

    def draw(self, points, cell_size, ax, mode="delaunay"):
        self.setup_plot(ax, cell_size)
        for x, y in points:
            ax.plot(x, y, 'o', color='black', markersize=3)
        if mode == "voronoi":
            self.process_voronoi(points)
            for segment in self.output:
                if segment.end is not None:
                    ax.plot([segment.start.x, segment.end.x], [segment.start.y, segment.end.y], color='blue')
        elif mode == "delaunay":
            edges = self.process_delaunay(points)
            for p1, p2 in edges:
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='blue')