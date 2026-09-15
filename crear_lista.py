"""Creación de listas de texto plano: un nombre completo por línea."""
from textos import tr
import os
from pathlib import Path
import tempfile
import tkinter as tk
from tkinter import ttk
from dialogos import messagebox, simpledialog

from biblioteca_listas import BibliotecaListas


def nombre_completo(nombre, apellidos):
    nombre, apellidos = nombre.strip(), apellidos.strip()
    if not nombre or not apellidos:
        raise ValueError(tr('participante.error'))
    if any(caracter in nombre + apellidos for caracter in ('\r', '\n', '\x00')):
        raise ValueError(tr('participante.error', 'alternativa'))
    return f"{nombre} {apellidos}"


def guardar_lista(ruta, personas):
    """Valida antes de escribir y sustituye el destino solo al terminar."""
    ruta = Path(ruta)
    if ruta.suffix.lower() != '.list':
        raise ValueError(tr('lista.extension'))
    nombres = [nombre_completo(nombre, apellidos) for nombre, apellidos in personas]
    if not nombres:
        raise ValueError(tr('lista.vacia', 'alternativa'))
    temporal = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='',
                                         dir=ruta.parent, prefix='.selector-', suffix='.tmp',
                                         delete=False) as archivo:
            temporal = Path(archivo.name)
            # CRLF es legible tanto en Windows como en Linux.
            archivo.write('\r\n'.join(nombres) + '\r\n')
        os.replace(temporal, ruta)
    finally:
        if temporal is not None:
            temporal.unlink(missing_ok=True)
    return nombres


class CrearLista(tk.Toplevel):
    def __init__(self, parent, al_guardar, biblioteca=None):
        super().__init__(parent)
        self.title(tr('lista.crear', 'titulo'))
        self.geometry('620x520')
        self.minsize(500, 450)
        self.transient(parent)
        self.al_guardar = al_guardar
        self.biblioteca = biblioteca if biblioteca is not None else BibliotecaListas()
        self.nombre = tk.StringVar(self)
        self.apellidos = tk.StringVar(self)
        self.cantidad = tk.StringVar(self, value=tr("participante.cantidad", cantidad=0))
        self.protocol('WM_DELETE_WINDOW', self.cancelar)
        self.bind('<Escape>', lambda evento: self.cancelar())

        marco = ttk.Frame(self, padding=16)
        marco.pack(fill='both', expand=True)
        marco.columnconfigure(1, weight=1)
        marco.rowconfigure(5, weight=1)
        ttk.Label(marco, text=tr('lista.crear', 'alternativa'), style='Titulo.TLabel').grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 8))
        ttk.Label(marco, text=tr('crear.instrucciones'),
                  wraplength=450).grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 14))
        ttk.Label(marco, text=tr('participante.nombre')).grid(row=2, column=0, sticky='w', padx=(0, 12))
        self.entrada_nombre = ttk.Entry(marco, textvariable=self.nombre)
        self.entrada_nombre.grid(row=2, column=1, sticky='ew', ipady=5, pady=4)
        ttk.Label(marco, text=tr('participante.apellidos')).grid(row=3, column=0, sticky='w', padx=(0, 12))
        self.entrada_apellidos = ttk.Entry(marco, textvariable=self.apellidos)
        self.entrada_apellidos.grid(row=3, column=1, sticky='ew', ipady=5, pady=4)
        self.entrada_nombre.bind('<Return>', self._pasar_a_apellidos)
        self.entrada_apellidos.bind('<Return>', self._anadir_con_enter)
        ttk.Button(marco, text=tr('participante.anadir'), command=self.anadir).grid(
            row=4, column=0, columnspan=2, sticky='e', pady=(6, 12))

        listado = ttk.Frame(marco)
        listado.grid(row=5, column=0, columnspan=2, sticky='nsew')
        listado.columnconfigure(0, weight=1)
        listado.rowconfigure(0, weight=1)
        self.tabla = ttk.Treeview(listado, columns=('nombre', 'apellidos'), show='headings', height=5)
        self.tabla.heading('nombre', text=tr('participante.nombre'))
        self.tabla.heading('apellidos', text=tr('participante.apellidos'))
        self.tabla.column('nombre', width=170, minwidth=100)
        self.tabla.column('apellidos', width=260, minwidth=140)
        self.tabla.grid(row=0, column=0, sticky='nsew')
        scroll = ttk.Scrollbar(listado, orient='vertical', command=self.tabla.yview)
        scroll.grid(row=0, column=1, sticky='ns')
        self.tabla.configure(yscrollcommand=scroll.set)
        ttk.Label(marco, textvariable=self.cantidad).grid(row=6, column=0, sticky='w', pady=8)
        ttk.Button(marco, text=tr('participante.quitar'), command=self.quitar).grid(row=6, column=1, sticky='e', pady=8)
        botones = ttk.Frame(marco)
        botones.grid(row=7, column=0, columnspan=2, sticky='e')
        ttk.Button(botones, text=tr('dialogo.cancelar'), command=self.cancelar).pack(side='left', padx=(0, 8))
        ttk.Button(botones, text=tr('lista.guardar'), style='Principal.TButton', command=self.guardar).pack(side='left')
        self.grab_set()
        self.entrada_nombre.focus_set()

    def _pasar_a_apellidos(self, evento):
        self.entrada_apellidos.focus_set()
        return 'break'

    def _anadir_con_enter(self, evento):
        self.anadir()
        return 'break'

    def anadir(self):
        try:
            nombre_completo(self.nombre.get(), self.apellidos.get())
        except ValueError as error:
            messagebox.showwarning(tr('participante.error', 'titulo'), str(error), parent=self)
            return False
        self.tabla.insert('', 'end', values=(self.nombre.get().strip(), self.apellidos.get().strip()))
        self.nombre.set('')
        self.apellidos.set('')
        self._actualizar_cantidad()
        self.tabla.see(self.tabla.get_children()[-1])
        self.entrada_nombre.focus_set()
        return True

    def quitar(self):
        self.tabla.delete(*self.tabla.selection())
        self._actualizar_cantidad()

    def _actualizar_cantidad(self):
        self.cantidad.set(tr("participante.cantidad", cantidad=len(self.tabla.get_children())))

    def guardar(self):
        # Incluir la última persona escrita aunque aún no se haya pulsado Añadir.
        if self.nombre.get().strip() or self.apellidos.get().strip():
            if not self.anadir():
                return
        if not self.tabla.get_children():
            messagebox.showwarning(tr('lista.vacia', 'titulo'), tr('lista.vacia'), parent=self)
            return
        nombre_lista = simpledialog.askstring(
            tr('lista.guardar', 'titulo'), tr('lista.campo_nombre'), parent=self,
        )
        if nombre_lista is None:
            return
        personas = [self.tabla.item(fila, 'values') for fila in self.tabla.get_children()]
        try:
            nombres = [nombre_completo(nombre, apellidos) for nombre, apellidos in personas]
            ruta = self.biblioteca.guardar(nombre_lista, nombres)
        except (OSError, ValueError) as error:
            messagebox.showerror(tr('lista.error', 'guardar'), str(error), parent=self)
            return
        self.al_guardar(nombres, ruta)
        self.destroy()

    def cancelar(self):
        if self.tabla.get_children() or self.nombre.get().strip() or self.apellidos.get().strip():
            if not messagebox.askyesno(tr('lista.descartar', 'titulo'), tr('lista.descartar'), parent=self):
                return
        self.destroy()
