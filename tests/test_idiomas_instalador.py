import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from configuracion import cargar_configuracion
from instaladores.install import SOURCE, payload_paths, prepare_app, desktop_requested
from textos import Catalogo, ESQUEMA

IDIOMAS = ('ES', 'EN-uk', 'EN-us', 'PO', 'ES-la')


class IdiomasTests(unittest.TestCase):
    def test_todas_las_frases_variantes_y_marcadores_en_cada_idioma(self):
        schema = json.loads(ESQUEMA.read_text(encoding='utf-8'))
        for language in IDIOMAS:
            with self.subTest(language=language):
                catalog = Catalogo(SOURCE / 'recursos/textos.xlsx', language.swapcase())
                self.assertEqual(set(catalog.frases), set(schema))
                for key, variants in schema.items():
                    for variant, parameters in variants.items():
                        text = catalog.texto(key, variant, **dict.fromkeys(parameters, 2))
                        self.assertIsInstance(text, str)
                        self.assertTrue(text.strip())
                if language != 'ES':
                    separate = Catalogo(SOURCE / f'recursos/idiomas/{language}.xlsx', language)
                    self.assertEqual(separate.frases, catalog.frases)

    def test_diferencias_regionales_y_respuestas_consola(self):
        expected = {
            'EN-uk': ('Randomise', 'Surname(s)', 'y'),
            'EN-us': ('Randomize', 'Last name(s)', 'y'),
            'PO': ('Aleatório', 'Apelidos', 's'),
            'ES-la': ('Al azar', 'Apellidos', 's'),
        }
        for language, values in expected.items():
            catalog = Catalogo(SOURCE / 'recursos/textos.xlsx', language)
            self.assertEqual((catalog.texto('seleccion.accion', 'aleatoria'),
                              catalog.texto('participante.apellidos'),
                              catalog.texto('consola.continuar', 'respuesta_si')), values)

    def test_config_y_arranque_consola_desde_otra_carpeta(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'config.json'
            data = json.loads((SOURCE / 'configuracion.json').read_text(encoding='utf-8'))
            data['textos'] = str(SOURCE / 'recursos/textos.xlsx')
            for language in IDIOMAS:
                data['languaje'] = language
                path.write_text(json.dumps(data), encoding='utf-8')
                settings = cargar_configuracion(path)
                catalog = Catalogo(settings.textos, settings.languaje)
                run = subprocess.run([sys.executable, str(SOURCE / 'Selector.py'), '--config', str(path), '--help'],
                                     cwd=directory, capture_output=True, text=True, encoding='utf-8',
                                     env={**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8'})
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertIn(catalog.texto('consola.ayuda_general'), run.stdout)


class InstallerTests(unittest.TestCase):
    def test_payload_excluye_datos_privados(self):
        paths = payload_paths()
        self.assertIn('LICENSE', paths)
        self.assertIn('recursos/idiomas/PO.xlsx', paths)
        self.assertFalse(any(Path(p).suffix.casefold() == '.list' for p in paths))
        self.assertFalse(any(p.startswith(('.git/', '.venv/', 'listas/')) for p in paths))
        self.assertNotIn('cosas.html', paths)

    def test_reinstalar_conserva_configuracion_y_listas(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            old, new = base / 'old', base / 'new'
            (old / 'listas').mkdir(parents=True)
            (old / 'listas/Prueba.list').write_text('Test Person\n', encoding='utf-8')
            custom = {'languaje': 'EN-us', 'custom': 'keep me'}
            (old / 'configuracion.json').write_text(json.dumps(custom), encoding='utf-8')
            prepare_app(SOURCE, new, old)
            from iconos import ruta_png, TAMANOS
            for size in TAMANOS:
                self.assertTrue(ruta_png(size, new).is_file(), size)
            self.assertEqual(json.loads((new / 'configuracion.json').read_text()), custom)
            self.assertEqual((new / 'listas/Prueba.list').read_text(), 'Test Person\n')
            self.assertTrue((old / 'listas/Prueba.list').exists())

    def test_desktop_opt_in(self):
        with patch('builtins.input', return_value='') as prompt:
            self.assertFalse(desktop_requested('ask'))
            self.assertIn('Do you want to create a desktop shortcut?', prompt.call_args.args[0])
        with patch('builtins.input', return_value='YES'):
            self.assertTrue(desktop_requested('ask'))
        self.assertTrue(desktop_requested('yes'))
        self.assertFalse(desktop_requested('no'))


if __name__ == '__main__':
    unittest.main()
