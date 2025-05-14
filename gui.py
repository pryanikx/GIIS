import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from lines import LineDrawer
from conics import ConicDrawer
from curves import CurveDrawer
from cube import CubeDrawer
from polygon import PolygonEditor
from voronoi_delaunay import VoronoiDelaunay

class GraphicEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Graphic Editor")
        self.root.geometry("800x600")
        self.root.configure(bg="lavenderblush2")
        self.line_drawer = LineDrawer()
        self.conic_drawer = ConicDrawer()
        self.curve_drawer = CurveDrawer()
        self.cube_drawer = CubeDrawer()
        self.polygon_editor = PolygonEditor()
        self.voronoi_delaunay = VoronoiDelaunay()
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        header_frame = tk.Frame(root, bg="lavenderblush2")
        header_frame.pack(fill=tk.X, pady=10)
        header_canvas = tk.Canvas(header_frame, height=60, bg="lavenderblush2", highlightthickness=0)
        header_canvas.pack(fill=tk.X, padx=10)
        header_canvas.create_rectangle(0, 0, 800, 60, fill="#d8bfd8", outline="#d8bfd8")
        header_canvas.create_text(400, 30, text="Graphic Editor Pro", font=("Arial", 24, "bold"), fill="#4b0082", justify="center")

        menubar = tk.Menu(root)
        root.config(menu=menubar)
        shapes_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Фигуры", menu=shapes_menu)
        shapes_menu.add_command(label="Линия", command=lambda: self.set_shape("Line"))
        conics_menu = tk.Menu(shapes_menu, tearoff=0)
        shapes_menu.add_cascade(label="Линии второго порядка", menu=conics_menu)
        conics_menu.add_command(label="Окружность", command=lambda: self.set_shape("Circle"))
        conics_menu.add_command(label="Эллипс", command=lambda: self.set_shape("Ellipse"))
        conics_menu.add_command(label="Гипербола", command=lambda: self.set_shape("Hyperbola"))
        conics_menu.add_command(label="Парабола", command=lambda: self.set_shape("Parabola"))
        curves_menu = tk.Menu(shapes_menu, tearoff=0)
        shapes_menu.add_cascade(label="Кривые", menu=curves_menu)
        curves_menu.add_command(label="Эрмита", command=lambda: self.set_shape("Hermite"))
        curves_menu.add_command(label="Безье", command=lambda: self.set_shape("Bezier"))
        curves_menu.add_command(label="В-сплайн", command=lambda: self.set_shape("BSpline"))
        shapes_menu.add_command(label="Куб", command=lambda: self.set_shape("Cube"))
        shapes_menu.add_command(label="Многоугольник", command=lambda: self.set_shape("Polygon"))
        shapes_menu.add_command(label="Триангуляция Делоне", command=lambda: self.set_shape("Delaunay"))
        shapes_menu.add_command(label="Диаграмма Вороного", command=lambda: self.set_shape("Voronoi"))

        toolbar = tk.Frame(root, bg="lavenderblush2")
        toolbar.pack(fill=tk.X, pady=5)
        tk.Label(toolbar, text="Фигура:", bg="lavenderblush2").pack(side=tk.LEFT, padx=5)
        self.shape_var = tk.StringVar(value="Line")
        shape_menu = ttk.Combobox(
            toolbar, textvariable=self.shape_var,
            values=["Line", "Circle", "Ellipse", "Hyperbola", "Parabola", "Hermite", "Bezier", "BSpline", "Cube", "Polygon", "Delaunay", "Voronoi"],
            width=15
        )
        shape_menu.pack(side=tk.LEFT, padx=5)
        shape_menu.bind("<<ComboboxSelected>>", lambda e: self.set_shape(self.shape_var.get()))

        self.input_frame = tk.Frame(root, bg="lavenderblush2")
        self.input_frame.pack(pady=10)
        self.setup_line_inputs()

        button_frame = tk.Frame(root, bg="lavenderblush2")
        button_frame.pack(pady=10)
        draw_button = ttk.Button(button_frame, text="Нарисовать", command=self.draw_shape)
        draw_button.pack(side=tk.LEFT, padx=5)
        debug_button = ttk.Button(button_frame, text="Отладка", command=self.debug_shape)
        debug_button.pack(side=tk.LEFT, padx=5)
        clear_button = ttk.Button(button_frame, text="Очистить", command=self.clear_canvas)
        clear_button.pack(side=tk.LEFT, padx=5)
        self.polygon_mode_var = tk.StringVar(value="По умолчанию")
        ttk.Combobox(button_frame, textvariable=self.polygon_mode_var,
                     values=["По умолчанию", "Нормали", "Грэхем", "Джарвис", "Пересечения",
                             "Проверка точки", "Простая развертка", "Развертка с активными ребрами",
                             "Заливка с затравкой", "Построчная заливка"], width=25).pack(side=tk.LEFT, padx=5)
        tk.Label(button_frame, text="Цвет заливки:", bg="lavenderblush2").pack(side=tk.LEFT, padx=5)
        self.fill_color_var = tk.StringVar(value="black")
        ttk.Combobox(button_frame, textvariable=self.fill_color_var,
                     values=["black", "green", "blue", "yellow", "purple"], width=8).pack(side=tk.LEFT, padx=5)

    def set_shape(self, shape):
        self.shape_var.set(shape)
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        if shape == "Line":
            self.setup_line_inputs()
        elif shape == "Circle":
            self.setup_circle_inputs()
        elif shape == "Ellipse":
            self.setup_ellipse_inputs()
        elif shape == "Hyperbola":
            self.setup_hyperbola_inputs()
        elif shape == "Parabola":
            self.setup_parabola_inputs()
        elif shape in ["Hermite", "Bezier", "BSpline"]:
            self.setup_curve_inputs(shape)
        elif shape == "Cube":
            self.setup_cube_inputs()
        elif shape == "Polygon":
            self.setup_polygon_inputs()
        elif shape in ["Delaunay", "Voronoi"]:
            self.setup_point_set_inputs()

    def setup_line_inputs(self):
        tk.Label(self.input_frame, text="x0", bg="lavenderblush2").grid(row=0, column=0, padx=5, pady=5)
        self.entry_x0 = tk.Entry(self.input_frame, width=10)
        self.entry_x0.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="y0", bg="lavenderblush2").grid(row=0, column=2, padx=5, pady=5)
        self.entry_y0 = tk.Entry(self.input_frame, width=10)
        self.entry_y0.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(self.input_frame, text="x1", bg="lavenderblush2").grid(row=1, column=0, padx=5, pady=5)
        self.entry_x1 = tk.Entry(self.input_frame, width=10)
        self.entry_x1.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="y1", bg="lavenderblush2").grid(row=1, column=2, padx=5, pady=5)
        self.entry_y1 = tk.Entry(self.input_frame, width=10)
        self.entry_y1.grid(row=1, column=3, padx=5, pady=5)
        tk.Label(self.input_frame, text="Размер ячейки", bg="lavenderblush2").grid(row=2, column=0, padx=5, pady=5)
        self.entry_cell_size = tk.Entry(self.input_frame, width=10)
        self.entry_cell_size.grid(row=2, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="Алгоритм", bg="lavenderblush2").grid(row=2, column=2, padx=5, pady=5)
        self.algorithm = tk.StringVar(value="DDA")
        algo_menu = ttk.Combobox(self.input_frame, textvariable=self.algorithm, values=["DDA", "Bresenham", "Wu"], width=10)
        algo_menu.grid(row=2, column=3, padx=5, pady=5)

    def setup_circle_inputs(self):
        tk.Label(self.input_frame, text="Центр x", bg="lavenderblush2").grid(row=0, column=0, padx=5, pady=5)
        self.entry_xc = tk.Entry(self.input_frame, width=10)
        self.entry_xc.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="Центр y", bg="lavenderblush2").grid(row=0, column=2, padx=5, pady=5)
        self.entry_yc = tk.Entry(self.input_frame, width=10)
        self.entry_yc.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(self.input_frame, text="Радиус", bg="lavenderblush2").grid(row=1, column=0, padx=5, pady=5)
        self.entry_r = tk.Entry(self.input_frame, width=10)
        self.entry_r.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="Размер ячейки", bg="lavenderblush2").grid(row=1, column=2, padx=5, pady=5)
        self.entry_cell_size = tk.Entry(self.input_frame, width=10)
        self.entry_cell_size.grid(row=1, column=3, padx=5, pady=5)

    def setup_ellipse_inputs(self):
        tk.Label(self.input_frame, text="Центр x", bg="lavenderblush2").grid(row=0, column=0, padx=5, pady=5)
        self.entry_xc = tk.Entry(self.input_frame, width=10)
        self.entry_xc.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="Центр y", bg="lavenderblush2").grid(row=0, column=2, padx=5, pady=5)
        self.entry_yc = tk.Entry(self.input_frame, width=10)
        self.entry_yc.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(self.input_frame, text="Полуось a", bg="lavenderblush2").grid(row=1, column=0, padx=5, pady=5)
        self.entry_a = tk.Entry(self.input_frame, width=10)
        self.entry_a.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="Полуось b", bg="lavenderblush2").grid(row=1, column=2, padx=5, pady=5)
        self.entry_b = tk.Entry(self.input_frame, width=10)
        self.entry_b.grid(row=1, column=3, padx=5, pady=5)
        tk.Label(self.input_frame, text="Размер ячейки", bg="lavenderblush2").grid(row=2, column=0, padx=5, pady=5)
        self.entry_cell_size = tk.Entry(self.input_frame, width=10)
        self.entry_cell_size.grid(row=2, column=1, padx=5, pady=5)

    def setup_hyperbola_inputs(self):
        tk.Label(self.input_frame, text="Центр x", bg="lavenderblush2").grid(row=0, column=0, padx=5, pady=5)
        self.entry_xc = tk.Entry(self.input_frame, width=10)
        self.entry_xc.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="Центр y", bg="lavenderblush2").grid(row=0, column=2, padx=5, pady=5)
        self.entry_yc = tk.Entry(self.input_frame, width=10)
        self.entry_yc.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(self.input_frame, text="Параметр a", bg="lavenderblush2").grid(row=1, column=0, padx=5, pady=5)
        self.entry_a = tk.Entry(self.input_frame, width=10)
        self.entry_a.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="Параметр b", bg="lavenderblush2").grid(row=1, column=2, padx=5, pady=5)
        self.entry_b = tk.Entry(self.input_frame, width=10)
        self.entry_b.grid(row=1, column=3, padx=5, pady=5)
        tk.Label(self.input_frame, text="Размер ячейки", bg="lavenderblush2").grid(row=2, column=0, padx=5, pady=5)
        self.entry_cell_size = tk.Entry(self.input_frame, width=10)
        self.entry_cell_size.grid(row=2, column=1, padx=5, pady=5)

    def setup_parabola_inputs(self):
        tk.Label(self.input_frame, text="Вершина x", bg="lavenderblush2").grid(row=0, column=0, padx=5, pady=5)
        self.entry_xc = tk.Entry(self.input_frame, width=10)
        self.entry_xc.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="Вершина y", bg="lavenderblush2").grid(row=0, column=2, padx=5, pady=5)
        self.entry_yc = tk.Entry(self.input_frame, width=10)
        self.entry_yc.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(self.input_frame, text="Параметр p", bg="lavenderblush2").grid(row=1, column=0, padx=5, pady=5)
        self.entry_p = tk.Entry(self.input_frame, width=10)
        self.entry_p.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="Размер ячейки", bg="lavenderblush2").grid(row=1, column=2, padx=5, pady=5)
        self.entry_cell_size = tk.Entry(self.input_frame, width=10)
        self.entry_cell_size.grid(row=1, column=3, padx=5, pady=5)

    def setup_curve_inputs(self, curve_type):
        labels = {"Hermite": ["P1 (x, y):", "P4 (x, y):", "R1 (x, y):", "R4 (x, y):"],
                  "Bezier": ["P1 (x, y):", "P2 (x, y):", "P3 (x, y):", "P4 (x, y):"],
                  "BSpline": ["P1 (x, y):", "P2 (x, y):", "P3 (x, y):", "P4 (x, y):", "P5 (x, y):"]}
        self.entries = []
        tk.Label(self.input_frame, text="Размер ячейки", bg="lavenderblush2").grid(row=0, column=0, padx=5, pady=5)
        self.entry_cell_size = tk.Entry(self.input_frame, width=10)
        self.entry_cell_size.grid(row=0, column=1, padx=5, pady=5)
        for i, label in enumerate(labels[curve_type]):
            tk.Label(self.input_frame, text=label, bg="lavenderblush2").grid(row=i+1, column=0, padx=5, pady=5)
            x_entry = tk.Entry(self.input_frame, width=10)
            y_entry = tk.Entry(self.input_frame, width=10)
            x_entry.grid(row=i+1, column=1, padx=5, pady=5)
            y_entry.grid(row=i+1, column=2, padx=5, pady=5)
            self.entries.append((x_entry, y_entry))

    def setup_cube_inputs(self):
        tk.Label(self.input_frame, text="Перемещение X", bg="lavenderblush2").grid(row=0, column=0, padx=5, pady=5)
        self.entry_tx = tk.Entry(self.input_frame, width=10)
        self.entry_tx.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="Перемещение Y", bg="lavenderblush2").grid(row=0, column=2, padx=5, pady=5)
        self.entry_ty = tk.Entry(self.input_frame, width=10)
        self.entry_ty.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(self.input_frame, text="Перемещение Z", bg="lavenderblush2").grid(row=1, column=0, padx=5, pady=5)
        self.entry_tz = tk.Entry(self.input_frame, width=10)
        self.entry_tz.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="Поворот X (град)", bg="lavenderblush2").grid(row=1, column=2, padx=5, pady=5)
        self.entry_rx = tk.Entry(self.input_frame, width=10)
        self.entry_rx.grid(row=1, column=3, padx=5, pady=5)
        tk.Label(self.input_frame, text="Поворот Y (град)", bg="lavenderblush2").grid(row=2, column=0, padx=5, pady=5)
        self.entry_ry = tk.Entry(self.input_frame, width=10)
        self.entry_ry.grid(row=2, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="Поворот Z (град)", bg="lavenderblush2").grid(row=2, column=2, padx=5, pady=5)
        self.entry_rz = tk.Entry(self.input_frame, width=10)
        self.entry_rz.grid(row=2, column=3, padx=5, pady=5)
        tk.Label(self.input_frame, text="Масштаб", bg="lavenderblush2").grid(row=3, column=0, padx=5, pady=5)
        self.entry_scale = tk.Entry(self.input_frame, width=10)
        self.entry_scale.grid(row=3, column=1, padx=5, pady=5)
        tk.Label(self.input_frame, text="Перспектива", bg="lavenderblush2").grid(row=3, column=2, padx=5, pady=5)
        self.entry_perspective = tk.Entry(self.input_frame, width=10)
        self.entry_perspective.grid(row=3, column=3, padx=5, pady=5)
        tk.Label(self.input_frame, text="Размер ячейки", bg="lavenderblush2").grid(row=4, column=0, padx=5, pady=5)
        self.entry_cell_size = tk.Entry(self.input_frame, width=10)
        self.entry_cell_size.grid(row=4, column=1, padx=5, pady=5)

    def setup_polygon_inputs(self):
        tk.Label(self.input_frame, text="Точки многоугольника (x, y) через пробел, по одной на строку", bg="lavenderblush2").grid(row=0, column=0, columnspan=4, padx=5, pady=5)
        self.entry_points = tk.Text(self.input_frame, height=5, width=30)
        self.entry_points.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        tk.Label(self.input_frame, text="Точки отрезка/точки (x, y) через пробел, по одной на строку", bg="lavenderblush2").grid(row=2, column=0, columnspan=4, padx=5, pady=5)
        self.entry_segment = tk.Text(self.input_frame, height=2, width=30)
        self.entry_segment.grid(row=3, column=0, columnspan=4, padx=5, pady=5)
        tk.Label(self.input_frame, text="Размер ячейки", bg="lavenderblush2").grid(row=4, column=0, padx=5, pady=5)
        self.entry_cell_size = tk.Entry(self.input_frame, width=10)
        self.entry_cell_size.grid(row=4, column=1, padx=5, pady=5)
        tk.Button(self.input_frame, text="Проверить выпуклость", command=self.check_convex).grid(row=4, column=2, columnspan=2, padx=5, pady=5)

    def setup_point_set_inputs(self):
        tk.Label(self.input_frame, text="Точки (x, y) через пробел, по одной на строку", bg="lavenderblush2").grid(row=0, column=0, columnspan=4, padx=5, pady=5)
        self.entry_points = tk.Text(self.input_frame, height=5, width=30)
        self.entry_points.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
        tk.Label(self.input_frame, text="Размер ячейки", bg="lavenderblush2").grid(row=2, column=0, padx=5, pady=5)
        self.entry_cell_size = tk.Entry(self.input_frame, width=10)
        self.entry_cell_size.grid(row=2, column=1, padx=5, pady=5)

    def get_polygon_points(self, text_widget):
        points_text = text_widget.get("1.0", tk.END).strip().split("\n")
        points = []
        for line in points_text:
            if line.strip():
                try:
                    x, y = map(float, line.strip().split())
                    points.append((x, y))
                except ValueError:
                    messagebox.showerror("Ошибка", "Введите корректные координаты (x y)")
                    return None
        return points if points else None

    def check_convex(self):
        points = self.get_polygon_points(self.entry_points)
        if not points or len(points) < 3:
            messagebox.showerror("Ошибка", "Нужно минимум 3 точки для многоугольника")
            return
        is_convex = self.polygon_editor.is_convex_polygon(points)
        messagebox.showinfo("Проверка выпуклости", f"Многоугольник {'выпуклый' if is_convex else 'не выпуклый'}")

    def draw_shape(self):
        try:
            shape = self.shape_var.get()
            cell_size = int(float(self.entry_cell_size.get()))
            if cell_size < 1:
                raise ValueError("Размер ячейки должен быть >= 1")
            if shape == "Line":
                x0 = float(self.entry_x0.get())
                y0 = float(self.entry_y0.get())
                x1 = float(self.entry_x1.get())
                y1 = float(self.entry_y1.get())
                method = {"DDA": 1, "Bresenham": 2, "Wu": 3}[self.algorithm.get()]
                self.line_drawer.draw_line(method, x0, y0, x1, y1, cell_size, self.fig, self.ax)
            elif shape in ["Circle", "Ellipse", "Hyperbola", "Parabola"]:
                xc = float(self.entry_xc.get())
                yc = float(self.entry_yc.get())
                if shape == "Circle":
                    r = float(self.entry_r.get())
                    self.conic_drawer.draw_conic("Circle", xc, yc, r, 0, 0, cell_size, self.fig, self.ax)
                elif shape == "Ellipse":
                    a = float(self.entry_a.get())
                    b = float(self.entry_b.get())
                    self.conic_drawer.draw_conic("Ellipse", xc, yc, a, b, 0, cell_size, self.fig, self.ax)
                elif shape == "Hyperbola":
                    a = float(self.entry_a.get())
                    b = float(self.entry_b.get())
                    self.conic_drawer.draw_conic("Hyperbola", xc, yc, a, b, 0, cell_size, self.fig, self.ax)
                elif shape == "Parabola":
                    p = float(self.entry_p.get())
                    self.conic_drawer.draw_conic("Parabola", xc, yc, 0, 0, p, cell_size, self.fig, self.ax)
            elif shape in ["Hermite", "Bezier", "BSpline"]:
                points = self.get_curve_points()
                if points:
                    self.curve_drawer.draw_curve(shape, points, cell_size, self.ax)
            elif shape == "Cube":
                transform_params = {
                    'translate_x': float(self.entry_tx.get()),
                    'translate_y': float(self.entry_ty.get()),
                    'translate_z': float(self.entry_tz.get()),
                    'rotate_x': float(self.entry_rx.get()),
                    'rotate_y': float(self.entry_ry.get()),
                    'rotate_z': float(self.entry_rz.get()),
                    'scale': float(self.entry_scale.get()),
                    'perspective': float(self.entry_perspective.get())
                }
                self.cube_drawer.draw_cube(cell_size, self.ax, transform_params)
            elif shape == "Polygon":
                points = self.get_polygon_points(self.entry_points)
                segment_points = self.get_polygon_points(self.entry_segment) or []
                mode = self.polygon_mode_var.get()
                if not points:
                    messagebox.showerror("Ошибка", "Введите точки многоугольника")
                    return
                if mode in ["Простая развертка", "Развертка с активными ребрами", "Заливка с затравкой", "Построчная заливка"] and len(points) < 3:
                    messagebox.showerror("Ошибка", "Для заполнения нужно минимум 3 точки")
                    return
                if mode == "Пересечения" and len(segment_points) != 2:
                    messagebox.showwarning("Предупреждение", "Для поиска пересечений нужен отрезок (2 точки)")
                    return
                if mode == "Проверка точки" and len(segment_points) != 1:
                    messagebox.showwarning("Предупреждение", "Для проверки точки нужна ровно одна точка")
                    return
                asyncio.run(self.polygon_editor.draw_polygon(points, segment_points, cell_size, self.ax,
                                                            mode=mode, fill_color=self.fill_color_var.get()))
            elif shape in ["Delaunay", "Voronoi"]:
                points = self.get_polygon_points(self.entry_points)
                if points and len(points) >= 3:
                    unique_points = []
                    seen = set()
                    for x, y in points:
                        if (x, y) not in seen and 0 <= x <= 100 and 0 <= y <= 100:
                            unique_points.append((x, y))
                            seen.add((x, y))
                        else:
                            messagebox.showwarning("Предупреждение", f"Пропущена точка ({x}, {y}): вне области или дубликат")
                    if len(unique_points) < 3:
                        messagebox.showerror("Ошибка", "Нужно минимум 3 уникальные точки в области [0, 100]")
                        return
                    asyncio.run(self.voronoi_delaunay.draw(unique_points, cell_size, self.ax, mode=shape.lower()))
                else:
                    messagebox.showerror("Ошибка", "Нужно минимум 3 точки")
            self.canvas.draw()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Пожалуйста, введите корректные числа: {str(e)}")

    def debug_shape(self):
        try:
            shape = self.shape_var.get()
            cell_size = int(float(self.entry_cell_size.get()))
            if cell_size < 1:
                raise ValueError("Размер ячейки должен быть >= 1")
            if shape == "Line":
                x0 = float(self.entry_x0.get())
                y0 = float(self.entry_y0.get())
                x1 = float(self.entry_x1.get())
                y1 = float(self.entry_y1.get())
                method = {"DDA": 1, "Bresenham": 2, "Wu": 3}[self.algorithm.get()]
                self.line_drawer.start_debug(method, x0, y0, x1, y1, cell_size, self.fig, self.ax)
            elif shape in ["Circle", "Ellipse", "Hyperbola", "Parabola"]:
                xc = float(self.entry_xc.get())
                yc = float(self.entry_yc.get())
                if shape == "Circle":
                    r = float(self.entry_r.get())
                    self.conic_drawer.start_debug("Circle", xc, yc, r, 0, 0, cell_size, self.fig, self.ax)
                elif shape == "Ellipse":
                    a = float(self.entry_a.get())
                    b = float(self.entry_b.get())
                    self.conic_drawer.start_debug("Ellipse", xc, yc, a, b, 0, cell_size, self.fig, self.ax)
                elif shape == "Hyperbola":
                    a = float(self.entry_a.get())
                    b = float(self.entry_b.get())
                    self.conic_drawer.start_debug("Hyperbola", xc, yc, a, b, 0, cell_size, self.fig, self.ax)
                elif shape == "Parabola":
                    p = float(self.entry_p.get())
                    self.conic_drawer.start_debug("Parabola", xc, yc, 0, 0, p, cell_size, self.fig, self.ax)
            elif shape in ["Hermite", "Bezier", "BSpline"]:
                points = self.get_curve_points()
                if points:
                    self.curve_drawer.start_debug(shape, points, cell_size, self.ax)
            elif shape == "Cube":
                transform_params = {
                    'translate_x': float(self.entry_tx.get()),
                    'translate_y': float(self.entry_ty.get()),
                    'translate_z': float(self.entry_tz.get()),
                    'rotate_x': float(self.entry_rx.get()),
                    'rotate_y': float(self.entry_ry.get()),
                    'rotate_z': float(self.entry_rz.get()),
                    'scale': float(self.entry_scale.get()),
                    'perspective': float(self.entry_perspective.get())
                }
                self.cube_drawer.start_debug(cell_size, self.ax, transform_params)
            elif shape == "Polygon":
                points = self.get_polygon_points(self.entry_points)
                segment_points = self.get_polygon_points(self.entry_segment) or []
                mode = self.polygon_mode_var.get()
                if not points:
                    messagebox.showerror("Ошибка", "Введите точки многоугольника")
                    return
                if mode in ["Простая развертка", "Развертка с активными ребрами", "Заливка с затравкой", "Построчная заливка"] and len(points) < 3:
                    messagebox.showerror("Ошибка", "Для заполнения нужно минимум 3 точки")
                    return
                if mode == "Пересечения" and len(segment_points) != 2:
                    messagebox.showwarning("Предупреждение", "Для поиска пересечений нужен отрезок (2 точки)")
                    return
                if mode == "Проверка точки" and len(segment_points) != 1:
                    messagebox.showwarning("Предупреждение", "Для проверки точки нужна ровно одна точка")
                    return
                asyncio.run(self.polygon_editor.draw_polygon(points, segment_points, cell_size, self.ax,
                                                            mode=mode, fill_color=self.fill_color_var.get(), debug=True))
            elif shape in ["Delaunay", "Voronoi"]:
                points = self.get_polygon_points(self.entry_points)
                if points and len(points) >= 3:
                    unique_points = []
                    seen = set()
                    for x, y in points:
                        if (x, y) not in seen and 0 <= x <= 100 and 0 <= y <= 100:
                            unique_points.append((x, y))
                            seen.add((x, y))
                        else:
                            messagebox.showwarning("Предупреждение", f"Пропущена точка ({x}, {y}): вне области или дубликат")
                    if len(unique_points) < 3:
                        messagebox.showerror("Ошибка", "Нужно минимум 3 уникальные точки в области [0, 100]")
                        return
                    try:
                        asyncio.run(self.voronoi_delaunay.draw(unique_points, cell_size, self.ax, mode=shape.lower(), debug=True))
                    except Exception as e:
                        messagebox.showerror("Ошибка отладки", f"Не удалось выполнить отладку: {str(e)}")
                else:
                    messagebox.showerror("Ошибка", "Нужно минимум 3 точки")
            self.canvas.draw()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Пожалуйста, введите корректные числа: {str(e)}")

    def clear_canvas(self):
        self.ax.clear()
        self.canvas.draw()

    def get_curve_points(self):
        points = []
        for x_entry, y_entry in self.entries:
            try:
                x = float(x_entry.get())
                y = float(y_entry.get())
                points.append((x, y))
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные координаты (x y)")
                return None
        return points if points else None