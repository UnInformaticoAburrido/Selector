# Selector de alumnos · Möbius

<img src="icono_lista_moebius_256x256.png" alt="Icono de Selector Möbius" width="110">

**Licencia: [PolyForm Noncommercial 1.0.0](LICENSE)**

Organiza los turnos de participación en clase: crea o importa listas de alumnos y elige quién participa, por número o al azar, sin repetir a nadie durante la ronda. Para Windows y Linux.

Puedes ver quién ha participado y quién queda pendiente. Al terminar la lista, inicia otra ronda con un clic. Las listas se guardan en tu ordenador.

## Funciones

- Selección manual por número o fila, con botón **Seleccionar** y tecla **Enter**.
- **Aleatorio** genera un entero entre 1 y el total de alumnos, lo introduce en el campo y ejecuta la selección normal.
- Si el número corresponde a un participante ya seleccionado, se busca el siguiente pendiente, volviendo al principio cuando haga falta. Por ello, el modo aleatorio no es un sorteo uniforme entre los pendientes.
- Tabla de participación, barra de progreso y reinicio de ronda.
- Al pulsar **Seleccionar** o **Aleatorio** tras completar la lista, se pregunta si se desea iniciar una nueva ronda.
- Creación de listas con nombre y apellidos, guardadas como texto plano `.list` en la carpeta `listas/`.
- Menú **Cambiar lista**: pulsa el nombre de una lista guardada para cargarla al instante.
- Importación de archivos `.list`, `.txt`, `.xlsx` y `.csv`.
- Botón **Reportar bug** para abrir el formulario de incidencias del repositorio en el navegador.
- Ventana inicial de 1280 × 720, redimensionable hasta un mínimo de 500 × 500, y paleta rosa, borgoña, menta y navy.

## Instalación y ejecución

### Instaladores de la versión 1.0

Descarga y extrae el paquete de tu sistema en [Releases](https://github.com/UnInformaticoAburrido/Selector/releases/tag/v1.0):

- **Windows:** abre `Install-Windows.cmd`. Instala Python con Tkinter si no encuentra una versión compatible, prepara las dependencias y registra **Selector Moebius** en el menú Inicio.
- **Linux:** ejecuta `bash install-linux.sh` desde la carpeta extraída, sin `sudo`. Instala los paquetes de Python que falten mediante el gestor de paquetes de la distribución y registra **Selector Moebius** en el menú de aplicaciones.

Ambos preguntan **“Do you want to create a desktop shortcut?”** para crear opcionalmente un acceso en el escritorio. Los mensajes del instalador están en inglés. La aplicación conserva sus idiomas configurables y arranca en español por defecto.

La instalación es para el usuario actual: `%LOCALAPPDATA%\Programs\SelectorMoebius` en Windows y `${XDG_DATA_HOME:-~/.local/share}/SelectorMoebius` en Linux. Cada instalación contiene `app/` (programa, configuración y `listas/`) y `environment/` (Python virtual y dependencias). Las reinstalaciones conservan las listas y la configuración; cierra la aplicación antes de reinstalar.

Se necesita conexión a Internet para descargar Python o las dependencias. Consulta [las instrucciones del instalador](instaladores/README.md) para distribuciones compatibles, detalles técnicos y desinstalación.

### Ejecución desde el código fuente

La aplicación está escrita en Python y utiliza Tkinter para la interfaz de escritorio. Necesitas Python 3.10 o posterior, con Tkinter. `openpyxl` es necesario tanto para cargar los textos de la aplicación como para importar Excel.

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

## Configuración y traducciones

Edita [configuracion.json](configuracion.json) y reinicia la aplicación para aplicar los cambios:

```json
{
  "languaje": "ES",
  "textos": "recursos/textos.xlsx",
  "tema": "Claro",
  "ventana": {
    "ancho": 1280,
    "alto": 720,
    "modo": "ventana"
  }
}
```

| Ajuste | Valores y funcionamiento |
| --- | --- |
| `languaje` | Nombre de la pestaña del libro: `ES`, `EN-uk`, `EN-us`, `PO` o `ES-la`. No distingue mayúsculas y minúsculas. Se conserva la escritura `languaje` de la clave solicitada. |
| `textos` | Ruta del archivo Excel, relativa a la carpeta del archivo de configuración. También admite una ruta absoluta. |
| `tema` | `Claro`, `Oscuro` o `Sistema`. Sistema consulta la apariencia de Windows/Linux y sigue sus cambios mientras la aplicación está abierta; si no puede detectarla, utiliza Claro. |
| `ventana.ancho` / `ventana.alto` | Tamaño inicial en píxeles, entre 500 y 16384 por dimensión. También se utiliza al volver al modo ventana. |
| `ventana.modo` | `ventana`, `pantalla_completa` o `pantalla_completa_sin_bordes`. |

**Esc** y el botón **Volver a ventana** permiten salir de pantalla completa o del modo sin bordes. **F11** alterna entre ventana y pantalla completa. La apariencia del sistema en Linux se consulta mediante el [portal de ajustes del escritorio](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Settings.html), con alternativas para escritorios GNOME.

Para usar otro archivo de configuración:

```bash
.venv/bin/python Selector.py --config /ruta/a/otra_configuracion.json
```

### Editar los textos o añadir un idioma

El libro [recursos/textos.xlsx](recursos/textos.xlsx) contiene **88 filas de frases y 124 textos contando las variantes por idioma**. Incluye etiquetas, botones, avisos, validaciones y mensajes de consola y de las herramientas auxiliares.

| Pestaña / `languaje` | Idioma | Archivo independiente |
| --- | --- | --- |
| `ES` | Español de España | Libro principal |
| `EN-uk` | Inglés del Reino Unido | [EN-uk.xlsx](recursos/idiomas/EN-uk.xlsx) |
| `EN-us` | Inglés de Estados Unidos | [EN-us.xlsx](recursos/idiomas/EN-us.xlsx) |
| `PO` | Portugués de Portugal | [PO.xlsx](recursos/idiomas/PO.xlsx) |
| `ES-la` | Español latinoamericano | [ES-la.xlsx](recursos/idiomas/ES-la.xlsx) |

Por ejemplo, cambia solo `"languaje": "EN-uk"` para usar inglés británico. Si prefieres su archivo independiente, cambia también `"textos": "recursos/idiomas/EN-uk.xlsx"`. `PO` y `ES-la` son los identificadores solicitados para esta aplicación.

- La columna `clave` identifica la frase: conserva su contenido.
- La columna `texto` contiene la frase principal. `variante_1`, `variante_2` y `variante_3` contienen sus alternativas en la misma fila, incluidos los plurales cuando corresponda.
- Los comentarios de las celdas indican qué variante se utiliza y qué marcadores necesita. Conserva los marcadores entre llaves, como `{cantidad}` o `{nombre}`; puedes cambiar su posición dentro de la traducción.
- Escribe texto, sin fórmulas. Puedes ordenar las filas, pero conserva las claves, los encabezados y la posición de las columnas de variantes.

Para añadir otro idioma, duplica una pestaña, cambia su nombre, traduce sus celdas y establece ese nombre en `languaje`. Cada pestaña debe contener todas las frases. Para mantener sincronizados los cuatro archivos independientes tras editar el libro principal, ejecuta `.venv/bin/python exportar_idiomas.py` (en Windows: `.venv\Scripts\python.exe exportar_idiomas.py`). Los archivos independientes son exportaciones del libro principal; utiliza el principal para mantener las traducciones del proyecto.

`recursos/textos.schema.json` describe las claves, las variantes y los marcadores que necesita el código; no contiene una copia de los textos. No hace falta editarlo para traducir. Al arrancar se comprueban la configuración, el idioma, las frases y los marcadores. Los errores se muestran antes de abrir la ventana principal. Si el propio catálogo está dañado o falta la dependencia que permite leerlo, el diagnóstico de emergencia puede ser técnico.

Los nombres de las personas y de sus listas conservan su contenido. Los títulos y filtros del selector de archivos proceden de Excel; sus controles nativos siguen el idioma y la apariencia del sistema operativo. Los detalles de errores proporcionados por el sistema o por bibliotecas externas pueden mantener su idioma original.

## Listas e importación

Las listas se guardan en la carpeta **`listas/`**, junto al programa, independientemente de la carpeta desde la que lo ejecutes. Cada archivo `.list` contiene texto UTF-8 con una persona por línea.

### Cambiar de lista

Pulsa **Cambiar lista** y después el nombre de la lista que quieras utilizar. El menú muestra los archivos guardados sin la extensión `.list`, ordenados por nombre. No necesitas buscar de nuevo el archivo ni pulsar un botón de confirmación. Cambiar de lista inicia una ronda nueva; el progreso anterior no se guarda.

Las listas que abras desde otro lugar o importes desde Excel/CSV se copian a `listas/`, conservando los archivos originales. Las creadas en la aplicación se guardan directamente allí. Al volver a abrir la aplicación, siguen disponibles. Se carga `alumnos` si existe; en su defecto, la primera lista por orden alfabético.

Al iniciar, las listas `.list` que hubiera junto al programa de versiones anteriores se incorporan a la biblioteca sin borrar sus originales. Si ese nombre ya existe, se respeta la copia guardada. Si no hay listas, puedes crear, abrir o importar una.

Si abres, importas o creas otra lista con un nombre ya usado, se reutiliza la copia si contiene exactamente las mismas personas en el mismo orden. Si el contenido difiere, se guarda como `Nombre (2)`, `Nombre (3)`, etc., sin sobrescribir ninguna lista. El menú se actualiza cada vez que lo abres, por lo que también muestra los archivos que añadas manualmente a la carpeta.

### Crear una lista

1. Pulsa **Crear lista…**, junto a **Abrir lista…** e **Importar lista…**.
2. Introduce **Nombre** y **Apellidos** y pulsa **Añadir persona**. Repite para cada participante; puedes quitar las filas seleccionadas si te equivocas.
3. Pulsa **Guardar lista…** e introduce el nombre, por ejemplo `Clase de tarde`. Se guardará como `listas/Clase de tarde.list`.
4. Se guarda en texto plano UTF-8, con nombre y apellidos separados por un espacio y una persona por línea (saltos CRLF compatibles con Windows y Linux). Se carga la nueva lista y comienza una ronda.

Si has escrito la última persona sin pulsar **Añadir**, se incluye al guardar. Una lista vacía no se guarda; cancelar o un error de escritura mantiene la lista activa y permite continuar editando. Los nombres coincidentes con contenido diferente se numeran automáticamente para conservar ambas listas.

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

Importar o abrir una lista inicia una ronda nueva. Cancelar o un error conserva la lista anterior. La selección y la importación no modifican los archivos originales ni guardan el progreso al cerrar. **Crear lista…**, **Abrir lista…** e **Importar lista…** guardan una copia en `listas/`. Todos los archivos `.list`, incluidos los ejemplos y los situados en subcarpetas, están excluidos de Git. También se excluyen hojas de cálculo, entornos virtuales, cachés, secretos locales, temporales y configuración local del editor.

## Icono de la aplicación

Los originales son los PNG `icono_lista_moebius_256x256.png`, `icono_lista_moebius_512x512.png` e `icono_lista_moebius_1024x1024.png`. Se incluyen versiones de **16, 20, 24, 32, 40, 48, 64, 96, 128, 192, 256, 384, 512 y 1024 píxeles**, con transparencia. Las reducciones se generan con filtro Lanczos desde la fuente de tamaño suficiente más próxima.

- **Windows:** `recursos/iconos/selector.ico` contiene varias resoluciones hasta 256 píxeles. Tkinter lo entrega a Windows para elegir el icono según las métricas del sistema. Para un acceso directo, utiliza ese mismo ICO en sus propiedades.
- **Linux:** el instalador registra los PNG en el tema `hicolor`, en tamaños estándar y escalas 1× y 2×. El acceso utiliza el nombre `SelectorMoebius`, de modo que el escritorio puede buscar la resolución adecuada; para 512 píxeles a escala 2× está disponible el PNG de 1024.
- **Cabecera de la ventana:** la aplicación elige el PNG según la escala que informa Tk al arrancar. Si cambias la escala de pantalla durante el uso, reinicia la aplicación para actualizar la cabecera.

Conserva los tres PNG originales y la carpeta `recursos/iconos/` al copiar el proyecto. Para instalar o actualizar el acceso y los iconos de Linux:

```bash
.venv/bin/python instalar_acceso_linux.py
```

Después abre **Selector de alumnos** desde el menú. Si mueves el proyecto, cambias el entorno virtual o sustituyes los PNG, vuelve a ejecutar el instalador. Algunos escritorios no muestran un icono en la barra de título; el menú y el dock gestionan sus iconos por separado.

### Regenerar los tamaños tras cambiar los PNG

Los recursos ya están incluidos; no se necesita Pillow para ejecutar la aplicación. Solo para regenerarlos:

```bash
.venv/bin/python -m pip install Pillow
.venv/bin/python generar_iconos.py
```

En Windows, utiliza `.venv\Scripts\python.exe` en esos comandos. El proyecto contiene scripts Python; no incluye un ejecutable empaquetado.

Referencias técnicas: [iconos de ventana en Tk](https://www.tcl-lang.org/man/tcl8.6/TkCmd/wm.htm) y [especificación de temas de iconos](https://specifications.freedesktop.org/icon-theme/latest/).

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
| `configuracion.py` / `configuracion.json` | Lectura, validación y valores de los ajustes |
| `textos.py` / `recursos/textos.xlsx` | Catálogo de frases por idioma y variantes |
| `apariencia.py` | Temas claro/oscuro y detección del tema del sistema |
| `dialogos.py` | Ventanas de aviso y preguntas con botones traducidos |
| `importar_lista.py` | Lectura de Excel y CSV |
| `crear_lista.py` | Formulario de creación y guardado de listas |
| `biblioteca_listas.py` | Carpeta de listas, incorporación de archivos y resolución de nombres repetidos |
| `reportar_bugs.py` | Enlace al formulario de incidencias |
| `proyecto.json` | URL del repositorio |
| `instalar_acceso_linux.py` | Integración del icono en el escritorio Linux |

## Repositorio Git

Código y reportes: [UnInformaticoAburrido/Selector](https://github.com/UnInformaticoAburrido/Selector).

La rama principal es `main`. `.gitignore` excluye todas las listas `.list`, hojas de cálculo de usuarios, entornos virtuales, cachés, secretos locales y temporales. Las excepciones de `recursos/textos.xlsx` y los cuatro libros de `recursos/idiomas/` permiten distribuir los catálogos necesarios para arrancar. `proyecto.json` contiene la URL del repositorio y la descripción breve destinada a usuarios no técnicos.

## Licencia y atribución

Este código y la aplicación se ofrecen bajo [PolyForm Noncommercial License 1.0.0](LICENSE), identificador SPDX `PolyForm-Noncommercial-1.0.0`. Copyright © 2026 Dimitry (UnInformaticoAburrido).

La licencia permite los usos no comerciales y los demás fines expresamente permitidos por su texto, incluidos los usos de las instituciones educativas descritos en él. Los usos comerciales que no estén cubiertos requieren una autorización aparte del autor.

Al distribuir el código o la aplicación debes entregar la licencia o su enlace y conservar los avisos `Required Notice:` incluidos en [NOTICE](NOTICE). Las dependencias de terceros conservan sus respectivas licencias.

El archivo `LICENSE` contiene el texto original sin modificaciones. Consulta las [condiciones completas de PolyForm](https://polyformproject.org/licenses/noncommercial/1.0.0).
