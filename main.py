#!/usr/bin/env python3
"""
Calculadora de Derivadas con Animación

Aplicación de escritorio para resolver derivadas simbólicamente,
graficar funciones y visualizar su comportamiento mediante animaciones.

Autor: Diego
Fecha: 2026
"""

import tkinter as tk
from tkinter import ttk
import sys


def check_dependencies():
    """Verifica que las dependencias estén instaladas."""
    missing = []

    try:
        import sympy
    except ImportError:
        missing.append('sympy')

    try:
        import matplotlib
    except ImportError:
        missing.append('matplotlib')

    try:
        import numpy
    except ImportError:
        missing.append('numpy')

    if missing:
        print("Error: Faltan las siguientes dependencias:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nInstala las dependencias con:")
        print("  pip install -r requirements.txt")
        sys.exit(1)


def main():
    """Punto de entrada principal."""
    # Verificar dependencias
    check_dependencies()

    # Importar después de verificar
    from ui.main_window import MainWindow

    # Crear ventana principal
    root = tk.Tk()

    # Configurar estilo
    style = ttk.Style()
    try:
        style.theme_use('clam')  # Tema moderno
    except:
        pass  # Usar tema por defecto si 'clam' no está disponible

    # Configurar fuente por defecto
    default_font = ('Segoe UI', 10)
    root.option_add('*Font', default_font)

    # Crear aplicación
    app = MainWindow(root)

    # Iniciar loop principal
    root.mainloop()


if __name__ == "__main__":
    main()
