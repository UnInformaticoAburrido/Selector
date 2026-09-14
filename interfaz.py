"""Interfaz Tkinter para Windows y Linux."""
import random
import sys
import webbrowser
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from Selector import ARCHIVO_PREDETERMINADO, Selector
from crear_lista import CrearLista
from importar_lista import importar_nombres
from reportar_bugs import url_reporte


class Aplicacion(tk.Tk):
    def __init__(self):
        if sys.platform == "win32":
            # Evitar que Windows agrupe la aplicación bajo el icono de Python.
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("SelectorMoebius.Desktop.1")
        super().__init__(className="SelectorMoebius")
        self.title("Selector · Alumnos")
        self.geometry("1280x720")
        self.minsize(500, 500)
        self.configure(background="#F0B7C9")
        self._configurar_icono()
        self.selector = None
        self.ruta = None
        self.numero = tk.StringVar(value="1")
        self.resultado = tk.StringVar(value="Carga una lista para empezar")
        self.detalle = tk.StringVar(value="Cada alumno participa una vez por ronda.")
        self.estado = tk.StringVar(value="Sin lista cargada")
        self.archivo = tk.StringVar(value="Archivo de alumnos (.list o .txt)")
        self._estilos()
        self._construir()
        self.bind("<Return>", self._al_pulsar_enter)
        if ARCHIVO_PREDETERMINADO.exists():
            self._cargar(ARCHIVO_PREDETERMINADO)

    def _configurar_icono(self):
        carpeta = Path(__file__).resolve().parent
        try:
            # Conservar referencias: Tk elimina las imágenes si Python las libera.
            self._icono = tk.PhotoImage(file=str(carpeta / "icono_lista_moebius.png"))
            self._iconos = [self._icono] + [self._icono.subsample(factor) for factor in (2, 4, 8, 16)]
            self._icono_cabecera = self._iconos[3]
            self.iconphoto(True, *self._iconos)
            if sys.platform == "win32":
                self.iconbitmap(default=str(carpeta / "icono_lista_moebius.ico"))
        except (OSError, tk.TclError) as error:
            self.after_idle(lambda detalle=str(error): messagebox.showwarning(
                "No se pudo cargar el icono",
                f"Comprueba los archivos de icono junto a interfaz.py.\n\n{detalle}", parent=self))

    def _estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure(".", background="#F0B7C9", foreground="#000000",
                         bordercolor="#91445E", lightcolor="#FFFFFF", darkcolor="#91445E")
        estilo.configure("TFrame", background="#F0B7C9")
        estilo.configure("TLabel", background="#F0B7C9", foreground="#000000", font=("DejaVu Sans", 10))
        estilo.configure("Titulo.TLabel", foreground="#000080", font=("DejaVu Sans", 17, "bold"))
        estilo.configure("Suave.TLabel", foreground="#000080")
        estilo.configure("Tarjeta.TFrame", background="#FFFFFF")
        estilo.configure("Tarjeta.TLabel", background="#FFFFFF")
        estilo.configure("Resultado.TLabel", background="#FFFFFF", foreground="#91445E", font=("DejaVu Sans", 17, "bold"))
        estilo.configure("TButton", background="#FFFFFF", foreground="#91445E",
                         font=("DejaVu Sans", 10), padding=(10, 7))
        estilo.map("TButton", background=[("disabled", "#F0B7C9"), ("pressed", "#91445E"), ("active", "#F0B7C9")],
                   foreground=[("disabled", "#91445E"), ("pressed", "#FFFFFF")])
        estilo.configure("Principal.TButton", background="#D57896", foreground="#000000")
        estilo.map("Principal.TButton", background=[("disabled", "#F0B7C9"), ("pressed", "#91445E"), ("active", "#91445E")],
                   foreground=[("disabled", "#91445E"), ("pressed", "#FFFFFF"), ("active", "#FFFFFF")])
        estilo.configure("TEntry", fieldbackground="#FFFFFF", foreground="#000000")
        estilo.map("TEntry", selectbackground=[("!disabled", "#000080")], selectforeground=[("!disabled", "#FFFFFF")])
        estilo.configure("Treeview", rowheight=30, font=("DejaVu Sans", 10),
                         background="#FFFFFF", fieldbackground="#FFFFFF", foreground="#000000")
        estilo.map("Treeview", background=[("selected", "#000080")], foreground=[("selected", "#FFFFFF")])
        estilo.configure("Treeview.Heading", background="#D57896", foreground="#000000",
                         font=("DejaVu Sans", 10, "bold"), padding=8)
        estilo.map("Treeview.Heading", background=[("active", "#F0B7C9")])
        estilo.configure("Vertical.TScrollbar", background="#D57896", troughcolor="#F0B7C9", arrowcolor="#000080")
        estilo.map("Vertical.TScrollbar", background=[("pressed", "#91445E"), ("active", "#F0B7C9")])
        estilo.configure("Horizontal.TProgressbar", background="#78D5B7", troughcolor="#FFFFFF")

    def _construir(self):
        marco = ttk.Frame(self, padding=14)
        marco.pack(fill="both", expand=True)
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(5, weight=1)
        cabecera = ttk.Frame(marco)
        cabecera.grid(row=0, column=0, sticky="ew")
        cabecera.columnconfigure(0, weight=1)
        ttk.Label(cabecera, text="Selector de alumnos", style="Titulo.TLabel",
                  image=getattr(self, "_icono_cabecera", ""), compound="left", padding=(0, 0, 8, 0)).grid(row=0, column=0, sticky="w")
        acciones = ttk.Frame(cabecera)
        acciones.grid(row=0, column=1, sticky="e")
        ttk.Button(acciones, text="Abrir lista…", command=self.abrir).pack(side="left")
        ttk.Button(acciones, text="Importar lista…", command=self.importar).pack(side="left", padx=(8, 0))
        ttk.Button(acciones, text="Crear lista…", command=self.crear_lista).pack(side="left", padx=(8, 0))
        # Mantener las acciones accesibles al reducir la ventana a 500 píxeles.
        def ajustar_cabecera(evento):
            estrecha = evento.width < 850
            fila = 1 if estrecha else 0
            if acciones.grid_info()["row"] != fila:
                acciones.grid_configure(row=fila, column=0 if estrecha else 1,
                                       columnspan=2 if estrecha else 1,
                                       pady=(8, 0) if estrecha else 0)
        cabecera.bind("<Configure>", ajustar_cabecera)
        ttk.Label(marco, textvariable=self.archivo, style="Suave.TLabel", wraplength=460).grid(row=1, column=0, sticky="w", pady=(6, 10))

        tarjeta = ttk.Frame(marco, style="Tarjeta.TFrame", padding=12)
        tarjeta.grid(row=2, column=0, sticky="ew")
        ttk.Label(tarjeta, text="ALUMNO SELECCIONADO", style="Tarjeta.TLabel").pack(anchor="w")
        nombre = ttk.Label(tarjeta, textvariable=self.resultado, style="Resultado.TLabel", wraplength=440)
        nombre.pack(anchor="w", fill="x", pady=(10, 8))
        tarjeta.bind("<Configure>", lambda evento: nombre.configure(wraplength=max(200, evento.width - 40)))
        ttk.Label(tarjeta, textvariable=self.detalle, style="Tarjeta.TLabel", wraplength=440).pack(anchor="w")

        controles = ttk.Frame(marco)
        controles.grid(row=3, column=0, sticky="ew", pady=10)
        controles.columnconfigure(3, weight=1)
        ttk.Label(controles, text="Número").grid(row=0, column=0, padx=(0, 10))
        self.entrada = ttk.Entry(controles, textvariable=self.numero, width=5, font=("DejaVu Sans", 12))
        self.entrada.grid(row=0, column=1, ipady=6)
        self.boton = ttk.Button(controles, text="Seleccionar", style="Principal.TButton", command=self.seleccionar, state="disabled")
        self.boton.grid(row=0, column=2, padx=10)
        self.aleatorio = ttk.Button(controles, text="Aleatorio", command=self.seleccionar_aleatorio, state="disabled")
        self.aleatorio.grid(row=0, column=3, sticky="w")
        self.reinicio = ttk.Button(controles, text="Nueva ronda", command=self.reiniciar, state="disabled")
        self.reinicio.grid(row=0, column=4, sticky="e")
        def ajustar_controles(evento):
            estrecha = evento.width < 600
            fila = 1 if estrecha else 0
            if self.reinicio.grid_info()["row"] != fila:
                self.reinicio.grid_configure(row=fila, column=0 if estrecha else 4,
                                            columnspan=4 if estrecha else 1,
                                            pady=(6, 0) if estrecha else 0)
        controles.bind("<Configure>", ajustar_controles)

        progreso = ttk.Frame(marco)
        progreso.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(progreso, textvariable=self.estado).pack(anchor="w", pady=(0, 8))
        self.barra = ttk.Progressbar(progreso, maximum=1)
        self.barra.pack(fill="x")

        listado = ttk.Frame(marco)
        listado.grid(row=5, column=0, sticky="nsew")
        listado.columnconfigure(0, weight=1)
        listado.rowconfigure(0, weight=1)
        self.tabla = ttk.Treeview(listado, columns=("numero", "nombre", "estado"), show="headings", selectmode="browse")
        for columna, titulo, ancho in [("numero", "N.º", 45), ("nombre", "Alumno", 265), ("estado", "Participación", 130)]:
            self.tabla.heading(columna, text=titulo)
            self.tabla.column(columna, width=ancho, minwidth=50, stretch=columna == "nombre")
        self.tabla.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(listado, orient="vertical", command=self.tabla.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.tag_configure("visto", foreground="#000000", background="#78D5B7")
        self.tabla.bind("<<TreeviewSelect>>", self._fila_elegida)
        pie = ttk.Frame(marco)
        pie.grid(row=6, column=0, sticky="ew", pady=(12, 0))
        pie.columnconfigure(0, weight=1)
        ttk.Label(pie, text="Si el número ya participó, se elige el siguiente pendiente.",
                  style="Suave.TLabel", wraplength=300).grid(row=0, column=0, sticky="w")
        ttk.Button(pie, text="Reportar bug", command=self.reportar_bug).grid(row=0, column=1, sticky="e")

    def seleccionar_aleatorio(self):
        if self.selector is None:
            return
        if not self.selector.completado:
            self.numero.set(str(random.randint(1, len(self.selector.alumnos))))
        # Exactamente el mismo flujo que escribir un número y pulsar Seleccionar.
        self.seleccionar()

    def reportar_bug(self):
        try:
            url = url_reporte()
            if not webbrowser.open(url, new=2):
                raise OSError(f"No se pudo abrir el navegador. Abre este enlace:\n{url}")
        except (OSError, ValueError, webbrowser.Error) as error:
            messagebox.showerror("Reportar un error", str(error), parent=self)

    def crear_lista(self):
        CrearLista(self, lambda nombres, ruta: self._usar_lista(Selector(nombres), ruta))

    def abrir(self):
        ruta = filedialog.askopenfilename(parent=self, title="Abrir lista de alumnos", filetypes=[("Listas de alumnos", "*.list *.txt"), ("Todos los archivos", "*")])
        if ruta:
            self._cargar(Path(ruta))

    def importar(self):
        ruta = filedialog.askopenfilename(
            parent=self,
            title="Importar lista · Se utilizará la primera columna",
            filetypes=[("Hojas de cálculo", "*.xlsx *.csv"),
                       ("Excel", "*.xlsx"), ("CSV UTF-8", "*.csv")],
        )
        if not ruta:
            return
        omitir_cabecera = messagebox.askyesnocancel(
            "Importar nombres de la primera columna",
            "Se tomarán los nombres de la primera columna (A). En Excel se usará "
            "la primera pestaña. Las celdas vacías se ignorarán.\n\n"
            "La lista importada iniciará una nueva ronda.\n\n"
            "¿La primera fila es un encabezado que debemos omitir?\n"
            "Sí: omitir la primera fila. No: incluirla. Cancelar: no importar.",
            parent=self,
            default=messagebox.NO,
        )
        if omitir_cabecera is None:
            return
        try:
            selector = Selector(importar_nombres(ruta, omitir_cabecera=omitir_cabecera))
        except (OSError, UnicodeError, ValueError) as error:
            messagebox.showerror("No se pudo importar la lista", str(error), parent=self)
            return
        self._usar_lista(selector, Path(ruta))

    def _cargar(self, ruta):
        try:
            selector = Selector.desde_archivo(ruta)
        except (OSError, UnicodeError, ValueError) as error:
            messagebox.showerror("No se pudo abrir la lista", f"{error}\n\nUsa un archivo UTF-8 con un alumno por línea.", parent=self)
            return
        self._usar_lista(selector, ruta)

    def _usar_lista(self, selector, ruta):
        self.selector = selector
        self.ruta = ruta
        self.archivo.set(f"Lista: {ruta.name} · {len(selector.alumnos)} alumnos")
        self._mostrar_ronda()

    def _mostrar_ronda(self):
        self.numero.set("1")
        self.resultado.set("¿Quién participa ahora?")
        self.detalle.set("Elige un número o una fila y pulsa Seleccionar.")
        self.tabla.delete(*self.tabla.get_children())
        for indice, nombre in enumerate(self.selector.alumnos):
            self.tabla.insert("", "end", iid=str(indice), values=(indice + 1, nombre, "Pendiente"))
        self._actualizar()
        self.entrada.focus_set()

    def _actualizar(self):
        vistos = len(self.selector.mirados)
        total = len(self.selector.alumnos)
        self.estado.set(f"{vistos} de {total} han participado · {total - vistos} pendientes")
        self.barra.configure(maximum=total, value=vistos)
        self.boton.configure(state="normal")
        self.reinicio.configure(state="normal")
        self.aleatorio.configure(state="normal")

    def _fila_elegida(self, evento=None):
        seleccion = self.tabla.selection()
        if seleccion:
            self.numero.set(str(int(seleccion[0]) + 1))

    def _al_pulsar_enter(self, evento):
        if evento.widget in (self.entrada, self.tabla):
            self.seleccionar()
            return "break"

    def seleccionar(self):
        if self.selector is None:
            return
        if self.selector.completado:
            if messagebox.askyesno(
                "Lista completada",
                "La lista se ha recorrido por completo y no hay una siguiente persona "
                "en la lista.\n\n¿Quieres iniciar una nueva ronda?",
                parent=self,
            ):
                self.reiniciar()
            return
        try:
            numero = int(self.numero.get().strip())
        except ValueError:
            messagebox.showwarning("Número inválido", "Introduce un número entero.", parent=self)
            self.entrada.focus_set()
            return
        try:
            indice, nombre = self.selector.seleccionar(numero)
        except ValueError as error:
            messagebox.showwarning("Número inválido", str(error), parent=self)
            return
        self.resultado.set(nombre)
        self.detalle.set(f"Alumno n.º {indice + 1}" + (f" · El n.º {numero} ya había participado." if indice + 1 != numero else " · Participación registrada."))
        self.tabla.item(str(indice), values=(indice + 1, nombre, "Ya participó"), tags=("visto",))
        self.tabla.selection_set(str(indice))
        self.tabla.see(str(indice))
        self._actualizar()
        if self.selector.completado:
            self.detalle.set("¡Todos han participado! Pulsa Seleccionar para continuar.")

    def reiniciar(self):
        if self.selector is None:
            return
        if self.selector.mirados and not self.selector.completado:
            if not messagebox.askyesno("Nueva ronda", "¿Reiniciar la participación de todos los alumnos?", parent=self):
                return
        self.selector.reiniciar()
        self._mostrar_ronda()


def main():
    app = Aplicacion()
    app.mainloop()


if __name__ == "__main__":
    main()
