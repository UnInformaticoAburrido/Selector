"""Instala un acceso de escritorio con el SVG y la clase de ventana de Selector."""
import os
from pathlib import Path
import sys


def contenido_acceso(carpeta, ejecutable):
    def escapar(valor):
        return str(valor).replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%')
    # Escapar el valor Icon según el formato Desktop Entry (no es una orden).
    icono = str(carpeta / 'icono_lista_moebius.svg').replace('\\', '\\\\').replace('\n', '\\n')
    return '\n'.join([
        '[Desktop Entry]', 'Version=1.0', 'Type=Application',
        'Name=Selector de alumnos', 'Comment=Selección de alumnos por rondas',
        f'Exec="{escapar(ejecutable)}" "{escapar(carpeta / "Selector.py")}"',
        f'Icon={icono}', 'Terminal=false', 'Categories=Education;',
        'StartupWMClass=Selectormoebius', 'StartupNotify=true', '',
    ])


def main():
    if not sys.platform.startswith('linux'):
        raise SystemExit('Este instalador de acceso es para Linux.')
    carpeta = Path(__file__).resolve().parent
    destino = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'applications/SelectorMoebius.desktop'
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(contenido_acceso(carpeta, sys.executable), encoding='utf-8')
    print(f'Acceso instalado: {destino}')


if __name__ == '__main__':
    main()
