"""Export the additional language sheets from the master workbook."""
from pathlib import Path
from openpyxl import load_workbook

RAIZ = Path(__file__).resolve().parent
IDIOMAS = ('EN-uk', 'EN-us', 'PO', 'ES-la')


def exportar(origen=RAIZ / 'recursos/textos.xlsx', destino=RAIZ / 'recursos/idiomas'):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    for idioma in IDIOMAS:
        libro = load_workbook(origen)
        try:
            for hoja in list(libro):
                if hoja.title != idioma:
                    libro.remove(hoja)
            if len(libro.worksheets) != 1:
                raise ValueError(idioma)
            libro.active = 0
            libro.save(destino / f'{idioma}.xlsx')
        finally:
            libro.close()


if __name__ == '__main__':
    exportar()
