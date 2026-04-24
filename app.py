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
    page_title="Simulador Matemático para el Aprendizaje Significativo de Problemas de Optimización",
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

    /* Estilos para pantalla de introducción */
    .intro-container {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 20px;
        padding: 40px;
        margin: 20px 0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .intro-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d4aa, #00b4d8, #90e0ef);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 30px;
        text-transform: uppercase;
        letter-spacing: 3px;
    }

    .intro-content {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 30px;
        border-left: 4px solid #00d4aa;
        margin: 20px 0;
    }

    .intro-content p {
        color: #e0e0e0;
        font-size: 1.1rem;
        line-height: 1.8;
        text-align: justify;
        margin-bottom: 15px;
    }

    .intro-icon {
        text-align: center;
        font-size: 4rem;
        margin-bottom: 20px;
    }

    .intro-features {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 30px;
        flex-wrap: wrap;
    }

    .feature-card {
        background: rgba(0, 212, 170, 0.1);
        border: 1px solid rgba(0, 212, 170, 0.3);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        min-width: 150px;
        transition: transform 0.3s ease;
    }

    .feature-card:hover {
        transform: translateY(-5px);
    }

    .feature-icon {
        font-size: 2rem;
        margin-bottom: 10px;
    }

    .feature-text {
        color: #00d4aa;
        font-weight: 600;
    }

    /* Estilos para calculadora */
    .calc-container {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 8px;
        margin: 8px 0;
        border: 1px solid #3a3a4a;
    }

    .calc-display {
        background: #0d0d15;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 8px;
        font-family: 'Consolas', monospace;
        font-size: 0.95rem;
        color: #00d4aa;
        border: 1px solid #2a2a3a;
        word-wrap: break-word;
        overflow-x: auto;
    }

    /* Botones de calculadora más compactos */
    .stSidebar button {
        padding: 0.3rem 0.2rem !important;
        font-size: 0.8rem !important;
        min-height: 2.2rem !important;
    }

    .stSidebar [data-testid="column"] {
        padding: 0 2px !important;
    }

    /* Incisos */
    .inciso-header {
        background: linear-gradient(90deg, rgba(0, 212, 170, 0.15), rgba(0, 180, 216, 0.05));
        border-left: 4px solid #00d4aa;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 10px 0 5px 0;
        font-size: 1.05rem;
        color: #00d4aa;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def show_intro_screen():
    """Muestra la pantalla de introducción sobre optimización."""
    # Título centrado con estilo
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <span style="font-size: 4rem;">📐</span>
        </div>
        <h1 style="text-align: center; font-size: 2.5rem; font-weight: 700;
                   background: linear-gradient(90deg, #00d4aa, #00b4d8, #90e0ef);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   background-clip: text; text-transform: uppercase; letter-spacing: 3px;
                   margin-bottom: 30px;">
            Optimización
        </h1>
    """, unsafe_allow_html=True)

    # Contenido en un container
    with st.container():
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 15px;
                    padding: 30px; border-left: 4px solid #00d4aa; margin: 20px auto; max-width: 800px;">
            <p style="color: #e0e0e0; font-size: 1.1rem; line-height: 1.8; text-align: justify; margin-bottom: 15px;">
                Un <strong style="color: #00d4aa;">problema de optimización</strong> consiste en minimizar o maximizar el valor de una variable.
                En otras palabras, se trata de calcular o determinar el <strong style="color: #00d4aa;">valor mínimo</strong> o el
                <strong style="color: #00d4aa;">valor máximo</strong> de una función de una variable.
            </p>
            <p style="color: #e0e0e0; font-size: 1.1rem; line-height: 1.8; text-align: justify; margin-bottom: 15px;">
                Se debe tener presente que la variable que se desea minimizar o maximizar debe ser expresada como
                <strong style="color: #00d4aa;">función de otra de las variables</strong> relacionadas en el problema.
            </p>
            <p style="color: #e0e0e0; font-size: 1.1rem; line-height: 1.8; text-align: justify; margin-bottom: 15px;">
                En ocasiones es preciso considerar las <strong style="color: #00d4aa;">restricciones</strong> que se tengan en el problema,
                ya que éstas generan igualdades entre las variables que permiten la obtención de la función de una
                variable que se quiere minimizar o maximizar.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Tarjetas de características usando columnas de Streamlit
    st.write("")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div style="background: rgba(0, 212, 170, 0.1); border: 1px solid rgba(0, 212, 170, 0.3);
                    border-radius: 12px; padding: 20px; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">📈</div>
            <div style="color: #00d4aa; font-weight: 600;">Máximos</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: rgba(0, 212, 170, 0.1); border: 1px solid rgba(0, 212, 170, 0.3);
                    border-radius: 12px; padding: 20px; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">📉</div>
            <div style="color: #00d4aa; font-weight: 600;">Mínimos</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: rgba(0, 212, 170, 0.1); border: 1px solid rgba(0, 212, 170, 0.3);
                    border-radius: 12px; padding: 20px; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">🔄</div>
            <div style="color: #00d4aa; font-weight: 600;">Derivadas</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div style="background: rgba(0, 212, 170, 0.1); border: 1px solid rgba(0, 212, 170, 0.3);
                    border-radius: 12px; padding: 20px; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 10px;">🎯</div>
            <div style="color: #00d4aa; font-weight: 600;">Puntos Críticos</div>
        </div>
        """, unsafe_allow_html=True)

    # Espacio y botón centrado
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Comenzar Simulación", use_container_width=True, type="primary"):
            st.session_state.show_intro = False
            st.rerun()


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
        if self.function_expr:
            return str(self.function_expr).replace('**', '^')
        return ""

    def get_first_derivative_string(self) -> str:
        if self.first_derivative:
            return str(self.first_derivative).replace('**', '^')
        return ""

    def get_second_derivative_string(self) -> str:
        if self.second_derivative:
            return str(self.second_derivative).replace('**', '^')
        return ""

    def get_function_latex(self) -> str:
        if self.function_expr is None:
            return ""
        return sp.latex(self.function_expr)

    def get_first_derivative_latex(self) -> str:
        if self.first_derivative is None:
            return ""
        return sp.latex(self.first_derivative)

    def get_second_derivative_latex(self) -> str:
        if self.second_derivative is None:
            return ""
        return sp.latex(self.second_derivative)

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

    def get_calculation_steps(self, t: float, var_name: str,
                              f_name: str = "h", pos_unit: str = "m",
                              vel_unit: str = "m/s",
                              acc_unit: str = "m/s²") -> dict:
        """Genera los pasos de cálculo con sustituciones."""
        steps = {}
        try:
            f_expr = self._substitute_constants(self.function_expr)
            f1_expr = self._substitute_constants(self.first_derivative)
            f2_expr = self._substitute_constants(self.second_derivative)

            f_str = str(f_expr).replace('**', '^')
            f_subs = str(f_expr.subs(self.variable, t)).replace('**', '^')
            f_result = float(f_expr.subs(self.variable, t))
            steps['funcion'] = {
                'formula': f"{f_name}({var_name}) = {f_str}",
                'sustitucion': f"{f_name}({t}) = {f_subs}",
                'resultado': f"{f_name}({t}) = {f_result:.4f} {pos_unit}"
            }

            f1_str = str(f1_expr).replace('**', '^')
            f1_subs = str(f1_expr.subs(self.variable, t)).replace('**', '^')
            f1_result = float(f1_expr.subs(self.variable, t))
            steps['velocidad'] = {
                'formula': f"v({var_name}) = {f_name}'({var_name}) = {f1_str}",
                'sustitucion': f"v({t}) = {f1_subs}",
                'resultado': f"v({t}) = {f1_result:.4f} {vel_unit}"
            }

            f2_str = str(f2_expr).replace('**', '^')
            f2_subs = str(f2_expr.subs(self.variable, t)).replace('**', '^')
            f2_result = float(f2_expr.subs(self.variable, t))
            steps['aceleracion'] = {
                'formula': f"a({var_name}) = {f_name}''({var_name}) = {f2_str}",
                'sustitucion': f"a({t}) = {f2_subs}",
                'resultado': f"a({t}) = {f2_result:.4f} {acc_unit}"
            }

        except Exception as e:
            pass
        return steps

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

    h_display = max(0, height)

    # Fondo - cielo
    fig.add_shape(
        type="rect", x0=-2, y0=0, x1=2, y1=max_height + 5,
        fillcolor="#87CEEB", line_color="#87CEEB", layer="below"
    )

    # Suelo
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

    # Rinoceronte
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
    ball_color = '#FF4444' if velocity >= 0 else '#FF8C00'
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
        arrow_scale = velocity / 20 * 4
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

    # Trayectoria fantasma
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


def create_satellite_simulation(distance: float, stop_distance: float, velocity: float,
                                initial_velocity: float = 7500) -> go.Figure:
    """Crea la simulación visual del satélite en reentrada."""
    fig = go.Figure()

    # Fondo: espacio arriba, atmósfera abajo
    fig.add_shape(type="rect", x0=0, y0=0.55, x1=1, y1=1,
                  fillcolor="#0a0a2a", line_color="#0a0a2a", layer="below")
    fig.add_shape(type="rect", x0=0, y0=0.2, x1=1, y1=0.55,
                  fillcolor="#3a2a5a", line_color="#3a2a5a", layer="below")
    fig.add_shape(type="rect", x0=0, y0=0, x1=1, y1=0.2,
                  fillcolor="#1a4a6a", line_color="#1a4a6a", layer="below")

    # Estrellas
    rng = np.random.default_rng(42)
    stars_x = rng.uniform(0, 1, 30)
    stars_y = rng.uniform(0.6, 0.98, 30)
    fig.add_trace(go.Scatter(
        x=stars_x, y=stars_y, mode='markers',
        marker=dict(size=3, color='white', opacity=0.7),
        showlegend=False, hoverinfo='skip'
    ))

    # Curva de la Tierra
    earth_x = np.linspace(0, 1, 100)
    earth_y = 0.1 + 0.04 * np.cos((earth_x - 0.5) * np.pi)
    fig.add_trace(go.Scatter(
        x=np.concatenate([earth_x, [1, 0]]),
        y=np.concatenate([earth_y, [0, 0]]),
        mode='lines',
        line=dict(color='#2a5a2a', width=0),
        fill='toself', fillcolor='#2a7a3a',
        showlegend=False, hoverinfo='skip'
    ))

    # Trayectoria
    traj_x = np.linspace(0.08, 0.92, 50)
    traj_y = 0.88 - 0.7 * ((traj_x - 0.08) / 0.84)
    fig.add_trace(go.Scatter(
        x=traj_x, y=traj_y, mode='lines',
        line=dict(color='rgba(255,255,255,0.3)', width=2, dash='dot'),
        showlegend=False, hoverinfo='skip'
    ))

    # Posición del satélite (0 a 1)
    if stop_distance > 0:
        progress = float(np.clip(distance / stop_distance, 0.0, 1.0))
    else:
        progress = 0.0
    sat_x = 0.08 + 0.84 * progress
    sat_y = 0.88 - 0.7 * progress

    # Estela de reentrada
    if velocity > 100:
        intensity = min(velocity / 7500, 1.0)
        for i in range(6):
            frac = i / 6
            fig.add_trace(go.Scatter(
                x=[sat_x - 0.04 * (i + 1)], y=[sat_y + 0.03 * (i + 1)],
                mode='markers',
                marker=dict(
                    size=30 - i * 4,
                    color=['#FFFF66', '#FFA500', '#FF4500', '#CC3300', '#881100', '#440000'][i],
                    opacity=(1 - frac) * intensity
                ),
                showlegend=False, hoverinfo='skip'
            ))

    # Satélite
    fig.add_trace(go.Scatter(
        x=[sat_x], y=[sat_y], mode='markers+text',
        marker=dict(size=45, color='#e0e0e0', line=dict(color='#707080', width=3),
                    symbol='diamond'),
        text=['🛰️'], textposition='middle center',
        textfont=dict(size=22),
        showlegend=False,
        hovertemplate=(f'Distancia: {distance:,.0f} m<br>'
                       f'Velocidad: {velocity:,.2f} m/s<extra></extra>')
    ))

    # Flecha de velocidad
    if abs(velocity) > 50:
        arrow_len = min(abs(velocity) / max(initial_velocity, 1), 1.0) * 0.12
        sign = 1 if velocity > 0 else -1
        fig.add_annotation(
            x=sat_x + arrow_len * sign, y=sat_y - arrow_len * sign * 0.83,
            ax=sat_x, ay=sat_y,
            xref='x', yref='y', axref='x', ayref='y',
            showarrow=True, arrowhead=3, arrowsize=2, arrowwidth=3,
            arrowcolor='#00BFFF' if velocity > 0 else '#FF00FF'
        )

    # Línea de punto de parada
    stop_x = 0.92
    stop_y = 0.88 - 0.7 * 1.0
    fig.add_trace(go.Scatter(
        x=[stop_x], y=[stop_y], mode='markers+text',
        marker=dict(size=18, color='#00ff88', symbol='x',
                    line=dict(color='#00aa55', width=3)),
        text=['🎯 Parada'], textposition='bottom center',
        textfont=dict(size=11, color='#00ff88'),
        showlegend=False, hoverinfo='skip'
    ))

    # Etiquetas
    fig.add_annotation(
        x=0.5, y=0.96, xref='x', yref='y',
        text=f"<b>🛰️ REENTRADA ATMOSFÉRICA</b>",
        showarrow=False, font=dict(size=13, color='white'),
        bgcolor='rgba(0,0,0,0.5)', bordercolor='white', borderwidth=1
    )
    fig.add_annotation(
        x=0.05, y=0.05, xref='x', yref='y',
        text="🌍", showarrow=False, font=dict(size=30)
    )

    fig.update_layout(
        xaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, zeroline=False),
        height=500,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='#0a0a2a',
        paper_bgcolor='#0a0a2a',
    )

    return fig


def create_plots(engine: DerivativeEngine, t_min: float, t_max: float,
                 current_t: float, var_name: str,
                 pos_fn_label: str = "h", pos_label: str = "Altura", pos_unit: str = "m",
                 vel_label: str = "Velocidad", vel_unit: str = "m/s") -> go.Figure:
    """Crea las gráficas con Plotly."""
    t = np.linspace(t_min, t_max, 500)
    y, y1, y2 = engine.evaluate(t)

    if y is None:
        return None

    y_curr, y1_curr, y2_curr = engine.evaluate_at_point(current_t)

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            f"{pos_label}: {pos_fn_label}({var_name}) = {engine.get_function_string()}",
            f"{vel_label}: v({var_name}) = {engine.get_first_derivative_string()}"
        ),
        vertical_spacing=0.15
    )

    # Gráfica de función
    fig.add_trace(
        go.Scatter(x=t, y=y, mode='lines', name=f'{pos_fn_label}({var_name})',
                   line=dict(color='red', width=2)),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=[current_t], y=[y_curr], mode='markers',
                   name='Posición actual', marker=dict(color='red', size=12),
                   showlegend=False),
        row=1, col=1
    )

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

    # Velocidad
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
                  annotation_text="v=0", annotation_position="bottom right")
    fig.add_vline(x=current_t, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)

    fig.update_layout(
        height=450,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_xaxes(title_text=f"Tiempo ({var_name}) [s]", row=2, col=1)
    fig.update_yaxes(title_text=f"{pos_label} [{pos_unit}]", row=1, col=1)
    fig.update_yaxes(title_text=f"{vel_label} [{vel_unit}]", row=2, col=1)

    return fig


def render_calculator(state_key: str, key_suffix: str):
    """Renderiza los botones de calculadora que actualizan st.session_state[state_key]."""
    if state_key not in st.session_state:
        st.session_state[state_key] = ""

    def append(s):
        st.session_state[state_key] += s

    # Fila 1: Números 7-9
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("7", use_container_width=True, key=f"k7_{key_suffix}"):
            append("7"); st.rerun()
    with c2:
        if st.button("8", use_container_width=True, key=f"k8_{key_suffix}"):
            append("8"); st.rerun()
    with c3:
        if st.button("9", use_container_width=True, key=f"k9_{key_suffix}"):
            append("9"); st.rerun()

    # Fila 2: 4-6
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("4", use_container_width=True, key=f"k4_{key_suffix}"):
            append("4"); st.rerun()
    with c2:
        if st.button("5", use_container_width=True, key=f"k5_{key_suffix}"):
            append("5"); st.rerun()
    with c3:
        if st.button("6", use_container_width=True, key=f"k6_{key_suffix}"):
            append("6"); st.rerun()

    # Fila 3: 1-3
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("1", use_container_width=True, key=f"k1_{key_suffix}"):
            append("1"); st.rerun()
    with c2:
        if st.button("2", use_container_width=True, key=f"k2_{key_suffix}"):
            append("2"); st.rerun()
    with c3:
        if st.button("3", use_container_width=True, key=f"k3_{key_suffix}"):
            append("3"); st.rerun()

    # Fila 4: 0, punto, t
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("0", use_container_width=True, key=f"k0_{key_suffix}"):
            append("0"); st.rerun()
    with c2:
        if st.button(".", use_container_width=True, key=f"kdot_{key_suffix}"):
            append("."); st.rerun()
    with c3:
        if st.button("t", use_container_width=True, type="primary", key=f"kt_{key_suffix}"):
            append("t"); st.rerun()

    # Fila 5: operadores
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("+", use_container_width=True, key=f"kplus_{key_suffix}"):
            append("+"); st.rerun()
    with c2:
        if st.button("−", use_container_width=True, key=f"kminus_{key_suffix}"):
            append("-"); st.rerun()
    with c3:
        if st.button("×", use_container_width=True, key=f"kmult_{key_suffix}"):
            append("*"); st.rerun()

    # Fila 6
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("÷", use_container_width=True, key=f"kdiv_{key_suffix}"):
            append("/"); st.rerun()
    with c2:
        if st.button("^", use_container_width=True, key=f"kpow_{key_suffix}"):
            append("^"); st.rerun()
    with c3:
        if st.button("√", use_container_width=True, key=f"ksqrt_{key_suffix}"):
            append("sqrt("); st.rerun()

    # Fila 7
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("(", use_container_width=True, key=f"klp_{key_suffix}"):
            append("("); st.rerun()
    with c2:
        if st.button(")", use_container_width=True, key=f"krp_{key_suffix}"):
            append(")"); st.rerun()
    with c3:
        if st.button("⌫", use_container_width=True, key=f"kdel_{key_suffix}"):
            st.session_state[state_key] = st.session_state[state_key][:-1]
            st.rerun()

    # Fila 8
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("sin", use_container_width=True, key=f"ksin_{key_suffix}"):
            append("sin("); st.rerun()
    with c2:
        if st.button("cos", use_container_width=True, key=f"kcos_{key_suffix}"):
            append("cos("); st.rerun()
    with c3:
        if st.button("C", use_container_width=True, key=f"kclear_{key_suffix}"):
            st.session_state[state_key] = ""
            st.rerun()


def render_substitution_section(engine: DerivativeEngine, current_t: float, var_name: str,
                                f_name: str, pos_unit: str, vel_unit: str, acc_unit: str,
                                pos_label: str = "Altura"):
    """Renderiza la sección de cálculos con sustituciones."""
    calc_steps = engine.get_calculation_steps(
        current_t, var_name, f_name=f_name, pos_unit=pos_unit,
        vel_unit=vel_unit, acc_unit=acc_unit
    )
    if not calc_steps:
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**{pos_label} {f_name}({var_name})**")
        if 'funcion' in calc_steps:
            st.code(calc_steps['funcion']['formula'], language=None)
            st.markdown(f"Sustituyendo {var_name} = {current_t}:")
            st.code(calc_steps['funcion']['sustitucion'], language=None)
            st.success(calc_steps['funcion']['resultado'])

    with col2:
        st.markdown(f"**Velocidad v({var_name}) = {f_name}'({var_name})**")
        if 'velocidad' in calc_steps:
            st.code(calc_steps['velocidad']['formula'], language=None)
            st.markdown(f"Sustituyendo {var_name} = {current_t}:")
            st.code(calc_steps['velocidad']['sustitucion'], language=None)
            st.success(calc_steps['velocidad']['resultado'])

    with col3:
        st.markdown(f"**Aceleración a({var_name}) = {f_name}''({var_name})**")
        if 'aceleracion' in calc_steps:
            st.code(calc_steps['aceleracion']['formula'], language=None)
            st.markdown(f"Sustituyendo {var_name} = {current_t}:")
            st.code(calc_steps['aceleracion']['sustitucion'], language=None)
            st.success(calc_steps['aceleracion']['resultado'])


# ====================== SOLUCIONES POR INCISO ======================

def render_problem1_solutions():
    """Muestra la resolución paso a paso de los incisos del Problema 1."""
    st.caption("La solución que se muestra corresponde al enunciado original "
               "$h(t) = 20t - 4.9t^2$. Puedes modificar la función arriba para explorar "
               "variantes; los valores de arriba sí responden a tu función editada.")
    st.markdown("**Datos:** $h(t) = 20t - 4.9t^2$ (altura en metros, tiempo en segundos)")
    st.markdown("La velocidad y aceleración se obtienen derivando:")
    st.latex(r"v(t) = h'(t) = 20 - 9.8t \quad\quad a(t) = h''(t) = -9.8\ \text{m/s}^2")

    # Inciso a
    st.markdown('<div class="inciso-header">a. Halle su velocidad inicial de ascenso</div>',
                unsafe_allow_html=True)
    st.markdown("La velocidad inicial corresponde a $t = 0$:")
    st.latex(r"v(0) = 20 - 9.8(0) = 20\ \text{m/s}")
    st.success("✔️ **Velocidad inicial de ascenso:** $v_0 = 20$ m/s")

    # Inciso b
    st.markdown('<div class="inciso-header">b. Halle su velocidad después de 1 segundo</div>',
                unsafe_allow_html=True)
    st.markdown("Evaluamos $v(t)$ en $t = 1$:")
    st.latex(r"v(1) = 20 - 9.8(1) = 10.2\ \text{m/s}")
    st.success("✔️ **Velocidad a t = 1 s:** $v(1) = 10.2$ m/s")

    # Inciso c
    st.markdown('<div class="inciso-header">c. Dibuje la curva usando los ejes t y h</div>',
                unsafe_allow_html=True)
    st.markdown(
        "La función $h(t) = 20t - 4.9t^2$ es una **parábola invertida**. "
        "Toca el suelo cuando $h = 0$: $t(20 - 4.9t) = 0 \\Rightarrow t = 0$ "
        "o $t = \\tfrac{20}{4.9} \\approx 4.08$ s. "
        "Alcanza su altura máxima cuando $v = 0 \\Rightarrow t = \\tfrac{20}{9.8} \\approx 2.04$ s, "
        "con $h_{max} = 20(2.04) - 4.9(2.04)^2 \\approx 20.41$ m."
    )

    # Gráfica de referencia del inciso c (independiente de la función del usuario)
    import sympy as sp
    t_sym = sp.Symbol('t')
    h_expr = 20*t_sym - sp.Rational(49, 10) * t_sym**2
    f_ref = sp.lambdify(t_sym, h_expr, modules=['numpy'])
    t_c = np.linspace(0, 4.5, 200)
    y_c = f_ref(t_c)
    fig_c = go.Figure()
    fig_c.add_trace(go.Scatter(x=t_c, y=y_c, mode='lines',
                               line=dict(color='#FF4444', width=3), name='h(t)'))
    fig_c.add_hline(y=0, line_color='rgba(255,255,255,0.3)', line_dash='dash')
    t_peak = 20/9.8
    h_peak = 20*t_peak - 4.9*t_peak**2
    fig_c.add_trace(go.Scatter(
        x=[t_peak], y=[h_peak], mode='markers+text',
        marker=dict(color='gold', size=14, symbol='triangle-up'),
        text=[f'Máx ({t_peak:.2f}, {h_peak:.2f})'],
        textposition='top center', showlegend=False
    ))
    fig_c.update_layout(
        height=320, margin=dict(l=30, r=20, t=30, b=40),
        xaxis_title='Tiempo t [s]', yaxis_title='Altura h [m]',
        title='Curva h(t) = 20t - 4.9t²',
        plot_bgcolor='#1a1a2e', paper_bgcolor='#1a1a2e',
        font=dict(color='white')
    )
    st.plotly_chart(fig_c, use_container_width=True, key="p1_inciso_c")

    # Inciso d
    st.markdown('<div class="inciso-header">d. Calcule la velocidad máxima de la bola</div>',
                unsafe_allow_html=True)
    st.markdown("Para hallar el máximo de $v(t)$ analizamos su derivada (la aceleración):")
    st.latex(r"a(t) = v'(t) = -9.8\ \text{m/s}^2 \quad (\text{constante y negativa})")
    st.markdown(
        "Como $a(t) < 0$ en todo instante, $v(t)$ es **estrictamente decreciente**. "
        "Por tanto la velocidad máxima ocurre en el menor valor de $t$, es decir, $t = 0$:"
    )
    st.latex(r"v_{\max} = v(0) = 20\ \text{m/s}")
    st.success("✔️ **Velocidad máxima:** $v_{max} = 20$ m/s (en $t = 0$ s)")
    st.info(
        "📝 **Observación:** La velocidad máxima coincide con la velocidad inicial porque la "
        "gravedad actúa frenando la bola en todo momento durante el ascenso."
    )


def render_problem2_solutions():
    """Muestra la resolución paso a paso de los incisos del Problema 2."""
    st.caption("La solución que se muestra corresponde al enunciado original "
               "$s(t) = 7500t - \\tfrac{1}{16}t^3$. Puedes modificar la función arriba para "
               "explorar variantes; los valores de las métricas sí responden a tu función editada.")
    st.markdown("**Datos:** $s(t) = 7500t - \\tfrac{1}{16}t^3$ (distancia en metros, tiempo en segundos)")
    st.markdown("Derivamos para obtener la velocidad y la aceleración:")
    st.latex(r"v(t) = s'(t) = 7500 - \tfrac{3}{16}t^2")
    st.latex(r"a(t) = s''(t) = -\tfrac{3}{8}t")

    # Inciso e
    st.markdown('<div class="inciso-header">e. La distancia de parada en [m]</div>',
                unsafe_allow_html=True)
    st.markdown("El satélite se detiene cuando $v(t) = 0$:")
    st.latex(r"7500 - \tfrac{3}{16}t^2 = 0 \;\Rightarrow\; t^2 = \tfrac{7500 \cdot 16}{3} = 40\,000 \;\Rightarrow\; t = 200\ \text{s}")
    st.markdown("Sustituimos $t = 200$ s en $s(t)$:")
    st.latex(
        r"s(200) = 7500(200) - \tfrac{1}{16}(200)^3 = 1\,500\,000 - 500\,000 = 1\,000\,000\ \text{m}"
    )
    st.success("✔️ **Distancia de parada:** $s_{parada} = 1\\,000\\,000$ m = 1 000 km")

    # Inciso f
    st.markdown('<div class="inciso-header">f. La máxima aceleración negativa de los frenos</div>',
                unsafe_allow_html=True)
    st.markdown(
        "La aceleración es $a(t) = -\\tfrac{3}{8}t$. Es negativa y su **magnitud crece linealmente** "
        "con $t$ (frenado de magnitud constantemente creciente, tal como dice el enunciado)."
    )
    st.markdown(
        "Por lo tanto la aceleración más negativa en el intervalo $[0, 200]$ s ocurre "
        "justamente al detenerse el satélite, en $t = 200$ s:"
    )
    st.latex(r"a(200) = -\tfrac{3}{8}(200) = -75\ \text{m/s}^2")
    st.success("✔️ **Máxima aceleración negativa:** $a_{min} = -75$ m/s² "
               "(magnitud de frenado: $75$ m/s²)")
    st.info(
        "📝 **Observación:** Durante los primeros segundos la fricción atmosférica es pequeña "
        "porque la densidad del aire aún es baja; conforme el satélite penetra la atmósfera "
        "la resistencia crece, alcanzando su máximo justo cuando el satélite se detiene."
    )


# ====================== RENDER DE TABS ======================

def render_problem1_tab():
    """Renderiza la pestaña del Problema 1: lanzamiento vertical de una bola."""
    problem_key = "p1"
    var_name = "t"
    default_func = "20*t - 4.9*t^2"

    func_key = f"{problem_key}_func"
    t_key = f"{problem_key}_t"
    engine_key = f"{problem_key}_engine"

    if func_key not in st.session_state:
        st.session_state[func_key] = default_func
    if t_key not in st.session_state:
        st.session_state[t_key] = 0.0
    if engine_key not in st.session_state:
        st.session_state[engine_key] = DerivativeEngine()
    engine = st.session_state[engine_key]

    # Enunciado
    with st.expander("📋 Enunciado del Problema 1", expanded=True):
        st.markdown("""
**1. Se lanza una bola hacia arriba de modo que su altura sobre el suelo después de t segundos es
$h = 20t - 4.9t^2$ [m].**

- **a.** Halle su velocidad inicial de ascenso
- **b.** Halle su velocidad después de 1 segundo
- **c.** Dibuje la curva usando los ejes $t$ y $h$
- **d.** Calcule la velocidad máxima de la bola
        """)

    ctrl_col, main_col = st.columns([1, 3])

    with ctrl_col:
        st.subheader("⚙️ Controles")

        new_input = st.text_input(
            "h(t) =",
            value=st.session_state[func_key],
            key=f"{problem_key}_func_input",
            help="Escribe directamente o usa la calculadora"
        )
        if new_input != st.session_state[func_key]:
            st.session_state[func_key] = new_input

        with st.expander("🧮 Calculadora", expanded=False):
            render_calculator(func_key, key_suffix=problem_key)

        func_str = st.session_state[func_key] or "0"

        st.write("**Rango**")
        c1, c2 = st.columns(2)
        with c1:
            t_min = st.number_input("Mínimo", value=0.0, step=0.5, key=f"{problem_key}_tmin")
        with c2:
            t_max = st.number_input("Máximo", value=5.0, step=0.5, key=f"{problem_key}_tmax")

        engine.set_variable(var_name)
        engine.parse_function(func_str)

        if engine.function_expr is not None:
            st.markdown("**Derivadas:**")
            st.markdown(f"$v({var_name}) = $ `{engine.get_first_derivative_string()}`")
            st.markdown(f"$a({var_name}) = $ `{engine.get_second_derivative_string()}`")

            constants = engine.get_constants()
            if constants:
                st.write("**Constantes**")
                for const in constants:
                    val = st.slider(
                        f"{const}",
                        min_value=-10.0, max_value=10.0,
                        value=engine.constants.get(const, 1.0),
                        step=0.1,
                        key=f"{problem_key}_const_{const}"
                    )
                    engine.set_constant(const, val)

        st.write("**🕐 Tiempo t**")
        current_t = st.slider(
            "t",
            min_value=float(t_min), max_value=float(t_max),
            value=float(np.clip(st.session_state[t_key], t_min, t_max)),
            step=max((t_max - t_min) / 100, 0.01),
            key=f"{problem_key}_t_slider",
            label_visibility="collapsed"
        )
        st.session_state[t_key] = current_t

    with main_col:
        if engine.function_expr is None:
            st.warning("Ingresa una función válida.")
            return

        y_curr, y1_curr, y2_curr = engine.evaluate_at_point(current_t)

        critical = engine.find_critical_points(t_min, t_max)
        max_height = 25
        for t_crit, y_crit, ptype in critical:
            if ptype == 'Máximo':
                max_height = max(y_crit + 5, 10)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("⏱️ Tiempo", f"{current_t:.2f} s")
        with m2:
            st.metric("📏 Altura", f"{y_curr:.2f} m")
        with m3:
            direction = "↑" if y1_curr > 0 else "↓" if y1_curr < 0 else "•"
            st.metric(f"🚀 Velocidad {direction}", f"{y1_curr:.2f} m/s")
        with m4:
            st.metric("📉 Aceleración", f"{y2_curr:.2f} m/s²")

        sim_col, graph_col = st.columns([1, 2])
        with sim_col:
            st.subheader("🎯 Simulación")
            ball_fig = create_ball_simulation(y_curr, max_height, y1_curr)
            st.plotly_chart(ball_fig, use_container_width=True, key=f"{problem_key}_sim")

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
            fig = create_plots(engine, t_min, t_max, current_t, var_name,
                               pos_fn_label="h", pos_label="Altura", pos_unit="m")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key=f"{problem_key}_graph")

    st.divider()
    st.subheader("📝 Cálculos con Sustituciones (para el t actual)")
    render_substitution_section(engine, current_t, var_name,
                                f_name="h", pos_unit="m", vel_unit="m/s", acc_unit="m/s²",
                                pos_label="Altura")

    st.divider()
    st.subheader("✅ Solución por Incisos")
    render_problem1_solutions()


def render_problem2_tab():
    """Renderiza la pestaña del Problema 2: satélite en reentrada atmosférica."""
    problem_key = "p2"
    var_name = "t"
    default_func = "7500*t - (1/16)*t^3"

    func_key = f"{problem_key}_func"
    t_key = f"{problem_key}_t"
    engine_key = f"{problem_key}_engine"

    if func_key not in st.session_state:
        st.session_state[func_key] = default_func
    if t_key not in st.session_state:
        st.session_state[t_key] = 0.0
    if engine_key not in st.session_state:
        st.session_state[engine_key] = DerivativeEngine()
    engine = st.session_state[engine_key]

    with st.expander("📋 Enunciado del Problema 2", expanded=True):
        st.markdown("""
**2. Un satélite espacial que viaja a 7500 m/s retorna a la atmósfera terrestre donde se reduce
su velocidad por la resistencia atmosférica de magnitud constantemente creciente. Si
$s = 7500t - \\tfrac{1}{16}t^3$, con $t$ en segundos, hallar:**

- **e.** La distancia de parada en [m]
- **f.** La máxima aceleración negativa de los frenos
        """)

    ctrl_col, main_col = st.columns([1, 3])

    with ctrl_col:
        st.subheader("⚙️ Controles")

        new_input = st.text_input(
            "s(t) =",
            value=st.session_state[func_key],
            key=f"{problem_key}_func_input",
            help="Escribe directamente o usa la calculadora"
        )
        if new_input != st.session_state[func_key]:
            st.session_state[func_key] = new_input

        with st.expander("🧮 Calculadora", expanded=False):
            render_calculator(func_key, key_suffix=problem_key)

        func_str = st.session_state[func_key] or "0"

        st.write("**Rango**")
        c1, c2 = st.columns(2)
        with c1:
            t_min = st.number_input("Mínimo", value=0.0, step=10.0, key=f"{problem_key}_tmin")
        with c2:
            t_max = st.number_input("Máximo", value=210.0, step=10.0, key=f"{problem_key}_tmax")

        engine.set_variable(var_name)
        engine.parse_function(func_str)

        if engine.function_expr is not None:
            st.markdown("**Derivadas:**")
            st.markdown(f"$v({var_name}) = $ `{engine.get_first_derivative_string()}`")
            st.markdown(f"$a({var_name}) = $ `{engine.get_second_derivative_string()}`")

            constants = engine.get_constants()
            if constants:
                st.write("**Constantes**")
                for const in constants:
                    val = st.slider(
                        f"{const}",
                        min_value=-10.0, max_value=10.0,
                        value=engine.constants.get(const, 1.0),
                        step=0.1,
                        key=f"{problem_key}_const_{const}"
                    )
                    engine.set_constant(const, val)

        st.write("**🕐 Tiempo t**")
        current_t = st.slider(
            "t",
            min_value=float(t_min), max_value=float(t_max),
            value=float(np.clip(st.session_state[t_key], t_min, t_max)),
            step=max((t_max - t_min) / 200, 0.01),
            key=f"{problem_key}_t_slider",
            label_visibility="collapsed"
        )
        st.session_state[t_key] = current_t

    with main_col:
        if engine.function_expr is None:
            st.warning("Ingresa una función válida.")
            return

        y_curr, y1_curr, y2_curr = engine.evaluate_at_point(current_t)

        # Distancia de parada = máximo de s(t)
        stop_distance = 1_000_000
        critical = engine.find_critical_points(t_min, t_max)
        for t_crit, y_crit, ptype in critical:
            if ptype == 'Máximo':
                stop_distance = max(y_crit, 1.0)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("⏱️ Tiempo", f"{current_t:.2f} s")
        with m2:
            st.metric("📏 Distancia", f"{y_curr:,.0f} m")
        with m3:
            st.metric("🚀 Velocidad", f"{y1_curr:,.2f} m/s")
        with m4:
            st.metric("📉 Aceleración", f"{y2_curr:,.2f} m/s²")

        sim_col, graph_col = st.columns([1, 2])
        with sim_col:
            st.subheader("🛰️ Simulación")
            sat_fig = create_satellite_simulation(y_curr, stop_distance, y1_curr)
            st.plotly_chart(sat_fig, use_container_width=True, key=f"{problem_key}_sim")

            if current_t == 0:
                st.info("🚀 Satélite entrando a la atmósfera")
            elif abs(y1_curr) < 1 and current_t > 0:
                st.success("🛑 ¡Satélite detenido!")
            elif y1_curr > 0:
                st.warning("🌀 Frenando por fricción atmosférica")
            else:
                st.error("⚠️ Velocidad negativa (fuera del rango físico)")

        with graph_col:
            st.subheader("📊 Gráficas")
            fig = create_plots(engine, t_min, t_max, current_t, var_name,
                               pos_fn_label="s", pos_label="Distancia", pos_unit="m")
            if fig:
                st.plotly_chart(fig, use_container_width=True, key=f"{problem_key}_graph")

    st.divider()
    st.subheader("📝 Cálculos con Sustituciones (para el t actual)")
    render_substitution_section(engine, current_t, var_name,
                                f_name="s", pos_unit="m", vel_unit="m/s", acc_unit="m/s²",
                                pos_label="Distancia")

    st.divider()
    st.subheader("✅ Solución por Incisos")
    render_problem2_solutions()


def main():
    if 'show_intro' not in st.session_state:
        st.session_state.show_intro = True

    if st.session_state.show_intro:
        show_intro_screen()
        return

    st.title("SIMULADOR MATEMÁTICO PARA EL APRENDIZAJE SIGNIFICATIVO DE PROBLEMAS DE OPTIMIZACIÓN")

    tab1, tab2 = st.tabs(["📕 Problema 1 · Lanzamiento de una bola",
                          "🛰️ Problema 2 · Reentrada del satélite"])

    with tab1:
        render_problem1_tab()

    with tab2:
        render_problem2_tab()


if __name__ == "__main__":
    main()
