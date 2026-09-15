"""Lógica compartida del selector y punto de entrada de la aplicación."""
from textos import tr
from pathlib import Path

ARCHIVO_PREDETERMINADO = Path(__file__).resolve().with_name("alumnos.list")


class Selector:
    def __init__(self, alumnos):
        # Las líneas vacías no representan alumnos; conservar el orden original.
        self.alumnos = [nombre.strip() for nombre in alumnos if nombre.strip()]
        if not self.alumnos:
            raise ValueError(tr('lista.sin_alumnos'))
        self.mirados = set()

    @classmethod
    def desde_archivo(cls, ruta=ARCHIVO_PREDETERMINADO):
        with open(ruta, encoding="utf-8-sig") as archivo:
            return cls(archivo)

    @property
    def completado(self):
        return len(self.mirados) == len(self.alumnos)

    def seleccionar(self, numero: int) -> tuple[int, str]:
        if not 1 <= numero <= len(self.alumnos):
            raise ValueError(tr("seleccion.numero_error", "rango", total=len(self.alumnos)))
        if self.completado:
            raise ValueError(tr('ronda.error'))
        # Volver al principio al llegar al final; cada fila es un alumno distinto.
        indice = numero - 1
        for desplazamiento in range(len(self.alumnos)):
            candidato = (indice + desplazamiento) % len(self.alumnos)
            if candidato not in self.mirados:
                self.mirados.add(candidato)
                return candidato, self.alumnos[candidato]
        raise ValueError(tr('ronda.error', 'alternativa'))

    def reiniciar(self):
        self.mirados.clear()


def consola():
    selector = Selector.desde_archivo()
    while True:
        if selector.completado:
            print(tr('ronda.completada', 'consola'))
            if input(tr("consola.continuar")).strip().casefold() != tr("consola.continuar", "respuesta_si").casefold():
                return
            selector.reiniciar()
        try:
            numero = int(input(tr("consola.numero", total=len(selector.alumnos))))
        except ValueError:
            print(tr('seleccion.numero_error'))
            continue
        try:
            _, nombre = selector.seleccionar(numero)
            print(nombre)
        except ValueError as error:
            print(error)


def main():
    import argparse
    from configuracion import cargar_configuracion, RUTA_CONFIGURACION, ErrorConfiguracion
    from textos import iniciar_textos

    previo = argparse.ArgumentParser(add_help=False)
    previo.add_argument('--config', default=str(RUTA_CONFIGURACION))
    opciones, _ = previo.parse_known_args()
    try:
        config = cargar_configuracion(opciones.config)
        iniciar_textos(config)
        class FormatoAyuda(argparse.HelpFormatter):
            def _format_usage(self, usage, actions, groups, prefix):
                return super()._format_usage(usage, actions, groups, tr('consola.prefijo_uso'))

        parser = argparse.ArgumentParser(description=tr('app.nombre'), add_help=False,
                                         formatter_class=FormatoAyuda)
        parser._optionals.title = tr('consola.opciones')
        parser.add_argument('-h', '--help', action='help', help=tr('consola.ayuda_general'))
        parser.add_argument('--consola', action='store_true', help=tr('consola.ayuda'))
        parser.add_argument('--config', default=str(RUTA_CONFIGURACION), help=tr('consola.config'))
        argumentos = parser.parse_args()
        if argumentos.consola:
            consola()
            return 0
        from interfaz import main as interfaz_main
        return interfaz_main(argumentos.config)
    except (ErrorConfiguracion, ImportError) as error:
        from arranque import mostrar_error_inicio
        mostrar_error_inicio(error)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
