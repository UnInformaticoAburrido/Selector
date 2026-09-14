"""Lógica compartida del selector y punto de entrada de la aplicación."""
from pathlib import Path

ARCHIVO_PREDETERMINADO = Path(__file__).resolve().with_name("alumnos.list")


class Selector:
    def __init__(self, alumnos):
        # Las líneas vacías no representan alumnos; conservar el orden original.
        self.alumnos = [nombre.strip() for nombre in alumnos if nombre.strip()]
        if not self.alumnos:
            raise ValueError("El archivo no contiene alumnos.")
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
            raise ValueError(f"Introduce un número entre 1 y {len(self.alumnos)}.")
        if self.completado:
            raise ValueError("Ronda completada. Inicia una nueva ronda para continuar.")
        # Volver al principio al llegar al final; cada fila es un alumno distinto.
        indice = numero - 1
        for desplazamiento in range(len(self.alumnos)):
            candidato = (indice + desplazamiento) % len(self.alumnos)
            if candidato not in self.mirados:
                self.mirados.add(candidato)
                return candidato, self.alumnos[candidato]
        raise ValueError("No hay alumnos pendientes. Inicia una nueva ronda para continuar.")

    def reiniciar(self):
        self.mirados.clear()


def consola():
    selector = Selector.desde_archivo()
    while True:
        if selector.completado:
            print("Todos los alumnos han sido mirados")
            if input("¿Desea continuar? (s/n): ").strip().lower() != "s":
                return
            selector.reiniciar()
        try:
            numero = int(input(f"Ingrese un número entre 1 y {len(selector.alumnos)}: "))
            _, nombre = selector.seleccionar(numero)
            print(nombre)
        except ValueError as error:
            print(error)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Selector de alumnos")
    parser.add_argument("--consola", action="store_true", help="Usar el modo de terminal")
    argumentos = parser.parse_args()
    if argumentos.consola:
        consola()
    else:
        from interfaz import main
        main()
