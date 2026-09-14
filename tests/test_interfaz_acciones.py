import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from interfaz import Aplicacion
from reportar_bugs import url_reporte
from Selector import Selector


class AccionesTests(unittest.TestCase):
    def test_aleatorio_pasa_numero_valido_a_seleccionar(self):
        for numero in (1, 3):
            with self.subTest(numero=numero):
                selector = Selector(['Ana', 'Luis', 'Eva'])
                campo = Mock()
                app = SimpleNamespace(selector=selector, numero=campo)
                def seleccionar():
                    campo.set.assert_called_once_with(str(numero))
                    selector.seleccionar(numero)
                app.seleccionar = Mock(side_effect=seleccionar)
                with patch('interfaz.random.randint', return_value=numero) as sorteo:
                    Aplicacion.seleccionar_aleatorio(app)
                sorteo.assert_called_once_with(1, 3)
                app.seleccionar.assert_called_once_with()
                self.assertEqual(selector.mirados, {numero - 1})

    def test_aleatorio_completado_usa_aviso_normal(self):
        selector = Selector(['Ana'])
        selector.seleccionar(1)
        app = SimpleNamespace(selector=selector, numero=Mock(), seleccionar=Mock())
        with patch('interfaz.random.randint') as sorteo:
            Aplicacion.seleccionar_aleatorio(app)
        sorteo.assert_not_called()
        app.numero.set.assert_not_called()
        app.seleccionar.assert_called_once_with()

    def test_aleatorio_sin_lista(self):
        app = SimpleNamespace(selector=None, seleccionar=Mock())
        Aplicacion.seleccionar_aleatorio(app)
        app.seleccionar.assert_not_called()

    def test_url_incidencias(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / 'proyecto.json'
            for repositorio in ['https://github.com/autor/selector', 'https://github.com/autor/selector.git']:
                ruta.write_text(json.dumps({'repositorio': repositorio}))
                self.assertEqual(url_reporte(ruta), 'https://github.com/autor/selector/issues/new?template=bug_report.yml')
            for repositorio in ['', 'file:///tmp/archivo', 'https://github.com.ejemplo.org/autor/repo']:
                ruta.write_text(json.dumps({'repositorio': repositorio}))
                with self.assertRaises(ValueError):
                    url_reporte(ruta)

    def test_reportar_abre_formulario_sin_enviar(self):
        with patch('interfaz.url_reporte', return_value='https://github.com/autor/repo/issues/new') as url, patch('interfaz.webbrowser.open', return_value=True) as navegador:
            Aplicacion.reportar_bug(SimpleNamespace())
        url.assert_called_once_with()
        navegador.assert_called_once_with('https://github.com/autor/repo/issues/new', new=2)

    def test_reportar_error_de_navegador(self):
        app = SimpleNamespace()
        with patch('interfaz.url_reporte', return_value='https://github.com/autor/repo/issues/new'), patch('interfaz.webbrowser.open', return_value=False), patch('interfaz.messagebox.showerror') as aviso:
            Aplicacion.reportar_bug(app)
        aviso.assert_called_once()


if __name__ == '__main__':
    unittest.main()
