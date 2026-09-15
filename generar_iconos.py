"""Regenera recursos e ICO desde los PNG originales. Requiere Pillow solo al generar."""
from textos import tr
from iconos import CARPETA, TAMANOS, elegir_tamano, ruta_ico, ruta_png


def generar():
    from PIL import Image

    fuentes = {}
    for tamano in (256, 512, 1024):
        with Image.open(ruta_png(tamano)) as imagen:
            if imagen.size != (tamano, tamano):
                raise ValueError(tr('icono.dimensiones', tamano=tamano))
            fuentes[tamano] = imagen.convert('RGBA')
    (CARPETA / 'recursos' / 'iconos').mkdir(parents=True, exist_ok=True)
    for tamano in TAMANOS:
        if tamano in fuentes:
            continue
        fuente = fuentes[elegir_tamano(tamano, fuentes)]
        fuente.resize((tamano, tamano), Image.Resampling.LANCZOS).save(ruta_png(tamano))
    fuentes[256].save(ruta_ico(), sizes=[(n, n) for n in TAMANOS if n <= 256])
    print(tr('icono.generados', cantidad=len(TAMANOS)))


if __name__ == '__main__':
    generar()
