"""Interfaz Tkinter para Windows y Linux."""
from textos import tr, iniciar_textos
import random
import sys
import webbrowser
import tkinter as tk
from queue import Queue, Empty
from threading import Event, Thread
from pathlib import Path
from tkinter import filedialog, ttk
from dialogos import messagebox
from configuracion import cargar_configuracion, RUTA_CONFIGURACION, ErrorConfiguracion
from apariencia import aplicar_estilos, detectar_tema_sistema

from Selector import ARCHIVO_PREDETERMINADO, Selector
from biblioteca_listas import BibliotecaListas
from crear_lista import CrearLista
from importar_lista import importar_nombres
from reportar_bugs import url_reporte
from iconos import TAMANOS, elegir_tamano, ruta_ico, ruta_png


class Aplicacion(tk.Tk):
    def __init__(self, ruta_configuracion=RUTA_CONFIGURACION):
        self.ajustes = cargar_configuracion(ruta_configuracion)
        iniciar_textos(self.ajustes)
        if sys.platform == "win32":
            # Evitar que Windows agrupe la aplicación bajo el icono de Python.
            import ctypes
            # Solicitar la escala real del sistema antes de crear la ventana.
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except (AttributeError, OSError):
                ctypes.windll.user32.SetProcessDPIAware()
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("SelectorMoebius.Desktop.1")
        super().__init__(className="SelectorMoebius")
        self.title(tr('app.nombre', 'titulo'))
        self.geometry(f"{self.ajustes.ancho}x{self.ajustes.alto}")
        self.minsize(500, 500)
        self._tema_actual = 'oscuro' if self.ajustes.tema == 'oscuro' else 'claro'
        self._parar_tema = Event()
        self._cola_tema = Queue()
        self._temporizador_tema = None
        self._modo_actual = 'ventana'
        self.protocol('WM_DELETE_WINDOW', self.destroy)
        self._configurar_icono()
        self.biblioteca = BibliotecaListas()
        self.selector = None
        self.ruta = None
        self.numero = tk.StringVar(value="1")
        self.resultado = tk.StringVar(value=tr('inicio.resultado'))
        self.detalle = tk.StringVar(value=tr('inicio.detalle'))
        self.estado = tk.StringVar(value=tr('inicio.estado'))
        self.archivo = tk.StringVar(value=tr('inicio.archivo'))
        self._estilos()
        self._construir()
        self._estilos()
        self.bind("<Escape>", self._salir_pantalla)
        self.bind("<F11>", self._alternar_pantalla)
        self.after_idle(lambda: self._aplicar_modo(self.ajustes.modo))
        if self.ajustes.tema == "sistema":
            self._observar_tema()
        self.bind("<Return>", self._al_pulsar_enter)
        self._iniciar_biblioteca()

    def _configurar_icono(self):
        try:
            # La escala de Tk son píxeles por punto (96 DPI = 96/72).
            escala = float(self.tk.call("tk", "scaling")) / (96 / 72)
            tamano_cabecera = elegir_tamano(round(32 * escala))
            # X11 recomienda un icono grande y uno pequeño; el dock dispone
            # además de todos los tamaños instalados en el tema hicolor.
            tamanos = sorted({256, tamano_cabecera}, reverse=True)
            if sys.platform == "win32":
                tamanos = [n for n in TAMANOS if n <= 256]
                if tamano_cabecera not in tamanos:
                    tamanos.append(tamano_cabecera)
            imagenes = {n: tk.PhotoImage(master=self, file=str(ruta_png(n))) for n in tamanos}
            self._iconos = list(imagenes.values())
            self._icono = imagenes[256]
            self._icono_cabecera = imagenes[tamano_cabecera]
            self.iconphoto(True, *self._iconos)
            if sys.platform == "win32":
                # Windows elige los recursos pequeños/grandes del ICO según
                # las métricas de icono del sistema; conserva también los PNG.
                self.iconbitmap(default=str(ruta_ico()))
        except (OSError, tk.TclError) as error:
            self.after_idle(lambda detalle=str(error): messagebox.showwarning(
                tr('icono.error', 'titulo'),
                tr("icono.error", detalle=detalle), parent=self))

    def _estilos(self):
        aplicar_estilos(self, self._tema_actual)

    def _observar_tema(self):
        def observar():
            while not self._parar_tema.is_set():
                tema = detectar_tema_sistema()
                if not self._parar_tema.is_set():
                    self._cola_tema.put(tema)
                self._parar_tema.wait(3)
        Thread(target=observar, daemon=True).start()
        self._recibir_tema()

    def _recibir_tema(self):
        ultimo = None
        try:
            while True:
                ultimo = self._cola_tema.get_nowait()
        except Empty:
            pass
        if ultimo is not None and ultimo != self._tema_actual:
            self._tema_actual = ultimo
            self._estilos()
        self._temporizador_tema = self.after(300, self._recibir_tema)

    def _aplicar_modo(self, modo):
        # Cambiar la decoración al volver a mapear la ventana es fiable en X11.
        self.withdraw()
        self.attributes('-fullscreen', False)
        self.overrideredirect(False)
        if modo == 'ventana':
            self.geometry(f'{self.ajustes.ancho}x{self.ajustes.alto}')
            self.volver_ventana.grid_remove()
        else:
            self.volver_ventana.grid()
            if modo == 'sin_bordes':
                self.overrideredirect(True)
                self.geometry(f'{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0')
            else:
                self.attributes('-fullscreen', True)
        self._modo_actual = modo
        self.deiconify()

    def _salir_pantalla(self, evento=None):
        if self._modo_actual != 'ventana':
            self._aplicar_modo('ventana')
        return 'break'

    def _alternar_pantalla(self, evento=None):
        self._aplicar_modo('pantalla_completa' if self._modo_actual == 'ventana' else 'ventana')
        return 'break'

    def destroy(self):
        self._parar_tema.set()
        if self._temporizador_tema is not None:
            self.after_cancel(self._temporizador_tema)
            self._temporizador_tema = None
        super().destroy()

    def _construir(self):
        marco = ttk.Frame(self, padding=14)
        marco.pack(fill="both", expand=True)
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(5, weight=1)
        cabecera = ttk.Frame(marco)
        cabecera.grid(row=0, column=0, sticky="ew")
        cabecera.columnconfigure(0, weight=1)
        ttk.Label(cabecera, text=tr('app.nombre'), style="Titulo.TLabel",
                  image=getattr(self, "_icono_cabecera", ""), compound="left", padding=(0, 0, 8, 0)).grid(row=0, column=0, sticky="w")
        acciones = ttk.Frame(cabecera)
        acciones.grid(row=0, column=1, sticky="e")
        ttk.Button(acciones, text=tr('lista.abrir'), command=self.abrir).pack(side="left")
        ttk.Button(acciones, text=tr('lista.importar'), command=self.importar).pack(side="left", padx=(8, 0))
        ttk.Button(acciones, text=tr('lista.crear'), command=self.crear_lista).pack(side="left", padx=(8, 0))
        # Mantener las acciones accesibles al reducir la ventana a 500 píxeles.
        def ajustar_cabecera(evento):
            estrecha = evento.width < 850
            fila = 1 if estrecha else 0
            if acciones.grid_info()["row"] != fila:
                acciones.grid_configure(row=fila, column=0 if estrecha else 1,
                                       columnspan=2 if estrecha else 1,
                                       pady=(8, 0) if estrecha else 0)
        cabecera.bind("<Configure>", ajustar_cabecera)
        listas = ttk.Frame(marco)
        listas.grid(row=1, column=0, sticky="ew", pady=(6, 10))
        listas.columnconfigure(1, weight=1)
        self.menu_listas = tk.Menu(self, tearoff=False, postcommand=self._refrescar_listas,
                                  background=self.paleta["superficie"], foreground=self.paleta["texto"],
                                  activebackground=self.paleta["activo"], activeforeground=self.paleta["sobre_activo"])
        self.cambiar = ttk.Menubutton(listas, text=tr('lista.cambiar'), menu=self.menu_listas)
        self.cambiar.grid(row=0, column=0, sticky="nw", padx=(0, 12))
        etiqueta_lista = ttk.Label(listas, textvariable=self.archivo, style="Suave.TLabel", wraplength=290)
        etiqueta_lista.grid(row=0, column=1, sticky="w")
        listas.bind("<Configure>", lambda evento: etiqueta_lista.configure(
            wraplength=max(160, evento.width - self.cambiar.winfo_width() - 12)))

        tarjeta = ttk.Frame(marco, style="Tarjeta.TFrame", padding=12)
        tarjeta.grid(row=2, column=0, sticky="ew")
        ttk.Label(tarjeta, text=tr('participante.seleccionado'), style="Tarjeta.TLabel").pack(anchor="w")
        nombre = ttk.Label(tarjeta, textvariable=self.resultado, style="Resultado.TLabel", wraplength=440)
        nombre.pack(anchor="w", fill="x", pady=(10, 8))
        tarjeta.bind("<Configure>", lambda evento: nombre.configure(wraplength=max(200, evento.width - 40)))
        ttk.Label(tarjeta, textvariable=self.detalle, style="Tarjeta.TLabel", wraplength=440).pack(anchor="w")

        controles = ttk.Frame(marco)
        controles.grid(row=3, column=0, sticky="ew", pady=10)
        controles.columnconfigure(3, weight=1)
        ttk.Label(controles, text=tr('participante.numero')).grid(row=0, column=0, padx=(0, 10))
        self.entrada = ttk.Entry(controles, textvariable=self.numero, width=5, font=("DejaVu Sans", 12))
        self.entrada.grid(row=0, column=1, ipady=6)
        self.boton = ttk.Button(controles, text=tr('seleccion.accion'), style="Principal.TButton", command=self.seleccionar, state="disabled")
        self.boton.grid(row=0, column=2, padx=10)
        self.aleatorio = ttk.Button(controles, text=tr('seleccion.accion', 'aleatoria'), command=self.seleccionar_aleatorio, state="disabled")
        self.aleatorio.grid(row=0, column=3, sticky="w")
        self.reinicio = ttk.Button(controles, text=tr('ronda.nueva'), command=self.reiniciar, state="disabled")
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
        for columna, titulo, ancho in [("numero", tr('participante.numero', 'abreviado'), 45), ("nombre", tr('participante.alumno'), 265), ("estado", tr('participante.participacion'), 130)]:
            self.tabla.heading(columna, text=titulo)
            self.tabla.column(columna, width=ancho, minwidth=50, stretch=columna == "nombre")
        self.tabla.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(listado, orient="vertical", command=self.tabla.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.tag_configure("visto", foreground=self.paleta["sobre_visto"], background=self.paleta["visto"])
        self.tabla.bind("<<TreeviewSelect>>", self._fila_elegida)
        pie = ttk.Frame(marco)
        pie.grid(row=6, column=0, sticky="ew", pady=(12, 0))
        pie.columnconfigure(0, weight=1)
        ttk.Label(pie, text=tr('seleccion.ayuda'),
                  style="Suave.TLabel", wraplength=300).grid(row=0, column=0, sticky="w")
        ttk.Button(pie, text=tr('reporte.accion'), command=self.reportar_bug).grid(row=0, column=1, sticky="e")
        self.volver_ventana = ttk.Button(pie, text=tr('pantalla.volver'), command=self._salir_pantalla)
        self.volver_ventana.grid(row=1, column=0, columnspan=2, sticky='e', pady=(6,0))
        self.volver_ventana.grid_remove()

    def _iniciar_biblioteca(self):
        try:
            errores = self.biblioteca.incorporar_anteriores(ARCHIVO_PREDETERMINADO.parent)
            rutas = self.biblioteca.listar()
        except OSError as error:
            messagebox.showerror(tr('biblioteca.error', 'titulo'), str(error), parent=self)
            return
        self._refrescar_listas()
        if rutas:
            ruta = next((p for p in rutas if p.stem.casefold() == 'alumnos'), rutas[0])
            self._cambiar_lista(ruta)
        if errores:
            messagebox.showwarning(tr('biblioteca.incorporar_error', 'titulo'),
                                   tr("biblioteca.incorporar_error", archivos=", ".join(errores)), parent=self)

    def _refrescar_listas(self):
        self.menu_listas.delete(0, "end")
        try:
            rutas = self.biblioteca.listar()
        except OSError:
            self.menu_listas.add_command(label=tr('biblioteca.error'), state="disabled")
            return
        if not rutas:
            self.menu_listas.add_command(label=tr('biblioteca.vacia'), state="disabled")
        for ruta in rutas:
            self.menu_listas.add_command(label=ruta.stem, command=lambda elegida=ruta: self._cambiar_lista(elegida))

    def _cambiar_lista(self, ruta):
        try:
            selector = Selector.desde_archivo(ruta)
        except (OSError, UnicodeError, ValueError) as error:
            messagebox.showerror(tr('lista.error'), str(error), parent=self)
            return
        self._usar_lista(selector, ruta)

    def _guardar_en_biblioteca(self, selector, origen):
        try:
            ruta = self.biblioteca.guardar(origen.stem, selector.alumnos)
        except (OSError, ValueError) as error:
            messagebox.showerror(tr('lista.error', 'guardar'), str(error), parent=self)
            return
        self._usar_lista(selector, ruta)

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
                raise OSError(tr("reporte.navegador", url=url))
        except (OSError, ValueError, webbrowser.Error) as error:
            messagebox.showerror(tr('reporte.accion', 'titulo'), str(error), parent=self)

    def crear_lista(self):
        CrearLista(self, lambda nombres, ruta: self._usar_lista(Selector(nombres), ruta), self.biblioteca)

    def abrir(self):
        ruta = filedialog.askopenfilename(parent=self, title=tr('lista.abrir', 'titulo'), filetypes=[(tr('archivo.filtro_listas'), "*.list *.txt"), (tr('archivo.filtro_todos'), "*")])
        if ruta:
            self._cargar(Path(ruta))

    def importar(self):
        ruta = filedialog.askopenfilename(
            parent=self,
            title=tr('lista.importar', 'titulo'),
            filetypes=[(tr('archivo.filtro_hojas'), "*.xlsx *.csv"),
                       (tr('archivo.filtro_excel'), "*.xlsx"), (tr('archivo.filtro_csv'), "*.csv")],
        )
        if not ruta:
            return
        omitir_cabecera = messagebox.askyesnocancel(
            tr('importar.aviso', 'titulo'),
            tr('importar.aviso'),
            parent=self,
            default=messagebox.NO,
        )
        if omitir_cabecera is None:
            return
        try:
            selector = Selector(importar_nombres(ruta, omitir_cabecera=omitir_cabecera))
        except (OSError, UnicodeError, ValueError) as error:
            messagebox.showerror(tr('lista.error', 'importar'), str(error), parent=self)
            return
        self._guardar_en_biblioteca(selector, Path(ruta))

    def _cargar(self, ruta):
        try:
            selector = Selector.desde_archivo(ruta)
        except (OSError, UnicodeError, ValueError) as error:
            messagebox.showerror(tr('lista.error', 'abrir'), tr("lista.utf8", detalle=error), parent=self)
            return
        self._guardar_en_biblioteca(selector, ruta)

    def _usar_lista(self, selector, ruta):
        self.selector = selector
        self.ruta = ruta
        self.archivo.set(tr("lista.leyenda", nombre=ruta.stem, cantidad=len(selector.alumnos)))
        self._mostrar_ronda()
        self._refrescar_listas()

    def _mostrar_ronda(self):
        self.numero.set("1")
        self.resultado.set(tr('seleccion.espera'))
        self.detalle.set(tr('seleccion.espera', 'ayuda'))
        self.tabla.delete(*self.tabla.get_children())
        for indice, nombre in enumerate(self.selector.alumnos):
            self.tabla.insert("", "end", iid=str(indice), values=(indice + 1, nombre, tr('participante.estado')))
        self._actualizar()
        self.entrada.focus_set()

    def _actualizar(self):
        vistos = len(self.selector.mirados)
        total = len(self.selector.alumnos)
        self.estado.set(tr("ronda.progreso", vistos=vistos, total=total, pendientes=total-vistos))
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
                tr('ronda.completada', 'titulo'),
                tr('ronda.completada', 'pregunta'),
                parent=self,
            ):
                self.reiniciar()
            return
        try:
            numero = int(self.numero.get().strip())
        except ValueError:
            messagebox.showwarning(tr('seleccion.numero_error', 'titulo'), tr('seleccion.numero_error'), parent=self)
            self.entrada.focus_set()
            return
        try:
            indice, nombre = self.selector.seleccionar(numero)
        except ValueError as error:
            messagebox.showwarning(tr('seleccion.numero_error', 'titulo'), str(error), parent=self)
            return
        self.resultado.set(nombre)
        self.detalle.set(tr("seleccion.detalle", "alternativa" if indice + 1 != numero else "texto", numero=indice+1, solicitado=numero))
        self.tabla.item(str(indice), values=(indice + 1, nombre, tr('participante.estado', 'realizada')), tags=("visto",))
        self.tabla.selection_set(str(indice))
        self.tabla.see(str(indice))
        self._actualizar()
        if self.selector.completado:
            self.detalle.set(tr('ronda.completada'))

    def reiniciar(self):
        if self.selector is None:
            return
        if self.selector.mirados and not self.selector.completado:
            if not messagebox.askyesno(tr('ronda.nueva'), tr('ronda.nueva', 'pregunta'), parent=self):
                return
        self.selector.reiniciar()
        self._mostrar_ronda()


def main(ruta_configuracion=RUTA_CONFIGURACION):
    try:
        app = Aplicacion(ruta_configuracion)
    except (ErrorConfiguracion, ImportError) as error:
        from arranque import mostrar_error_inicio
        mostrar_error_inicio(error)
        return 1
    app.mainloop()
    return 0


if __name__ == "__main__":
    main()
