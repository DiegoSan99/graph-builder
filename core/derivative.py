"""Motor de cálculo de derivadas usando SymPy."""

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from typing import Dict, List, Tuple, Callable
import re


class DerivativeEngine:
    """Motor para calcular derivadas simbólicas y evaluar funciones."""

    def __init__(self):
        self.transformations = standard_transformations + (implicit_multiplication_application,)
        self.function_expr = None
        self.first_derivative = None
        self.second_derivative = None
        self.variable = sp.Symbol('t')
        self.constants: Dict[str, float] = {}
        self.constant_symbols: Dict[str, sp.Symbol] = {}

    def set_variable(self, var_name: str):
        """Establece la variable independiente."""
        self.variable = sp.Symbol(var_name)

    def parse_function(self, func_str: str) -> bool:
        """
        Parsea una función desde string y calcula sus derivadas.

        Args:
            func_str: String con la función (ej: "20*t - 4.9*t**2")

        Returns:
            True si el parseo fue exitoso, False en caso contrario.
        """
        try:
            # Limpiar la expresión
            func_str = func_str.replace('^', '**')

            # Parsear la expresión
            local_dict = {self.variable.name: self.variable}
            self.function_expr = parse_expr(
                func_str,
                local_dict=local_dict,
                transformations=self.transformations
            )

            # Extraer constantes (símbolos que no son la variable)
            self._extract_constants()

            # Calcular derivadas
            self.first_derivative = sp.diff(self.function_expr, self.variable)
            self.second_derivative = sp.diff(self.first_derivative, self.variable)

            return True
        except Exception as e:
            print(f"Error al parsear la función: {e}")
            return False

    def _extract_constants(self):
        """Extrae las constantes de la expresión."""
        if self.function_expr is None:
            return

        # Obtener todos los símbolos de la expresión
        all_symbols = self.function_expr.free_symbols

        # Filtrar la variable independiente
        constant_symbols = [s for s in all_symbols if s != self.variable]

        # Crear diccionario de constantes con valores por defecto
        self.constant_symbols = {str(s): s for s in constant_symbols}

        # Inicializar valores por defecto para nuevas constantes
        for name in self.constant_symbols:
            if name not in self.constants:
                self.constants[name] = 1.0

    def get_constants(self) -> List[str]:
        """Retorna lista de nombres de constantes."""
        return list(self.constant_symbols.keys())

    def set_constant(self, name: str, value: float):
        """Establece el valor de una constante."""
        self.constants[name] = value

    def get_constant(self, name: str) -> float:
        """Obtiene el valor de una constante."""
        return self.constants.get(name, 1.0)

    def _substitute_constants(self, expr: sp.Expr) -> sp.Expr:
        """Sustituye las constantes por sus valores numéricos."""
        substitutions = {
            self.constant_symbols[name]: value
            for name, value in self.constants.items()
            if name in self.constant_symbols
        }
        return expr.subs(substitutions)

    def get_function_string(self) -> str:
        """Retorna la función como string legible."""
        if self.function_expr is None:
            return ""
        return str(self.function_expr)

    def get_first_derivative_string(self) -> str:
        """Retorna la primera derivada como string."""
        if self.first_derivative is None:
            return ""
        return str(self.first_derivative)

    def get_second_derivative_string(self) -> str:
        """Retorna la segunda derivada como string."""
        if self.second_derivative is None:
            return ""
        return str(self.second_derivative)

    def get_function_latex(self) -> str:
        """Retorna la función en formato LaTeX."""
        if self.function_expr is None:
            return ""
        return sp.latex(self.function_expr)

    def get_first_derivative_latex(self) -> str:
        """Retorna la primera derivada en formato LaTeX."""
        if self.first_derivative is None:
            return ""
        return sp.latex(self.first_derivative)

    def get_second_derivative_latex(self) -> str:
        """Retorna la segunda derivada en formato LaTeX."""
        if self.second_derivative is None:
            return ""
        return sp.latex(self.second_derivative)

    def evaluate_function(self, t_value: float) -> float:
        """Evalúa la función en un punto."""
        if self.function_expr is None:
            return 0.0
        try:
            expr = self._substitute_constants(self.function_expr)
            return float(expr.subs(self.variable, t_value))
        except:
            return float('nan')

    def evaluate_first_derivative(self, t_value: float) -> float:
        """Evalúa la primera derivada en un punto."""
        if self.first_derivative is None:
            return 0.0
        try:
            expr = self._substitute_constants(self.first_derivative)
            return float(expr.subs(self.variable, t_value))
        except:
            return float('nan')

    def evaluate_second_derivative(self, t_value: float) -> float:
        """Evalúa la segunda derivada en un punto."""
        if self.second_derivative is None:
            return 0.0
        try:
            expr = self._substitute_constants(self.second_derivative)
            return float(expr.subs(self.variable, t_value))
        except:
            return float('nan')

    def get_callable_function(self) -> Callable:
        """Retorna una función callable para evaluación rápida."""
        if self.function_expr is None:
            return lambda t: 0.0

        expr = self._substitute_constants(self.function_expr)
        return sp.lambdify(self.variable, expr, modules=['numpy'])

    def get_callable_first_derivative(self) -> Callable:
        """Retorna la primera derivada como función callable."""
        if self.first_derivative is None:
            return lambda t: 0.0

        expr = self._substitute_constants(self.first_derivative)
        return sp.lambdify(self.variable, expr, modules=['numpy'])

    def get_callable_second_derivative(self) -> Callable:
        """Retorna la segunda derivada como función callable."""
        if self.second_derivative is None:
            return lambda t: 0.0

        expr = self._substitute_constants(self.second_derivative)
        return sp.lambdify(self.variable, expr, modules=['numpy'])

    def find_critical_points(self, t_min: float = 0, t_max: float = 10) -> List[Tuple[float, str]]:
        """
        Encuentra puntos críticos (donde la derivada es cero).

        Returns:
            Lista de tuplas (t_value, tipo) donde tipo es 'max', 'min' o 'inflexion'
        """
        if self.first_derivative is None:
            return []

        try:
            expr = self._substitute_constants(self.first_derivative)
            solutions = sp.solve(expr, self.variable)

            critical_points = []
            for sol in solutions:
                t_val = float(sol)
                if t_min <= t_val <= t_max:
                    # Determinar el tipo usando la segunda derivada
                    second_val = self.evaluate_second_derivative(t_val)
                    if second_val < 0:
                        point_type = 'max'
                    elif second_val > 0:
                        point_type = 'min'
                    else:
                        point_type = 'inflexion'
                    critical_points.append((t_val, point_type))

            return critical_points
        except:
            return []
