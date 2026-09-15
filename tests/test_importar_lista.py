import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from openpyxl import Workbook

from importar_lista import importar_nombres
from interfaz import Aplicacion
from Selector import Selector


class ImportacionTests(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(self.carpeta.cleanup)
        self.ruta = Path(self.carpeta.name)

    def test_excel_primera_columna_primera_pestana(self):
        libro = Workbook()
        hoja = libro.active
        hoja.append(['Nombre', 'Apellido'])
        hoja.append([' Ángela ', 'No importar'])
        hoja.append([None, 'No es un nombre'])
        hoja.append(['Luis', 'Otro'])
        hoja.append(['Luis', 'Duplicado'])
        libro.create_sheet('Segunda').append(['No importar'])
        libro.active = 1
        ruta = self.ruta / 'alumnos.xlsx'
        libro.save(ruta)
        libro.close()
        self.assertEqual(importar_nombres(ruta, True), ['Ángela', 'Luis', 'Luis'])
        self.assertEqual(importar_nombres(ruta), ['Nombre', 'Ángela', 'Luis', 'Luis'])

    def test_csv_delimitadores_bom_acentos_y_comillas(self):
        for separador in [',', ';', '\t']:
            with self.subTest(separador=separador):
                ruta = self.ruta / 'alumnos.csv'
                ruta.write_text(f'\ufeffNombre{separador}Grupo\n"Pérez, Ana"{separador}A\nLuis{separador}B\n', encoding='utf-8')
                self.assertEqual(importar_nombres(ruta, True), ['Pérez, Ana', 'Luis'])

    def test_csv_una_columna_y_lineas_vacias(self):
        ruta = self.ruta / 'alumnos.csv'
        ruta.write_text('Ana\n\n Luis \n', encoding='utf-8')
        self.assertEqual(importar_nombres(ruta), ['Ana', 'Luis'])

    def test_vacio_y_excel_corrupto(self):
        for nombre, contenido in [('vacio.csv', '\n \n'), ('malo.xlsx', 'no es Excel')]:
            ruta = self.ruta / nombre
            ruta.write_text(contenido, encoding='utf-8')
            with self.assertRaises(ValueError):
                importar_nombres(ruta)

    def test_cancelar_o_error_conserva_ronda(self):
        selector = Selector(['Ana'])
        selector.seleccionar(1)
        app = SimpleNamespace(selector=selector, _guardar_en_biblioteca=Mock())
        for archivo, respuesta in [('', False), ('archivo.xlsx', None), ('inexistente.csv', False)]:
            with self.subTest(archivo=archivo), patch('interfaz.filedialog.askopenfilename', return_value=archivo), patch('interfaz.messagebox.askyesnocancel', return_value=respuesta), patch('interfaz.messagebox.showerror'):
                Aplicacion.importar(app)
                self.assertIs(app.selector, selector)
                self.assertTrue(app.selector.completado)
                app._guardar_en_biblioteca.assert_not_called()

    def test_importar_carga_lista_validada(self):
        ruta = self.ruta / 'alumnos.csv'
        ruta.write_text('Nombre\nAna\nLuis\n', encoding='utf-8')
        app = SimpleNamespace(_guardar_en_biblioteca=Mock())
        with patch('interfaz.filedialog.askopenfilename', return_value=str(ruta)), patch('interfaz.messagebox.askyesnocancel', return_value=True):
            Aplicacion.importar(app)
        selector, origen = app._guardar_en_biblioteca.call_args.args
        self.assertEqual(selector.alumnos, ['Ana', 'Luis'])
        self.assertEqual(selector.mirados, set())
        self.assertEqual(origen, ruta)


if __name__ == '__main__':
    unittest.main()
