"""Ventana principal de la aplicación de derivadas."""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

# Configurar backend ANTES de importar pyplot
import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from typing import Optional

from core.derivative import DerivativeEngine


class MainWindow:
    """Ventana principal de la aplicación."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Calculadora de Derivadas - Animación de Funciones")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # Motor de derivadas
        self.engine = DerivativeEngine()

        # Estado de animación
        self.animation: Optional[FuncAnimation] = None
        self.is_playing = False
        self.current_t = 0.0
        self.t_min = 0.0
        self.t_max = 5.0
        self.animation_speed = 50  # ms entre frames

        # Sliders de constantes
        self.constant_sliders = {}
        self.constant_labels = {}

        # Configurar la interfaz
        self._setup_ui()

        # Cargar ejemplo inicial
        self._load_example()

    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Frame principal con dos columnas
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Panel izquierdo (controles)
        self._setup_control_panel()

        # Panel derecho (gráficas)
        self._setup_graph_panel()

    def _setup_control_panel(self):
        """Configura el panel de controles."""
        control_frame = ttk.LabelFrame(self.main_frame, text="Controles", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # --- Entrada de función ---
        func_frame = ttk.LabelFrame(control_frame, text="Función", padding="5")
        func_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(func_frame, text="f(t) =").pack(anchor=tk.W)
        self.func_entry = ttk.Entry(func_frame, width=30, font=('Consolas', 11))
        self.func_entry.pack(fill=tk.X, pady=2)
        self.func_entry.bind('<Return>', lambda e: self._on_function_change())

        # Variable independiente
        var_frame = ttk.Frame(func_frame)
        var_frame.pack(fill=tk.X, pady=5)
        ttk.Label(var_frame, text="Variable:").pack(side=tk.LEFT)
        self.var_combo = ttk.Combobox(var_frame, values=['t', 'x', 's'], width=5, state='readonly')
        self.var_combo.set('t')
        self.var_combo.pack(side=tk.LEFT, padx=5)
        self.var_combo.bind('<<ComboboxSelected>>', lambda e: self._on_function_change())

        ttk.Button(func_frame, text="Calcular", command=self._on_function_change).pack(fill=tk.X, pady=5)

        # --- Resultados de derivadas ---
        deriv_frame = ttk.LabelFrame(control_frame, text="Derivadas", padding="5")
        deriv_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(deriv_frame, text="f'(t) =").pack(anchor=tk.W)
        self.deriv1_label = ttk.Label(deriv_frame, text="", font=('Consolas', 10), foreground='blue')
        self.deriv1_label.pack(anchor=tk.W, pady=(0, 5))

        ttk.Label(deriv_frame, text="f''(t) =").pack(anchor=tk.W)
        self.deriv2_label = ttk.Label(deriv_frame, text="", font=('Consolas', 10), foreground='green')
        self.deriv2_label.pack(anchor=tk.W)

        # --- Rango de tiempo ---
        range_frame = ttk.LabelFrame(control_frame, text="Rango de t", padding="5")
        range_frame.pack(fill=tk.X, pady=(0, 10))

        t_min_frame = ttk.Frame(range_frame)
        t_min_frame.pack(fill=tk.X)
        ttk.Label(t_min_frame, text="t mín:").pack(side=tk.LEFT)
        self.t_min_entry = ttk.Entry(t_min_frame, width=8)
        self.t_min_entry.insert(0, "0")
        self.t_min_entry.pack(side=tk.RIGHT)

        t_max_frame = ttk.Frame(range_frame)
        t_max_frame.pack(fill=tk.X, pady=5)
        ttk.Label(t_max_frame, text="t máx:").pack(side=tk.LEFT)
        self.t_max_entry = ttk.Entry(t_max_frame, width=8)
        self.t_max_entry.insert(0, "5")
        self.t_max_entry.pack(side=tk.RIGHT)

        ttk.Button(range_frame, text="Actualizar Rango", command=self._update_range).pack(fill=tk.X)

        # --- Controles de animación ---
        anim_frame = ttk.LabelFrame(control_frame, text="Animación", padding="5")
        anim_frame.pack(fill=tk.X, pady=(0, 10))

        btn_frame = ttk.Frame(anim_frame)
        btn_frame.pack(fill=tk.X)

        self.play_btn = ttk.Button(btn_frame, text="▶ Play", command=self._toggle_animation, width=8)
        self.play_btn.pack(side=tk.LEFT, padx=2)

        self.reset_btn = ttk.Button(btn_frame, text="⟲ Reset", command=self._reset_animation, width=8)
        self.reset_btn.pack(side=tk.LEFT, padx=2)

        # Velocidad
        speed_frame = ttk.Frame(anim_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="Velocidad:").pack(side=tk.LEFT)
        self.speed_scale = ttk.Scale(speed_frame, from_=10, to=200, orient=tk.HORIZONTAL,
                                      command=self._on_speed_change)
        self.speed_scale.set(50)
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Valores actuales
        values_frame = ttk.LabelFrame(anim_frame, text="Valores Actuales", padding="5")
        values_frame.pack(fill=tk.X, pady=5)

        self.t_value_label = ttk.Label(values_frame, text="t = 0.00", font=('Consolas', 10))
        self.t_value_label.pack(anchor=tk.W)
        self.f_value_label = ttk.Label(values_frame, text="f(t) = 0.00", font=('Consolas', 10))
        self.f_value_label.pack(anchor=tk.W)
        self.v_value_label = ttk.Label(values_frame, text="f'(t) = 0.00", font=('Consolas', 10), foreground='blue')
        self.v_value_label.pack(anchor=tk.W)
        self.a_value_label = ttk.Label(values_frame, text="f''(t) = 0.00", font=('Consolas', 10), foreground='green')
        self.a_value_label.pack(anchor=tk.W)

        # --- Frame para sliders de constantes ---
        self.constants_frame = ttk.LabelFrame(control_frame, text="Constantes", padding="5")
        self.constants_frame.pack(fill=tk.X, pady=(0, 10))

        # --- Ejemplos ---
        examples_frame = ttk.LabelFrame(control_frame, text="Ejemplos", padding="5")
        examples_frame.pack(fill=tk.X)

        examples = [
            ("Bola lanzada", "20*t - 4.9*t**2"),
            ("Satélite", "7500*t - (1/16)*t**3"),
            ("Seno", "sin(t)"),
            ("Exponencial", "exp(-t)*cos(2*t)"),
        ]

        for name, func in examples:
            ttk.Button(
                examples_frame,
                text=name,
                command=lambda f=func: self._load_function(f)
            ).pack(fill=tk.X, pady=1)

    def _setup_graph_panel(self):
        """Configura el panel de gráficas."""
        graph_frame = ttk.Frame(self.main_frame)
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Crear figura de matplotlib
        self.fig = Figure(figsize=(8, 8), dpi=100)

        # Tres subplots: función, primera derivada, segunda derivada
        self.ax1 = self.fig.add_subplot(3, 1, 1)
        self.ax2 = self.fig.add_subplot(3, 1, 2)
        self.ax3 = self.fig.add_subplot(3, 1, 3)

        self.fig.tight_layout(pad=3.0)

        # Canvas de matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Toolbar de navegación
        toolbar = NavigationToolbar2Tk(self.canvas, graph_frame)
        toolbar.update()

        # Puntos animados
        self.point1, = self.ax1.plot([], [], 'ro', markersize=10, zorder=5)
        self.point2, = self.ax2.plot([], [], 'bo', markersize=10, zorder=5)
        self.point3, = self.ax3.plot([], [], 'go', markersize=10, zorder=5)

        # Líneas verticales
        self.vline1 = self.ax1.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        self.vline2 = self.ax2.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        self.vline3 = self.ax3.axvline(x=0, color='gray', linestyle='--', alpha=0.5)

    def _load_example(self):
        """Carga el ejemplo inicial."""
        self._load_function("20*t - 4.9*t**2")

    def _load_function(self, func_str: str):
        """Carga una función en el campo de entrada."""
        self.func_entry.delete(0, tk.END)
        self.func_entry.insert(0, func_str)
        self._on_function_change()

    def _on_function_change(self):
        """Maneja el cambio de función."""
        func_str = self.func_entry.get().strip()
        if not func_str:
            return

        # Actualizar variable
        var = self.var_combo.get()
        self.engine.set_variable(var)

        # Parsear función
        if not self.engine.parse_function(func_str):
            messagebox.showerror("Error", "No se pudo parsear la función. Verifica la sintaxis.")
            return

        # Mostrar derivadas
        self.deriv1_label.config(text=self.engine.get_first_derivative_string())
        self.deriv2_label.config(text=self.engine.get_second_derivative_string())

        # Actualizar sliders de constantes
        self._update_constant_sliders()

        # Actualizar gráficas
        self._update_graphs()

        # Resetear animación
        self._reset_animation()

    def _update_constant_sliders(self):
        """Actualiza los sliders de constantes."""
        # Limpiar sliders existentes
        for widget in self.constants_frame.winfo_children():
            widget.destroy()
        self.constant_sliders.clear()
        self.constant_labels.clear()

        # Crear nuevos sliders
        constants = self.engine.get_constants()

        if not constants:
            ttk.Label(self.constants_frame, text="(sin constantes)").pack()
            return

        for const_name in constants:
            frame = ttk.Frame(self.constants_frame)
            frame.pack(fill=tk.X, pady=2)

            value = self.engine.get_constant(const_name)

            label = ttk.Label(frame, text=f"{const_name} = {value:.2f}", width=12)
            label.pack(side=tk.LEFT)
            self.constant_labels[const_name] = label

            slider = ttk.Scale(
                frame,
                from_=-10,
                to=10,
                orient=tk.HORIZONTAL,
                command=lambda v, n=const_name: self._on_constant_change(n, float(v))
            )
            slider.set(value)
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            self.constant_sliders[const_name] = slider

    def _on_constant_change(self, name: str, value: float):
        """Maneja el cambio de una constante."""
        self.engine.set_constant(name, value)
        self.constant_labels[name].config(text=f"{name} = {value:.2f}")
        self._update_graphs()

    def _update_range(self):
        """Actualiza el rango de tiempo."""
        try:
            self.t_min = float(self.t_min_entry.get())
            self.t_max = float(self.t_max_entry.get())
            if self.t_min >= self.t_max:
                messagebox.showerror("Error", "t mín debe ser menor que t máx")
                return
            self._update_graphs()
            self._reset_animation()
        except ValueError:
            messagebox.showerror("Error", "Valores de rango inválidos")

    def _update_graphs(self):
        """Actualiza las gráficas."""
        # Generar puntos
        t = np.linspace(self.t_min, self.t_max, 500)

        # Obtener funciones
        try:
            f = self.engine.get_callable_function()
            f_prime = self.engine.get_callable_first_derivative()
            f_double_prime = self.engine.get_callable_second_derivative()

            y1 = f(t)
            y2 = f_prime(t)
            y3 = f_double_prime(t)
        except Exception as e:
            print(f"Error evaluando funciones: {e}")
            return

        var = self.var_combo.get()

        # Limpiar y redibujar ax1 (función)
        self.ax1.clear()
        self.ax1.plot(t, y1, 'r-', linewidth=2, label=f'f({var})')
        self.ax1.set_xlabel(var)
        self.ax1.set_ylabel(f'f({var})')
        self.ax1.set_title(f'Función: f({var}) = {self.engine.get_function_string()}')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.legend()
        self.point1, = self.ax1.plot([], [], 'ro', markersize=10, zorder=5)
        self.vline1 = self.ax1.axvline(x=self.current_t, color='gray', linestyle='--', alpha=0.5)

        # Limpiar y redibujar ax2 (primera derivada)
        self.ax2.clear()
        self.ax2.plot(t, y2, 'b-', linewidth=2, label=f"f'({var})")
        self.ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        self.ax2.set_xlabel(var)
        self.ax2.set_ylabel(f"f'({var})")
        self.ax2.set_title(f"Primera Derivada: f'({var}) = {self.engine.get_first_derivative_string()}")
        self.ax2.grid(True, alpha=0.3)
        self.ax2.legend()
        self.point2, = self.ax2.plot([], [], 'bo', markersize=10, zorder=5)
        self.vline2 = self.ax2.axvline(x=self.current_t, color='gray', linestyle='--', alpha=0.5)

        # Limpiar y redibujar ax3 (segunda derivada)
        self.ax3.clear()
        self.ax3.plot(t, y3, 'g-', linewidth=2, label=f"f''({var})")
        self.ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        self.ax3.set_xlabel(var)
        self.ax3.set_ylabel(f"f''({var})")
        self.ax3.set_title(f"Segunda Derivada: f''({var}) = {self.engine.get_second_derivative_string()}")
        self.ax3.grid(True, alpha=0.3)
        self.ax3.legend()
        self.point3, = self.ax3.plot([], [], 'go', markersize=10, zorder=5)
        self.vline3 = self.ax3.axvline(x=self.current_t, color='gray', linestyle='--', alpha=0.5)

        # Marcar puntos críticos
        critical_points = self.engine.find_critical_points(self.t_min, self.t_max)
        for t_crit, point_type in critical_points:
            y_crit = self.engine.evaluate_function(t_crit)
            marker = '^' if point_type == 'max' else 'v' if point_type == 'min' else 's'
            color = 'gold' if point_type == 'max' else 'purple' if point_type == 'min' else 'orange'
            self.ax1.plot(t_crit, y_crit, marker, color=color, markersize=12,
                         label=f'{point_type} ({t_crit:.2f}, {y_crit:.2f})')
            self.ax1.legend()

        self.fig.tight_layout(pad=3.0)
        self.canvas.draw()

    def _toggle_animation(self):
        """Alterna entre play y pause."""
        if self.is_playing:
            self._pause_animation()
        else:
            self._start_animation()

    def _start_animation(self):
        """Inicia la animación."""
        self.is_playing = True
        self.play_btn.config(text="⏸ Pause")
        self._animate()

    def _pause_animation(self):
        """Pausa la animación."""
        self.is_playing = False
        self.play_btn.config(text="▶ Play")

    def _reset_animation(self):
        """Resetea la animación al inicio."""
        self.is_playing = False
        self.play_btn.config(text="▶ Play")
        self.current_t = self.t_min
        self._update_animation_point()

    def _animate(self):
        """Función de animación."""
        if not self.is_playing:
            return

        # Avanzar tiempo
        dt = (self.t_max - self.t_min) / 100
        self.current_t += dt

        # Verificar si llegamos al final
        if self.current_t > self.t_max:
            self.current_t = self.t_min

        # Actualizar punto
        self._update_animation_point()

        # Programar siguiente frame
        self.root.after(self.animation_speed, self._animate)

    def _update_animation_point(self):
        """Actualiza la posición del punto animado."""
        t = self.current_t

        # Evaluar funciones
        y1 = self.engine.evaluate_function(t)
        y2 = self.engine.evaluate_first_derivative(t)
        y3 = self.engine.evaluate_second_derivative(t)

        # Actualizar puntos
        self.point1.set_data([t], [y1])
        self.point2.set_data([t], [y2])
        self.point3.set_data([t], [y3])

        # Actualizar líneas verticales
        self.vline1.set_xdata([t, t])
        self.vline2.set_xdata([t, t])
        self.vline3.set_xdata([t, t])

        # Actualizar etiquetas
        var = self.var_combo.get()
        self.t_value_label.config(text=f"{var} = {t:.2f}")
        self.f_value_label.config(text=f"f({var}) = {y1:.2f}")
        self.v_value_label.config(text=f"f'({var}) = {y2:.2f}")
        self.a_value_label.config(text=f"f''({var}) = {y3:.2f}")

        # Redibujar
        self.canvas.draw_idle()

    def _on_speed_change(self, value):
        """Maneja el cambio de velocidad de animación."""
        # Invertir: mayor valor = más rápido = menor intervalo
        self.animation_speed = int(210 - float(value))
