"""Diálogos ttk cuyos botones se traducen desde el catálogo de textos."""
import tkinter as tk
from tkinter import ttk

from textos import tr


def _mostrar(titulo, mensaje, opciones, parent, defecto=None, entrada=False):
    ventana = tk.Toplevel(parent)
    ventana.title(titulo)
    ventana.transient(parent)
    ventana.resizable(False, False)
    marco = ttk.Frame(ventana, padding=20)
    marco.pack(fill='both', expand=True)
    ttk.Label(marco, text=mensaje, wraplength=480, justify='left').pack(anchor='w', pady=(0,16))
    valor = tk.StringVar(ventana)
    campo = None
    if entrada:
        campo = ttk.Entry(marco, textvariable=valor, width=42)
        campo.pack(fill='x', pady=(0,16), ipady=5)
    botones = ttk.Frame(marco)
    botones.pack(anchor='e')
    resultado = [None if entrada or len(opciones) == 3 else False]
    anterior = parent.grab_current()
    def cerrar(respuesta):
        resultado[0] = valor.get() if entrada and respuesta is True else respuesta
        ventana.destroy()
    foco = None
    for clave, respuesta in opciones:
        boton = ttk.Button(botones, text=tr(clave), command=lambda r=respuesta: cerrar(r))
        boton.pack(side='left', padx=(8,0))
        if respuesta == defecto:
            foco = boton
    cancelar = None if entrada or len(opciones) == 3 else False
    ventana.protocol('WM_DELETE_WINDOW', lambda: cerrar(cancelar))
    ventana.bind('<Escape>', lambda evento: cerrar(cancelar))
    if entrada:
        ventana.bind('<Return>', lambda evento: cerrar(True))
    else:
        ventana.bind('<Return>', lambda evento: cerrar(defecto))
    ventana.update_idletasks()
    x = max(0, parent.winfo_rootx() + (parent.winfo_width()-ventana.winfo_reqwidth())//2)
    y = max(0, parent.winfo_rooty() + (parent.winfo_height()-ventana.winfo_reqheight())//2)
    ventana.geometry(f'+{x}+{y}')
    ventana.wait_visibility()
    ventana.grab_set()
    (campo or foco or ventana).focus_set()
    try:
        ventana.wait_window()
    finally:
        if anterior is not None and anterior.winfo_exists():
            anterior.grab_set()
    return resultado[0]


class messagebox:
    NO = 'no'

    @staticmethod
    def showerror(title, message, *, parent):
        return _mostrar(title, message, [('dialogo.aceptar',True)], parent, True)

    showwarning = showerror

    @staticmethod
    def askyesno(title, message, *, parent, default=None):
        return _mostrar(title, message, [('dialogo.si',True),('dialogo.no',False)], parent, default != 'no')

    @staticmethod
    def askyesnocancel(title, message, *, parent, default=None):
        return _mostrar(title, message, [('dialogo.si',True),('dialogo.no',False),('dialogo.cancelar',None)], parent, default != 'no')


class simpledialog:
    @staticmethod
    def askstring(title, prompt, *, parent):
        return _mostrar(title, prompt, [('dialogo.aceptar',True),('dialogo.cancelar',None)], parent, True, entrada=True)
