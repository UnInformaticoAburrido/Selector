import tempfile
import unittest
from pathlib import Path

from Selector import Selector


class SelectorTests(unittest.TestCase):
    def test_siguiente_pendiente_vuelve_al_inicio(self):
        selector = Selector(["Ana", "Luis", "Eva"])
        self.assertEqual(selector.seleccionar(3), (2, "Eva"))
        self.assertEqual(selector.seleccionar(3), (0, "Ana"))
        self.assertEqual(selector.seleccionar(3), (1, "Luis"))
        self.assertTrue(selector.completado)
        with self.assertRaises(ValueError):
            selector.seleccionar(1)
        selector.reiniciar()
        self.assertFalse(selector.completado)
        self.assertEqual(selector.seleccionar(3), (2, "Eva"))

    def test_nombres_iguales_son_filas_distintas(self):
        selector = Selector(["Ana", "Ana"])
        self.assertEqual(selector.seleccionar(1)[0], 0)
        self.assertEqual(selector.seleccionar(1)[0], 1)
        self.assertTrue(selector.completado)

    def test_numeros_invalidos_no_modifican_la_ronda(self):
        selector = Selector(["Ana"])
        for numero in (0, -1, 2):
            with self.assertRaises(ValueError):
                selector.seleccionar(numero)
        self.assertEqual(selector.mirados, set())

    def test_archivo_utf8_bom_y_lineas_vacias(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "alumnos.list"
            ruta.write_text("\ufeff Ángela \n\n Luis\n", encoding="utf-8")
            self.assertEqual(Selector.desde_archivo(ruta).alumnos, ["Ángela", "Luis"])
            ruta.write_text("\n \n", encoding="utf-8")
            with self.assertRaises(ValueError):
                Selector.desde_archivo(ruta)


if __name__ == "__main__":
    unittest.main()
