"""Creación de listas de texto plano: un nombre completo por línea."""
import os
from pathlib import Path
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


def nombre_completo(nombre, apellidos):
    nombre, apellidos = nombre.strip(), apellidos.strip()
    if not nombre or not apellidos:
        raise ValueError("Introduce el nombre y los apellidos de la persona.")
    if any(caracter in nombre + apellidos for caracter in ('\r', '\n', '\x00')):
        raise ValueError("Escribe el nombre y los apellidos en una sola línea.")
    return f"{nombre} {apellidos}"


def guardar_lista(ruta, personas):
    """Valida antes de escribir y sustituye el destino solo al terminar."""
    ruta = Path(ruta)
    if ruta.suffix.lower() != '.list':
        raise ValueError("El nombre del archivo debe terminar en .list.")
    nombres = [nombre_completo(nombre, apellidos) for nombre, apellidos in personas]
    if not nombres:
        raise ValueError("Añade al menos una persona antes de guardar la lista.")
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
    def __init__(self, parent, al_guardar):
        super().__init__(parent)
        self.title('Crear lista')
        self.geometry('620x520')
        self.minsize(500, 450)
        self.transient(parent)
        self.al_guardar = al_guardar
        self.nombre = tk.StringVar(self)
        self.apellidos = tk.StringVar(self)
        self.cantidad = tk.StringVar(self, value='0 personas')
        self.protocol('WM_DELETE_WINDOW', self.cancelar)
        self.bind('<Escape>', lambda evento: self.cancelar())

        marco = ttk.Frame(self, padding=16)
        marco.pack(fill='both', expand=True)
        marco.columnconfigure(1, weight=1)
        marco.rowconfigure(5, weight=1)
        ttk.Label(marco, text='Crear una lista de alumnos', style='Titulo.TLabel').grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 8))
        ttk.Label(marco, text='Añade personas. Al guardar podrás elegir el nombre del archivo .list.',
                  wraplength=450).grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 14))
        ttk.Label(marco, text='Nombre').grid(row=2, column=0, sticky='w', padx=(0, 12))
        self.entrada_nombre = ttk.Entry(marco, textvariable=self.nombre)
        self.entrada_nombre.grid(row=2, column=1, sticky='ew', ipady=5, pady=4)
        ttk.Label(marco, text='Apellidos').grid(row=3, column=0, sticky='w', padx=(0, 12))
        self.entrada_apellidos = ttk.Entry(marco, textvariable=self.apellidos)
        self.entrada_apellidos.grid(row=3, column=1, sticky='ew', ipady=5, pady=4)
        self.entrada_nombre.bind('<Return>', self._pasar_a_apellidos)
        self.entrada_apellidos.bind('<Return>', self._anadir_con_enter)
        ttk.Button(marco, text='Añadir persona', command=self.anadir).grid(
            row=4, column=0, columnspan=2, sticky='e', pady=(6, 12))

        listado = ttk.Frame(marco)
        listado.grid(row=5, column=0, columnspan=2, sticky='nsew')
        listado.columnconfigure(0, weight=1)
        listado.rowconfigure(0, weight=1)
        self.tabla = ttk.Treeview(listado, columns=('nombre', 'apellidos'), show='headings', height=5)
        self.tabla.heading('nombre', text='Nombre')
        self.tabla.heading('apellidos', text='Apellidos')
        self.tabla.column('nombre', width=170, minwidth=100)
        self.tabla.column('apellidos', width=260, minwidth=140)
        self.tabla.grid(row=0, column=0, sticky='nsew')
        scroll = ttk.Scrollbar(listado, orient='vertical', command=self.tabla.yview)
        scroll.grid(row=0, column=1, sticky='ns')
        self.tabla.configure(yscrollcommand=scroll.set)
        ttk.Label(marco, textvariable=self.cantidad).grid(row=6, column=0, sticky='w', pady=8)
        ttk.Button(marco, text='Quitar seleccionados', command=self.quitar).grid(row=6, column=1, sticky='e', pady=8)
        botones = ttk.Frame(marco)
        botones.grid(row=7, column=0, columnspan=2, sticky='e')
        ttk.Button(botones, text='Cancelar', command=self.cancelar).pack(side='left', padx=(0, 8))
        ttk.Button(botones, text='Guardar lista…', style='Principal.TButton', command=self.guardar).pack(side='left')
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
            messagebox.showwarning('Datos incompletos', str(error), parent=self)
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
        self.cantidad.set(f'{len(self.tabla.get_children())} personas')

    def guardar(self):
        # Incluir la última persona escrita aunque aún no se haya pulsado Añadir.
        if self.nombre.get().strip() or self.apellidos.get().strip():
            if not self.anadir():
                return
        if not self.tabla.get_children():
            messagebox.showwarning('Lista vacía', 'Añade al menos una persona.', parent=self)
            return
        ruta = filedialog.asksaveasfilename(
            parent=self, title='Guardar lista de alumnos', defaultextension='.list',
            initialdir=Path(__file__).resolve().parent,
            filetypes=[('Lista de alumnos', '*.list')], confirmoverwrite=True,
        )
        if not ruta:
            return
        personas = [self.tabla.item(fila, 'values') for fila in self.tabla.get_children()]
        try:
            nombres = guardar_lista(ruta, personas)
        except (OSError, ValueError) as error:
            messagebox.showerror('No se pudo guardar la lista', str(error), parent=self)
            return
        self.al_guardar(nombres, Path(ruta))
        self.destroy()

    def cancelar(self):
        if self.tabla.get_children() or self.nombre.get().strip() or self.apellidos.get().strip():
            if not messagebox.askyesno('Descartar lista', '¿Cerrar sin guardar esta lista?', parent=self):
                return
        self.destroy()
