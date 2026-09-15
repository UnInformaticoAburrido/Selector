"""Diagnóstico de arranque, incluso cuando el propio catálogo no puede abrirse."""
from pathlib import Path
import sys


def mostrar_error_inicio(error):
    titulo, mensaje = 'Selector', str(error)
    try:
        from textos import Catalogo
        catalogo = Catalogo(Path(__file__).resolve().parent / 'recursos/textos.xlsx', 'ES')
        titulo = catalogo.texto('config.titulo')
        if hasattr(error, 'clave'):
            mensaje = catalogo.texto(error.clave, **error.datos)
    except Exception:
        # Sin libro/dependencias solo es posible emitir el diagnóstico técnico.
        pass
    print(mensaje, file=sys.stderr)
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        try:
            messagebox.showerror(titulo, mensaje, parent=root)
        finally:
            root.destroy()
    except Exception:
        pass
