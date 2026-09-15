"""Carga y validación de los ajustes de la aplicación."""
from dataclasses import dataclass
import json
from pathlib import Path

RUTA_CONFIGURACION = Path(__file__).resolve().with_name('configuracion.json')


class ErrorConfiguracion(ValueError):
    def __init__(self, codigo, **datos):
        self.clave, self.datos = codigo, datos
        super().__init__(f'{codigo}: {datos}')


@dataclass(frozen=True)
class Configuracion:
    ruta: Path
    languaje: str
    textos: Path
    tema: str
    ancho: int
    alto: int
    modo: str


def cargar_configuracion(ruta=RUTA_CONFIGURACION):
    ruta = Path(ruta).resolve()
    try:
        datos = json.loads(ruta.read_text(encoding='utf-8-sig'))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ErrorConfiguracion('config.archivo_error', ruta=str(ruta), detalle=str(error)) from error
    if not isinstance(datos, dict):
        raise ErrorConfiguracion('config.valor_invalido', campo='configuracion.json')
    def invalido(campo):
        raise ErrorConfiguracion('config.valor_invalido', campo=campo)
    idioma = datos.get('languaje')
    if not isinstance(idioma, str) or not idioma.strip():
        invalido('languaje')
    idioma = idioma.strip().upper()
    archivo = datos.get('textos')
    if not isinstance(archivo, str) or not archivo.strip():
        invalido('textos')
    archivo = (ruta.parent / archivo).resolve()
    tema = datos.get('tema')
    if not isinstance(tema, str) or tema.casefold() not in ('claro', 'oscuro', 'sistema'):
        invalido('tema: Claro / Oscuro / Sistema')
    ventana = datos.get('ventana')
    if not isinstance(ventana, dict):
        invalido('ventana')
    ancho, alto = ventana.get('ancho'), ventana.get('alto')
    if type(ancho) is not int or ancho < 500 or ancho > 16384:
        invalido('ventana.ancho: 500–16384')
    if type(alto) is not int or alto < 500 or alto > 16384:
        invalido('ventana.alto: 500–16384')
    modos = {
        'ventana': 'ventana', 'pantalla_completa': 'pantalla_completa',
        'pantalla completa': 'pantalla_completa',
        'pantalla_completa_sin_bordes': 'sin_bordes',
        'pantalla completa sin bordes': 'sin_bordes', 'sin_bordes': 'sin_bordes',
    }
    modo = ventana.get('modo')
    if not isinstance(modo, str) or modo.casefold() not in modos:
        invalido('ventana.modo: ventana / pantalla_completa / pantalla_completa_sin_bordes')
    return Configuracion(ruta, idioma, archivo, tema.casefold(), ancho, alto, modos[modo.casefold()])
