"""Enlaces de incidencias: el usuario revisa y envía el informe en su navegador."""
import json
from pathlib import Path
from urllib.parse import urlencode, urlsplit

CONFIGURACION = Path(__file__).resolve().with_name("proyecto.json")


def url_reporte(ruta=CONFIGURACION):
    with Path(ruta).open(encoding="utf-8") as archivo:
        configuracion = json.load(archivo)
    repositorio = configuracion.get("repositorio", "").strip().rstrip("/")
    if not repositorio:
        raise ValueError("Aún no se ha configurado el repositorio. Añade su URL en proyecto.json, en el campo repositorio.")
    partes = urlsplit(repositorio)
    segmentos = partes.path.strip("/").split("/")
    if (partes.scheme != "https" or partes.netloc != "github.com"
            or len(segmentos) != 2 or not all(segmentos)
            or partes.query or partes.fragment):
        raise ValueError("Configura una URL de GitHub con el formato https://github.com/autor/repositorio en proyecto.json.")
    if repositorio.endswith(".git"):
        repositorio = repositorio[:-4]
    return repositorio + "/issues/new?" + urlencode({"template": "bug_report.yml"})
