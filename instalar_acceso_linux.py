"""Instala el acceso y los PNG por tamaño y escala para el escritorio Linux."""
from textos import tr
import os
from pathlib import Path
import shutil
import subprocess
import sys

from iconos import CARPETA, NOMBRE_ICONO, TAMANOS_ESCRITORIO, ruta_png


def contenido_acceso(carpeta, ejecutable):
    def escapar(valor):
        return str(valor).replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%')
    return '\n'.join([
        '[Desktop Entry]', 'Version=1.0', 'Type=Application',
        'Name=' + tr('app.nombre'), 'Comment=' + tr('app.descripcion'),
        f'Exec="{escapar(ejecutable)}" "{escapar(carpeta / "Selector.py")}"',
        f'Icon={NOMBRE_ICONO}', 'Terminal=false', 'Categories=Education;',
        'StartupWMClass=Selectormoebius', 'StartupNotify=true', '',
    ])


def instalar_iconos(carpeta, datos):
    tema = Path(datos) / 'icons' / 'hicolor'
    rutas = []
    # Directorios estándar: 512x512@2 contiene el PNG de 1024 píxeles.
    for tamano in TAMANOS_ESCRITORIO:
        for escala in (1, 2):
            origen = ruta_png(tamano * escala, carpeta)
            dimension = f'{tamano}x{tamano}' + ('@2' if escala == 2 else '')
            rutas.append((origen, tema / dimension / 'apps' / f'{NOMBRE_ICONO}.png'))
    # Detectar recursos ausentes antes de modificar la instalación.
    for origen, _ in rutas:
        if not origen.is_file():
            raise FileNotFoundError(tr('icono.falta_recurso', ruta=origen))
    for origen, destino in rutas:
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(origen, destino)
    return tema


def main():
    if not sys.platform.startswith('linux'):
        raise SystemExit(tr('acceso.solo_linux'))
    datos = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
    tema = instalar_iconos(CARPETA, datos)
    destino = datos / 'applications/SelectorMoebius.desktop'
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(contenido_acceso(CARPETA, sys.executable), encoding='utf-8')
    # Refrescar cachés existentes sin modificar el índice compartido del tema.
    actualizar = shutil.which('gtk-update-icon-cache')
    if actualizar:
        subprocess.run([actualizar, '--force', '--ignore-theme-index', str(tema)],
                       check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(tr('acceso.instalado', ruta=destino))


if __name__ == '__main__':
    main()
