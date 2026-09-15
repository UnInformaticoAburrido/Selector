from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from biblioteca_listas import BibliotecaListas
from interfaz import Aplicacion
from Selector import Selector


class BibliotecaTests(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.base = Path(self.temporal.name)
        self.biblioteca = BibliotecaListas(self.base / 'listas')

    def test_guarda_y_persiste_tras_reabrir(self):
        ruta = self.biblioteca.guardar('Grupo tarde', [' Ana García ', 'Luis Pérez'])
        self.assertEqual(ruta, self.base / 'listas/Grupo tarde.list')
        self.assertEqual(ruta.read_bytes(), 'Ana García\r\nLuis Pérez\r\n'.encode())
        otra = BibliotecaListas(self.biblioteca.directorio)
        self.assertEqual(otra.listar(), [ruta])
        self.assertEqual(Selector.desde_archivo(ruta).alumnos, ['Ana García', 'Luis Pérez'])

    def test_colisiones_sin_sobrescribir_ni_duplicar(self):
        primera = self.biblioteca.guardar('Grupo', ['Ana'])
        segunda = self.biblioteca.guardar('grupo.list', ['Luis'])
        self.assertEqual(segunda.stem, 'grupo (2)')
        self.assertEqual(self.biblioteca.guardar('GRUPO', ['Ana']), primera)
        self.assertEqual(self.biblioteca.guardar('grupo', ['Luis']), segunda)
        self.assertEqual(Selector.desde_archivo(primera).alumnos, ['Ana'])
        self.assertEqual(len(self.biblioteca.listar()), 2)

    def test_nombres_invalidos_y_lista_vacia(self):
        for nombre in ('../fuera', 'ruta/archivo', 'ruta\\archivo', 'CON', '.list', 'a:b', ' ', 'grupo.'):
            with self.subTest(nombre=nombre), self.assertRaises(ValueError):
                self.biblioteca.guardar(nombre, ['Ana'])
        with self.assertRaises(ValueError):
            self.biblioteca.guardar('Vacia', [])
        with self.assertRaises(ValueError):
            self.biblioteca.guardar('Varias lineas', ['Ana\nLuis'])
        self.assertEqual(self.biblioteca.listar(), [])

    def test_listar_orden_y_filtrado(self):
        self.biblioteca.guardar('Zeta', ['Ana'])
        self.biblioteca.guardar('alfa', ['Luis'])
        (self.biblioteca.directorio / 'ignorar.txt').write_text('No es una lista')
        self.assertEqual([ruta.stem for ruta in self.biblioteca.listar()], ['alfa', 'Zeta'])

    def test_incorporar_anteriores_conserva_originales_y_no_repite(self):
        origen = self.base / 'Vieja.list'
        origen.write_text('Ana\nLuis\n')
        (self.base / 'Vacia.list').write_text('')
        self.assertEqual(self.biblioteca.incorporar_anteriores(self.base), ['Vacia.list'])
        self.assertTrue(origen.exists())
        self.biblioteca.incorporar_anteriores(self.base)
        self.assertEqual(len(self.biblioteca.listar()), 1)
        self.assertEqual(origen.read_text(), 'Ana\nLuis\n')

    def test_abrir_externo_guarda_en_biblioteca(self):
        app = SimpleNamespace(biblioteca=self.biblioteca, _usar_lista=Mock())
        selector = Selector(['Ana'])
        Aplicacion._guardar_en_biblioteca(app, selector, self.base / 'Externa.txt')
        _, ruta = app._usar_lista.call_args.args
        self.assertEqual(ruta, self.biblioteca.directorio / 'Externa.list')
        self.assertEqual(Selector.desde_archivo(ruta).alumnos, ['Ana'])

    def test_cambiar_archivo_borrado_no_reemplaza_lista_actual(self):
        app = SimpleNamespace(_usar_lista=Mock())
        with patch('interfaz.messagebox.showerror') as aviso:
            Aplicacion._cambiar_lista(app, self.base / 'Borrada.list')
        app._usar_lista.assert_not_called()
        aviso.assert_called_once()

    def test_menu_muestra_nombres_y_carga_al_pulsar(self):
        ruta = self.biblioteca.guardar('Grupo tarde', ['Ana'])
        app = SimpleNamespace(biblioteca=self.biblioteca, menu_listas=Mock(), _cambiar_lista=Mock())
        Aplicacion._refrescar_listas(app)
        llamada = app.menu_listas.add_command.call_args.kwargs
        self.assertEqual(llamada['label'], 'Grupo tarde')
        llamada['command']()
        app._cambiar_lista.assert_called_once_with(ruta)


if __name__ == '__main__':
    unittest.main()
