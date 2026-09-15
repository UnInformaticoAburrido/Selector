from pathlib import Path
import struct
import tempfile
import unittest

from iconos import CARPETA, TAMANOS, elegir_tamano, ruta_ico, ruta_png
from instalar_acceso_linux import contenido_acceso, instalar_iconos


class IconosTests(unittest.TestCase):
    def test_resoluciones_para_escalas_habituales(self):
        for escala, esperado in [(1,32), (1.25,40), (1.5,48), (2,64), (3,96)]:
            self.assertEqual(elegir_tamano(32 * escala), esperado)
        self.assertEqual(elegir_tamano(33), 40)
        self.assertEqual(elegir_tamano(2000), 1024)

    def test_png_tienen_dimensiones_correctas(self):
        for tamano in TAMANOS:
            with self.subTest(tamano=tamano):
                cabecera = ruta_png(tamano).read_bytes()[:24]
                self.assertEqual(cabecera[:8], b'\x89PNG\r\n\x1a\n')
                self.assertEqual(struct.unpack('>II', cabecera[16:24]), (tamano, tamano))

    def test_ico_incluye_tamanos_windows(self):
        datos = ruta_ico().read_bytes()
        reservado, tipo, cantidad = struct.unpack_from('<HHH', datos)
        self.assertEqual((reservado,tipo), (0,1))
        tamanos = set()
        for i in range(cantidad):
            ancho, alto, _, _, _, _, longitud, inicio = struct.unpack_from('<BBBBHHII', datos, 6 + i*16)
            tamanos.add((ancho or 256, alto or 256))
            self.assertGreater(longitud, 0)
            self.assertLessEqual(inicio + longitud, len(datos))
        self.assertEqual(tamanos, {(n,n) for n in TAMANOS if n <= 256})

    def test_instalacion_hidpi_y_acceso_por_nombre(self):
        with tempfile.TemporaryDirectory() as carpeta:
            datos = Path(carpeta)
            tema = instalar_iconos(CARPETA, datos)
            self.assertEqual((tema / '32x32/apps/SelectorMoebius.png').read_bytes(), ruta_png(32).read_bytes())
            self.assertEqual((tema / '32x32@2/apps/SelectorMoebius.png').read_bytes(), ruta_png(64).read_bytes())
            self.assertEqual((tema / '512x512@2/apps/SelectorMoebius.png').read_bytes(), ruta_png(1024).read_bytes())
            self.assertIn('Icon=SelectorMoebius\n', contenido_acceso(CARPETA, CARPETA / '.venv/bin/python'))


if __name__ == '__main__':
    unittest.main()
