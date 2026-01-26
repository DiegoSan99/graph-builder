"""
Calculadora de Derivadas con Animación - Streamlit App

Aplicación web para resolver derivadas simbólicamente,
graficar funciones y visualizar su comportamiento mediante animaciones.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from typing import Dict, List, Tuple, Callable
import base64
from pathlib import Path

# Configuración de página
st.set_page_config(
    page_title="Calculadora de Derivadas",
    page_icon="📈",
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
    [data-testid="stMetric"] {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #4a4a5a;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #fafafa !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #00d4aa !important;
    }
    /* Ocultar ícono de link en toolbar */
    [data-testid="stToolbar"] {
        display: none !important;
    }
    /* Ocultar anclas de encabezados */
    .stMainBlockContainer [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)


class DerivativeEngine:
    """Motor para calcular derivadas simbólicas."""

    def __init__(self):
        self.transformations = standard_transformations + (implicit_multiplication_application,)
        self.function_expr = None
        self.first_derivative = None
        self.second_derivative = None
        self.variable = sp.Symbol('t')
        self.constants: Dict[str, float] = {}
        self.constant_symbols: Dict[str, sp.Symbol] = {}

    def set_variable(self, var_name: str):
        self.variable = sp.Symbol(var_name)

    def parse_function(self, func_str: str) -> bool:
        try:
            func_str = func_str.replace('^', '**')
            local_dict = {self.variable.name: self.variable}
            self.function_expr = parse_expr(
                func_str,
                local_dict=local_dict,
                transformations=self.transformations
            )
            self._extract_constants()
            self.first_derivative = sp.diff(self.function_expr, self.variable)
            self.second_derivative = sp.diff(self.first_derivative, self.variable)
            return True
        except Exception as e:
            st.error(f"Error al parsear la función: {e}")
            return False

    def _extract_constants(self):
        if self.function_expr is None:
            return
        all_symbols = self.function_expr.free_symbols
        constant_symbols = [s for s in all_symbols if s != self.variable]
        self.constant_symbols = {str(s): s for s in constant_symbols}
        for name in self.constant_symbols:
            if name not in self.constants:
                self.constants[name] = 1.0

    def get_constants(self) -> List[str]:
        return list(self.constant_symbols.keys())

    def set_constant(self, name: str, value: float):
        self.constants[name] = value

    def _substitute_constants(self, expr):
        substitutions = {
            self.constant_symbols[name]: value
            for name, value in self.constants.items()
            if name in self.constant_symbols
        }
        return expr.subs(substitutions)

    def get_function_string(self) -> str:
        return str(self.function_expr) if self.function_expr else ""

    def get_first_derivative_string(self) -> str:
        return str(self.first_derivative) if self.first_derivative else ""

    def get_second_derivative_string(self) -> str:
        return str(self.second_derivative) if self.second_derivative else ""

    def evaluate(self, t_values):
        """Evalúa función y derivadas para un array de valores."""
        if self.function_expr is None:
            return None, None, None

        try:
            f_expr = self._substitute_constants(self.function_expr)
            f1_expr = self._substitute_constants(self.first_derivative)
            f2_expr = self._substitute_constants(self.second_derivative)

            f = sp.lambdify(self.variable, f_expr, modules=['numpy'])
            f1 = sp.lambdify(self.variable, f1_expr, modules=['numpy'])
            f2 = sp.lambdify(self.variable, f2_expr, modules=['numpy'])

            y = f(t_values)
            y1 = f1(t_values)
            y2 = f2(t_values)

            # Convertir escalares a arrays si la derivada es constante
            if np.isscalar(y):
                y = np.full_like(t_values, y)
            if np.isscalar(y1):
                y1 = np.full_like(t_values, y1)
            if np.isscalar(y2):
                y2 = np.full_like(t_values, y2)

            return y, y1, y2
        except:
            return None, None, None

    def evaluate_at_point(self, t: float) -> Tuple[float, float, float]:
        """Evalúa en un punto específico."""
        try:
            f_expr = self._substitute_constants(self.function_expr)
            f1_expr = self._substitute_constants(self.first_derivative)
            f2_expr = self._substitute_constants(self.second_derivative)

            y = float(f_expr.subs(self.variable, t))
            y1 = float(f1_expr.subs(self.variable, t))
            y2 = float(f2_expr.subs(self.variable, t))
            return y, y1, y2
        except:
            return 0, 0, 0

    def find_critical_points(self, t_min: float, t_max: float) -> List[Tuple[float, float, str]]:
        """Encuentra puntos críticos."""
        if self.first_derivative is None:
            return []
        try:
            expr = self._substitute_constants(self.first_derivative)
            solutions = sp.solve(expr, self.variable)
            points = []
            for sol in solutions:
                try:
                    t_val = float(sol)
                    if t_min <= t_val <= t_max:
                        f_expr = self._substitute_constants(self.function_expr)
                        f2_expr = self._substitute_constants(self.second_derivative)
                        y_val = float(f_expr.subs(self.variable, t_val))
                        second_val = float(f2_expr.subs(self.variable, t_val))
                        if second_val < 0:
                            point_type = 'Máximo'
                        elif second_val > 0:
                            point_type = 'Mínimo'
                        else:
                            point_type = 'Inflexión'
                        points.append((t_val, y_val, point_type))
                except:
                    pass
            return points
        except:
            return []


def create_ball_simulation(height: float, max_height: float, velocity: float) -> go.Figure:
    """Crea la simulación visual de la bola."""
    fig = go.Figure()

    # Calcular posición normalizada (0 a 1)
    h_display = max(0, height)  # No mostrar bajo el suelo

    # Fondo - cielo azul brillante
    fig.add_shape(
        type="rect", x0=-2, y0=0, x1=2, y1=max_height + 5,
        fillcolor="#87CEEB", line_color="#87CEEB", layer="below"
    )

    # Suelo - pasto verde brillante
    fig.add_shape(
        type="rect", x0=-2, y0=-2, x1=2, y1=0,
        fillcolor="#228B22", line_color="#228B22", layer="below"
    )

    # Sol
    fig.add_trace(go.Scatter(
        x=[1.5], y=[max_height + 3],
        mode='markers',
        marker=dict(size=50, color='#FFD700', line=dict(color='#FFA500', width=3)),
        showlegend=False, hoverinfo='skip'
    ))

    # Rinoceronte (imagen PNG)
    rhino_path = Path(__file__).parent / "assets" / "rhino.png"
    if rhino_path.exists():
        with open(rhino_path, "rb") as f:
            rhino_base64 = base64.b64encode(f.read()).decode()
        fig.add_layout_image(
            dict(
                source=f"data:image/png;base64,{rhino_base64}",
                x=-1.9, y=7,
                xref="x", yref="y",
                sizex=5, sizey=7,
                xanchor="left", yanchor="top",
                layer="above"
            )
        )

    # La bola
    ball_color = '#FF4444' if velocity >= 0 else '#FF8C00'  # Rojo subiendo, naranja bajando
    fig.add_trace(go.Scatter(
        x=[0], y=[h_display],
        mode='markers+text',
        marker=dict(size=35, color=ball_color, line=dict(color='#8B0000', width=3)),
        text=[f'{h_display:.1f}m'],
        textposition='top center',
        textfont=dict(size=16, color='white', family='Arial Black'),
        showlegend=False,
        hovertemplate=f'Altura: {h_display:.2f}m<br>Velocidad: {velocity:.2f}m/s<extra></extra>'
    ))

    # Flecha de velocidad
    if abs(velocity) > 0.5:
        arrow_scale = velocity / 20 * 4  # Escalar flecha
        fig.add_annotation(
            x=0, y=h_display,
            ax=0, ay=h_display - arrow_scale,
            xref='x', yref='y', axref='x', ayref='y',
            showarrow=True,
            arrowhead=2, arrowsize=2, arrowwidth=4,
            arrowcolor='#00BFFF' if velocity > 0 else '#9932CC'
        )

    # Línea de altura máxima
    fig.add_hline(y=max_height, line_dash="dash", line_color="#FFD700", line_width=2,
                  annotation_text=f"🎯 Altura máx: {max_height:.1f}m",
                  annotation_font=dict(color="white", size=12))

    # Trayectoria fantasma (línea punteada vertical)
    fig.add_trace(go.Scatter(
        x=[0, 0], y=[0, max_height],
        mode='lines', line=dict(color='rgba(255,255,255,0.4)', width=2, dash='dot'),
        showlegend=False, hoverinfo='skip'
    ))

    fig.update_layout(
        xaxis=dict(range=[-2, 2], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(range=[-2, max_height + 6], showgrid=False, zeroline=False,
                   tickfont=dict(color='white')),
        height=500,
        margin=dict(l=30, r=20, t=30, b=20),
        plot_bgcolor='#1a1a2e',
        paper_bgcolor='#1a1a2e',
    )

    return fig


def create_plots(engine: DerivativeEngine, t_min: float, t_max: float,
                 current_t: float, var_name: str) -> go.Figure:
    """Crea las gráficas con Plotly."""
    t = np.linspace(t_min, t_max, 500)
    y, y1, y2 = engine.evaluate(t)

    if y is None:
        return None

    # Valores actuales
    y_curr, y1_curr, y2_curr = engine.evaluate_at_point(current_t)

    # Crear subplots - 2 filas ahora
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            f"Altura: h({var_name}) = {engine.get_function_string()}",
            f"Velocidad: v({var_name}) = {engine.get_first_derivative_string()}"
        ),
        vertical_spacing=0.15
    )

    # Gráfica de función
    fig.add_trace(
        go.Scatter(x=t, y=y, mode='lines', name=f'f({var_name})',
                   line=dict(color='red', width=2)),
        row=1, col=1
    )

    # Punto animado en función
    fig.add_trace(
        go.Scatter(x=[current_t], y=[y_curr], mode='markers',
                   name='Posición actual', marker=dict(color='red', size=12),
                   showlegend=False),
        row=1, col=1
    )

    # Línea vertical
    fig.add_vline(x=current_t, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=1)

    # Puntos críticos
    critical = engine.find_critical_points(t_min, t_max)
    for t_crit, y_crit, ptype in critical:
        color = 'gold' if ptype == 'Máximo' else 'purple' if ptype == 'Mínimo' else 'orange'
        symbol = 'triangle-up' if ptype == 'Máximo' else 'triangle-down' if ptype == 'Mínimo' else 'square'
        fig.add_trace(
            go.Scatter(x=[t_crit], y=[y_crit], mode='markers+text',
                       name=f'{ptype} ({t_crit:.2f})',
                       marker=dict(color=color, size=14, symbol=symbol),
                       text=[ptype], textposition='top center'),
            row=1, col=1
        )

    # Gráfica de primera derivada (velocidad)
    fig.add_trace(
        go.Scatter(x=t, y=y1, mode='lines', name=f"v({var_name})",
                   line=dict(color='blue', width=2)),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=[current_t], y=[y1_curr], mode='markers',
                   marker=dict(color='blue', size=12), showlegend=False),
        row=2, col=1
    )
    fig.add_hline(y=0, line_color="red", line_width=1, line_dash="dash", row=2, col=1,
                  annotation_text="v=0 (altura máxima)", annotation_position="bottom right")
    fig.add_vline(x=current_t, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)

    # Configurar layout
    fig.update_layout(
        height=450,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_xaxes(title_text=f"Tiempo ({var_name}) [s]", row=2, col=1)
    fig.update_yaxes(title_text="Altura [m]", row=1, col=1)
    fig.update_yaxes(title_text="Velocidad [m/s]", row=2, col=1)

    return fig


def main():
    st.title("📈 Calculadora de Derivadas con Animación")

    # Inicializar estado
    if 'engine' not in st.session_state:
        st.session_state.engine = DerivativeEngine()
    if 'current_t' not in st.session_state:
        st.session_state.current_t = 0.0

    engine = st.session_state.engine

    # Sidebar con controles
    with st.sidebar:
        st.header("⚙️ Controles")

        # Entrada de función
        st.subheader("Función")

        # Función fija: Bola lanzada
        default_func = "20*t - 4.9*t**2"

        func_str = st.text_input("h(t) =", value=default_func,
                                  help="Altura en función del tiempo")

        var_name = 't'  # Variable fija para el problema de la bola

        # Rango
        st.subheader("Rango")
        col1, col2 = st.columns(2)
        with col1:
            t_min = st.number_input("Mínimo", value=0.0, step=0.5)
        with col2:
            t_max = st.number_input("Máximo", value=5.0, step=0.5)

        # Procesar función
        engine.set_variable(var_name)
        if engine.parse_function(func_str):
            st.session_state.last_func = func_str

            # Mostrar derivadas
            st.subheader("📐 Derivadas")
            st.markdown(f"**f'({var_name})** = `{engine.get_first_derivative_string()}`")
            st.markdown(f"**f''({var_name})** = `{engine.get_second_derivative_string()}`")

            # Sliders para constantes
            constants = engine.get_constants()
            if constants:
                st.subheader("🎚️ Constantes")
                for const in constants:
                    val = st.slider(
                        f"{const}",
                        min_value=-10.0,
                        max_value=10.0,
                        value=engine.constants.get(const, 1.0),
                        step=0.1
                    )
                    engine.set_constant(const, val)

        # Control de tiempo
        st.subheader("🕐 Tiempo")

        # Input numérico
        time_input = st.number_input(
            "Valor de t",
            min_value=float(t_min),
            max_value=float(t_max),
            value=float(st.session_state.current_t),
            step=0.1,
            format="%.2f"
        )

        # Slider
        time_slider = st.slider(
            "Ajustar tiempo",
            min_value=float(t_min),
            max_value=float(t_max),
            value=float(time_input),
            step=(t_max - t_min) / 100,
            label_visibility="collapsed"
        )

        # Sincronizar: usar el valor que cambió más recientemente
        if abs(time_input - st.session_state.current_t) > 0.001:
            current_t = time_input
        else:
            current_t = time_slider
        st.session_state.current_t = current_t

    # Contenido principal
    if engine.function_expr is not None:
        # Valores actuales
        y_curr, y1_curr, y2_curr = engine.evaluate_at_point(current_t)

        # Calcular altura máxima para la simulación
        critical = engine.find_critical_points(t_min, t_max)
        max_height = 25  # Default
        for t_crit, y_crit, ptype in critical:
            if ptype == 'Máximo':
                max_height = max(y_crit + 5, 10)

        # Métricas en la parte superior
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("⏱️ Tiempo", f"{current_t:.2f} s")
        with col2:
            st.metric("📏 Altura", f"{y_curr:.2f} m")
        with col3:
            direction = "↑" if y1_curr > 0 else "↓" if y1_curr < 0 else "•"
            st.metric(f"🚀 Velocidad {direction}", f"{y1_curr:.2f} m/s")
        with col4:
            st.metric("📉 Aceleración", f"{y2_curr:.2f} m/s²")

        # Layout: Simulación a la izquierda, gráficas a la derecha
        sim_col, graph_col = st.columns([1, 2])

        with sim_col:
            st.subheader("🎯 Simulación")
            # Crear simulación de la bola
            ball_fig = create_ball_simulation(y_curr, max_height, y1_curr)
            st.plotly_chart(ball_fig, use_container_width=True)

            # Estado de la bola
            if y_curr <= 0 and current_t > 0:
                st.error("💥 ¡La bola tocó el suelo!")
            elif y1_curr > 0:
                st.success("⬆️ Subiendo...")
            elif y1_curr < 0:
                st.warning("⬇️ Bajando...")
            else:
                st.info("🎯 ¡Punto máximo alcanzado!")

        with graph_col:
            st.subheader("📊 Gráficas")
            # Gráficas
            fig = create_plots(engine, t_min, t_max, current_t, var_name)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Ingresa una función válida en el panel izquierdo.")


if __name__ == "__main__":
    main()
