"""Biblioteca local de listas; conserva los originales y evita sobrescrituras."""
from textos import tr
from pathlib import Path

from Selector import Selector

DIRECTORIO_LISTAS = Path(__file__).resolve().parent / 'listas'


def validar_nombre(nombre):
    nombre = nombre.strip()
    if nombre.lower().endswith('.list'):
        nombre = nombre[:-5]
    reservados = {'CON', 'PRN', 'AUX', 'NUL'} | {f'{prefijo}{i}' for prefijo in ('COM', 'LPT') for i in range(1, 10)}
    if (not nombre or nombre in ('.', '..') or len(nombre) > 200
            or nombre.endswith(('.', ' '))
            or any(ord(c) < 32 or c in '<>:"/\\|?*' for c in nombre)
            or nombre.split('.')[0].upper() in reservados):
        raise ValueError(tr('lista.nombre_invalido'))
    return nombre


class BibliotecaListas:
    def __init__(self, directorio=DIRECTORIO_LISTAS):
        self.directorio = Path(directorio)

    def listar(self):
        self.directorio.mkdir(parents=True, exist_ok=True)
        return sorted((p for p in self.directorio.iterdir() if p.is_file() and p.suffix.lower() == '.list'),
                      key=lambda p: (p.stem.casefold(), p.name))

    def guardar(self, nombre, alumnos):
        nombre = validar_nombre(nombre)
        nombres = Selector(alumnos).alumnos
        if any('\n' in n or '\r' in n or '\x00' in n for n in nombres):
            raise ValueError(tr('lista.una_linea'))
        self.directorio.mkdir(parents=True, exist_ok=True)
        numero = 1
        while True:
            etiqueta = nombre if numero == 1 else f'{nombre} ({numero})'
            # Evitar diferencias de comportamiento entre Windows y Linux.
            existentes = {p.stem.casefold(): p for p in self.listar()}
            ruta = existentes.get(etiqueta.casefold(), self.directorio / f'{etiqueta}.list')
            if ruta.exists():
                try:
                    if Selector.desde_archivo(ruta).alumnos == nombres:
                        return ruta
                except (OSError, UnicodeError, ValueError):
                    pass
                numero += 1
                continue
            try:
                archivo = ruta.open('x', encoding='utf-8', newline='')
            except FileExistsError:
                # Otra instancia acaba de crear este archivo; volver a comprobarlo.
                continue
            try:
                with archivo:
                    archivo.write('\r\n'.join(nombres) + '\r\n')
            except OSError:
                ruta.unlink(missing_ok=True)
                raise
            return ruta

    def incorporar_anteriores(self, carpeta):
        """Incorpora las listas de versiones anteriores sin borrar originales.

        Si el nombre ya está en la biblioteca, se respeta la copia guardada.
        Devuelve los archivos que no pudieron incorporarse.
        """
        existentes = {p.stem.casefold() for p in self.listar()}
        errores = []
        for ruta in sorted(Path(carpeta).iterdir()):
            if not ruta.is_file() or ruta.suffix.lower() != '.list' or ruta.stem.casefold() in existentes:
                continue
            try:
                self.guardar(ruta.stem, Selector.desde_archivo(ruta).alumnos)
                existentes.add(ruta.stem.casefold())
            except (OSError, UnicodeError, ValueError):
                errores.append(ruta.name)
        return errores
