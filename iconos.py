"""Recursos de icono y elección de resolución, sin dependencias de ejecución."""
from textos import tr
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
TAMANOS = (16, 20, 24, 32, 40, 48, 64, 96, 128, 192, 256, 384, 512, 1024)
NOMBRE_ICONO = 'SelectorMoebius'
TAMANOS_ESCRITORIO = (16, 24, 32, 48, 64, 96, 128, 192, 256, 512)


def elegir_tamano(objetivo, disponibles=TAMANOS):
    """Elige el menor tamaño suficiente; usa el mayor si no hay uno suficiente."""
    tamanos = sorted(disponibles)
    if not tamanos:
        raise ValueError(tr('icono.sin_tamanos'))
    return next((tamano for tamano in tamanos if tamano >= objetivo), tamanos[-1])


def ruta_png(tamano, carpeta=CARPETA):
    carpeta = Path(carpeta)
    if tamano in (256, 512, 1024):
        return carpeta / f'icono_lista_moebius_{tamano}x{tamano}.png'
    return carpeta / 'recursos' / 'iconos' / f'{tamano}.png'


def ruta_ico(carpeta=CARPETA):
    return Path(carpeta) / 'recursos' / 'iconos' / 'selector.ico'
