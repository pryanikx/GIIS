import numpy as np
from matplotlib.patches import Rectangle
from math import cos, sin, radians
import time

class CubeDrawer:
    def __init__(self):
        self.vertices = np.array([
            [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5],
            [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5]
        ], dtype=float)
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Нижняя грань
            (4, 5), (5, 6), (6, 7), (7, 4),  # Верхняя грань
            (0, 4), (1, 5), (2, 6), (3, 7)   # Боковые ребра
        ]
        self.original_vertices = self.vertices.copy()
        self.transform_params = {
            'translate_x': 0, 'translate_y': 0, 'translate_z': 0,
            'rotate_x': 0, 'rotate_y': 0, 'rotate_z': 0,
            'scale': 1, 'perspective': 5,
            'reflect_xy': False, 'reflect_xz': False, 'reflect_yz': False,
            'transform_type': 'all'  # 'translate', 'rotate_x', 'rotate_y', 'rotate_z', 'scale', 'perspective', 'reflect', 'all'
        }

    def reset(self):
        self.vertices = self.original_vertices.copy()
        self.transform_params = {
            'translate_x': 0, 'translate_y': 0, 'translate_z': 0,
            'rotate_x': 0, 'rotate_y': 0, 'rotate_z': 0,
            'scale': 1, 'perspective': 5,
            'reflect_xy': False, 'reflect_xz': False, 'reflect_yz': False,
            'transform_type': 'all'
        }

    def translate(self, dx, dy, dz):
        translation_matrix = np.array([
            [1, 0, 0, dx],
            [0, 1, 0, dy],
            [0, 0, 1, dz],
            [0, 0, 0, 1]
        ])
        self.apply_transform(translation_matrix)

    def rotate_x(self, angle):
        angle = radians(angle)
        rotation_matrix = np.array([
            [1, 0, 0, 0],
            [0, cos(angle), -sin(angle), 0],
            [0, sin(angle), cos(angle), 0],
            [0, 0, 0, 1]
        ])
        self.apply_transform(rotation_matrix)

    def rotate_y(self, angle):
        angle = radians(angle)
        rotation_matrix = np.array([
            [cos(angle), 0, sin(angle), 0],
            [0, 1, 0, 0],
            [-sin(angle), 0, cos(angle), 0],
            [0, 0, 0, 1]
        ])
        self.apply_transform(rotation_matrix)

    def rotate_z(self, angle):
        angle = radians(angle)
        rotation_matrix = np.array([
            [cos(angle), -sin(angle), 0, 0],
            [sin(angle), cos(angle), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        self.apply_transform(rotation_matrix)

    def scale(self, sx, sy, sz):
        scaling_matrix = np.array([
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1]
        ])
        self.apply_transform(scaling_matrix)

    def reflect(self, plane):
        if plane == 'xy':
            matrix = np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, -1, 0],
                [0, 0, 0, 1]
            ])
        elif plane == 'xz':
            matrix = np.array([
                [1, 0, 0, 0],
                [0, -1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])
        elif plane == 'yz':
            matrix = np.array([
                [-1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])
        else:
            return
        self.apply_transform(matrix)

    def apply_perspective(self, distance):
        if distance <= 0:
            distance = 0.001
        perspective_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, -1 / distance, 1]
        ])
        self.apply_transform(perspective_matrix)

    def apply_transform(self, matrix):
        homogeneous_vertices = np.hstack((self.vertices, np.ones((len(self.vertices), 1))))
        transformed_vertices = np.dot(homogeneous_vertices, matrix.T)
        w = transformed_vertices[:, 3]
        self.vertices = transformed_vertices[:, :3] / w[:, np.newaxis]

    def get_projected_vertices(self, width=100, height=100):
        projected = []
        scale = min(width, height) / 3
        for vertex in self.vertices:
            x = vertex[0] * scale + width / 2
            y = -vertex[1] * scale + height / 2
            projected.append((x, y))
        return projected

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

    def draw_cube(self, cell_size, ax, transform_params=None, debug=False):
        self.reset()
        if transform_params:
            self.transform_params.update(transform_params)
        params = self.transform_params
        transform_type = params.get('transform_type', 'all')

        transformations = []
        if transform_type in ['all', 'scale']:
            scale_val = params['scale']
            transformations.append(('scale', lambda: self.scale(scale_val, scale_val, scale_val)))
        if transform_type in ['all', 'rotate_x']:
            transformations.append(('rotate_x', lambda: self.rotate_x(params['rotate_x'])))
        if transform_type in ['all', 'rotate_y']:
            transformations.append(('rotate_y', lambda: self.rotate_y(params['rotate_y'])))
        if transform_type in ['all', 'rotate_z']:
            transformations.append(('rotate_z', lambda: self.rotate_z(params['rotate_z'])))
        if transform_type in ['all', 'translate']:
            transformations.append(('translate', lambda: self.translate(
                params['translate_x'], params['translate_y'], params['translate_z'])))
        if transform_type in ['all', 'reflect']:
            if params['reflect_xy']:
                transformations.append(('reflect_xy', lambda: self.reflect('xy')))
            if params['reflect_xz']:
                transformations.append(('reflect_xz', lambda: self.reflect('xz')))
            if params['reflect_yz']:
                transformations.append(('reflect_yz', lambda: self.reflect('yz')))
        if transform_type in ['all', 'perspective']:
            transformations.append(('perspective', lambda: self.apply_perspective(params['perspective'])))

        self.setup_plot(ax, cell_size)
        if debug:
            for name, transform in transformations:
                transform()
                vertices = self.get_projected_vertices()
                ax.clear()
                self.setup_plot(ax, cell_size)
                for edge in self.edges:
                    x1, y1 = vertices[edge[0]]
                    x2, y2 = vertices[edge[1]]
                    ax.plot([x1, x2], [y1, y2], color='black')
                ax.figure.canvas.draw()
                ax.figure.canvas.flush_events()
                time.sleep(0.5)
        else:
            for name, transform in transformations:
                transform()
            vertices = self.get_projected_vertices()
            for edge in self.edges:
                x1, y1 = vertices[edge[0]]
                x2, y2 = vertices[edge[1]]
                ax.plot([x1, x2], [y1, y2], color='black')

    def start_debug(self, cell_size, ax, transform_params=None):
        self.draw_cube(cell_size, ax, transform_params, debug=True)