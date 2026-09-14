import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from crear_lista import guardar_lista, nombre_completo
from Selector import Selector


class CrearListaTests(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(self.carpeta.cleanup)
        self.ruta = Path(self.carpeta.name) / 'Clase de tarde.list'

    def test_guarda_nombre_apellidos_crlf_y_se_puede_cargar(self):
        nombres = guardar_lista(self.ruta, [(' Ana María ', ' García López '), ('Luis', 'Pérez')])
        self.assertEqual(nombres, ['Ana María García López', 'Luis Pérez'])
        self.assertEqual(self.ruta.read_bytes(), 'Ana María García López\r\nLuis Pérez\r\n'.encode('utf-8'))
        self.assertEqual(Selector.desde_archivo(self.ruta).alumnos, nombres)

    def test_validaciones_no_modifican_archivo_existente(self):
        self.ruta.write_text('Lista anterior\n', encoding='utf-8')
        for personas in [[], [('', 'Pérez')], [('Ana', '')], [('Ana\nLuis', 'García')], [('Ana', 'García\rPérez')]]:
            with self.subTest(personas=personas), self.assertRaises(ValueError):
                guardar_lista(self.ruta, personas)
            self.assertEqual(self.ruta.read_text(), 'Lista anterior\n')

    def test_error_de_escritura_conserva_original_y_limpia_temporal(self):
        self.ruta.write_text('Original\n')
        with patch('crear_lista.os.replace', side_effect=PermissionError('Sin permiso')):
            with self.assertRaises(PermissionError):
                guardar_lista(self.ruta, [('Ana', 'García')])
        self.assertEqual(self.ruta.read_text(), 'Original\n')
        self.assertEqual(list(self.ruta.parent.iterdir()), [self.ruta])

    def test_extension_y_nombres_repetidos(self):
        with self.assertRaises(ValueError):
            guardar_lista(self.ruta.with_suffix('.txt'), [('Ana', 'García')])
        nombres = guardar_lista(self.ruta, [('Ana', 'García'), ('Ana', 'García')])
        self.assertEqual(nombres, ['Ana García', 'Ana García'])


if __name__ == '__main__':
    unittest.main()
