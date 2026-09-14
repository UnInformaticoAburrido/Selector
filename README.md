# Selector de alumnos · Möbius

<img src="icono_lista_moebius.svg" alt="Icono de Selector Möbius" width="110">

**Licencia: [PolyForm Noncommercial 1.0.0](LICENSE)**

Organiza los turnos de participación en clase: crea o importa listas de alumnos y elige quién participa, por número o al azar, sin repetir a nadie durante la ronda. Para Windows y Linux.

Puedes ver quién ha participado y quién queda pendiente. Al terminar la lista, inicia otra ronda con un clic. Las listas se guardan en tu ordenador.

## Funciones

- Selección manual por número o fila, con botón **Seleccionar** y tecla **Enter**.
- **Aleatorio** genera un entero entre 1 y el total de alumnos, lo introduce en el campo y ejecuta la selección normal.
- Si el número corresponde a un participante ya seleccionado, se busca el siguiente pendiente, volviendo al principio cuando haga falta. Por ello, el modo aleatorio no es un sorteo uniforme entre los pendientes.
- Tabla de participación, barra de progreso y reinicio de ronda.
- Al pulsar **Seleccionar** o **Aleatorio** tras completar la lista, se pregunta si se desea iniciar una nueva ronda.
- Creación de listas con nombre y apellidos, guardadas como texto plano `.list`.
- Importación de archivos `.list`, `.txt`, `.xlsx` y `.csv`.
- Botón **Reportar bug** para abrir el formulario de incidencias del repositorio en el navegador.
- Ventana inicial de 1280 × 720, redimensionable hasta un mínimo de 500 × 500, y paleta rosa, borgoña, menta y navy.

## Instalación y ejecución

La aplicación está escrita en Python y utiliza Tkinter para la interfaz de escritorio. Necesitas Python 3.10 o posterior, con Tkinter. `openpyxl` se utiliza para importar Excel.

### Windows (PowerShell)

Instala Python con el componente Tcl/Tk y ejecuta desde la carpeta del proyecto:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe Selector.py
```

### Linux

En Ubuntu/Debian, si faltan Tkinter o el módulo de entornos virtuales:

```bash
sudo apt install python3-tk python3-venv
```

Desde la carpeta del proyecto:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python Selector.py
```

No es necesario activar el entorno si utilizas estas rutas. También puedes ejecutar `interfaz.py`. Las rutas de los recursos se resuelven respecto al código, por lo que puedes arrancar desde otra carpeta.

## Listas e importación

`alumnos.list` es un archivo UTF-8 con un alumno por línea. Se carga al iniciar si existe; si no existe, puedes crear, abrir o importar una lista desde la ventana.

### Crear una lista

1. Pulsa **Crear lista…**, junto a **Abrir lista…** e **Importar lista…**.
2. Introduce **Nombre** y **Apellidos** y pulsa **Añadir persona**. Repite para cada participante; puedes quitar las filas seleccionadas si te equivocas.
3. Pulsa **Guardar lista…** y elige la carpeta y el nombre, por ejemplo `clase_tarde.list`.
4. Se guarda en texto plano UTF-8, con nombre y apellidos separados por un espacio y una persona por línea (saltos CRLF compatibles con Windows y Linux). Se carga la nueva lista y comienza una ronda.

Si has escrito la última persona sin pulsar **Añadir**, se incluye al guardar. Una lista vacía no se guarda; cancelar o un error de escritura mantiene la lista activa y permite continuar editando. Para sustituir un archivo existente se pide confirmación.

Ejemplo del contenido:

```text
Ana García López
Luis Pérez Ruiz
```

**Abrir lista…** permite elegir otro `.list` o `.txt`.

### Importar una hoja de cálculo

**Importar lista…** permite seleccionar:

| Formato | Lectura |
| --- | --- |
| Excel `.xlsx` | Primera columna (A) de la primera pestaña |
| CSV UTF-8 `.csv` | Primera columna; separadores coma, punto y coma o tabulación |

Antes de importar se avisa de la columna utilizada y se pregunta si la primera fila es un encabezado. Se ignoran celdas vacías y se conserva el orden. Dos filas con el mismo nombre cuentan como alumnos diferentes. Convierte `.xls` y `.ods` a `.xlsx` o `.csv` antes de importarlos.

Importar o abrir una lista inicia una ronda nueva. Cancelar o un error conserva la lista anterior. La selección y la importación no modifican los archivos originales ni guardan el progreso al cerrar. **Crear lista…** guarda el archivo que elijas. Todos los archivos `.list`, incluidos los ejemplos y los situados en subcarpetas, están excluidos de Git. También se excluyen hojas de cálculo, entornos virtuales, cachés, secretos locales, temporales y configuración local del editor.

## Icono de la aplicación

El original es `icono_lista_moebius.svg`. Tkinter utiliza el PNG y sus tamaños reducidos; Windows utiliza además el ICO multirresolución y una identidad de aplicación propia. El icono también aparece en la cabecera. Conserva los tres archivos junto a `interfaz.py`.

En Linux, para que el menú de aplicaciones y el dock asocien el icono con la ventana:

```bash
.venv/bin/python instalar_acceso_linux.py
```

El comando instala `SelectorMoebius.desktop` en el directorio de aplicaciones del usuario. Abre **Selector de alumnos** desde el menú. Si mueves el proyecto o cambias el entorno virtual, vuelve a ejecutar el instalador. La clase `Selectormoebius` coincide con la que Tkinter comunica al escritorio. Algunos escritorios no muestran iconos en la barra de título; eso no impide que aparezca en el menú o en el dock.

En Windows, para un acceso directo personalizado, selecciona `icono_lista_moebius.ico` en las propiedades del acceso directo. El proyecto contiene scripts Python; no incluye un ejecutable empaquetado.

## Reportar errores

Pulsa **Reportar bug** para abrir el [formulario de errores de GitHub](https://github.com/UnInformaticoAburrido/Selector/issues/new?template=bug_report.yml). Describe qué ocurrió y los pasos para repetir el problema, sin incluir nombres reales de alumnos. Revisa el informe y envíalo desde GitHub.

El repositorio de destino se configura en `proyecto.json`. La aplicación abre el formulario en el navegador, no envía datos automáticamente y no necesita tokens. Si el navegador no se puede abrir, se muestra el enlace.

## Desarrollo y pruebas

Con las dependencias instaladas:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

En Windows utiliza `.venv\Scripts\python.exe`. Las pruebas cubren la selección circular, reinicio, validaciones, importación, generación aleatoria y apertura de reportes. No necesitan una pantalla.

El modo de consola se conserva:

```bash
.venv/bin/python Selector.py --consola
```

### Archivos principales

| Archivo | Función |
| --- | --- |
| `Selector.py` | Lógica de las rondas y punto de entrada |
| `interfaz.py` | Interfaz Tkinter |
| `importar_lista.py` | Lectura de Excel y CSV |
| `crear_lista.py` | Formulario de creación y guardado de listas |
| `reportar_bugs.py` | Enlace al formulario de incidencias |
| `proyecto.json` | URL del repositorio |
| `instalar_acceso_linux.py` | Integración del icono en el escritorio Linux |

## Repositorio Git

Código y reportes: [UnInformaticoAburrido/Selector](https://github.com/UnInformaticoAburrido/Selector).

La rama principal es `main`. `.gitignore` excluye todas las listas `.list`, hojas de cálculo, entornos virtuales, cachés, secretos locales y temporales. `proyecto.json` contiene la URL del repositorio y la descripción breve destinada a usuarios no técnicos.

## Licencia y atribución

Este código y la aplicación se ofrecen bajo [PolyForm Noncommercial License 1.0.0](LICENSE), identificador SPDX `PolyForm-Noncommercial-1.0.0`. Copyright © 2026 Dimitry (UnInformaticoAburrido).

La licencia permite los usos no comerciales y los demás fines expresamente permitidos por su texto, incluidos los usos de las instituciones educativas descritos en él. Los usos comerciales que no estén cubiertos requieren una autorización aparte del autor.

Al distribuir el código o la aplicación debes entregar la licencia o su enlace y conservar los avisos `Required Notice:` incluidos en [NOTICE](NOTICE). Las dependencias de terceros conservan sus respectivas licencias.

El archivo `LICENSE` contiene el texto original sin modificaciones. Consulta las [condiciones completas de PolyForm](https://polyformproject.org/licenses/noncommercial/1.0.0).
