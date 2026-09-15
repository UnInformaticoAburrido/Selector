"""Shared per-user installer. Run through the Windows or Linux bootstrap."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv

SOURCE = Path(__file__).resolve().parents[1]
APP_FILES = (
    'Selector.py', 'interfaz.py', 'apariencia.py', 'arranque.py',
    'biblioteca_listas.py', 'configuracion.py', 'crear_lista.py', 'dialogos.py',
    'iconos.py', 'importar_lista.py', 'instalar_acceso_linux.py',
    'reportar_bugs.py', 'textos.py', 'exportar_idiomas.py', 'generar_iconos.py',
    'configuracion.json', 'proyecto.json',
    'requirements.txt', 'LICENSE', 'NOTICE', 'README.md', 'VERSION',
    'recursos/textos.xlsx', 'recursos/textos.schema.json',
    'recursos/idiomas/EN-uk.xlsx', 'recursos/idiomas/EN-us.xlsx',
    'recursos/idiomas/PO.xlsx', 'recursos/idiomas/ES-la.xlsx',
)
ICON_SIZES = (16, 20, 24, 32, 40, 48, 64, 96, 128, 192, 256, 384, 512, 1024)


def payload_paths(source=SOURCE):
    """Explicit allowlist: never distribute user lists, credentials or local files."""
    names = list(APP_FILES)
    names += [f'icono_lista_moebius_{n}x{n}.png' for n in (256, 512, 1024)]
    names += [f'recursos/iconos/{n}.png' for n in ICON_SIZES if n not in (256, 512, 1024)]
    names += ['recursos/iconos/selector.ico']
    for name in names:
        path = Path(source) / name
        if not path.is_file() or path.is_symlink():
            raise FileNotFoundError(f'Missing or invalid installation file: {name}')
    return names


def default_base():
    if sys.platform == 'win32':
        return Path(os.environ['LOCALAPPDATA']) / 'Programs/SelectorMoebius'
    return Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'SelectorMoebius'


def prepare_app(source, stage, previous):
    for name in payload_paths(source):
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / name, target)
    # Preserve data only from the installed copy, never import the developer's lists.
    if (previous / 'configuracion.json').is_file():
        shutil.copy2(previous / 'configuracion.json', stage / 'configuracion.json')
    if (previous / 'listas').is_dir():
        shutil.copytree(previous / 'listas', stage / 'listas')
    else:
        (stage / 'listas').mkdir()


def desktop_requested(value):
    if value != 'ask':
        return value == 'yes'
    return input('Do you want to create a desktop shortcut? [y/N]: ').strip().casefold() in ('y', 'yes')


def desktop_folder():
    tool = shutil.which('xdg-user-dir')
    if tool:
        result = subprocess.run([tool, 'DESKTOP'], capture_output=True, text=True, check=False)
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip())
    return Path.home() / 'Desktop'


def register_linux(app, python, desktop):
    data = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
    # Import the installed module, not a module from the source tree.
    command = (
        'from pathlib import Path; '
        'from instalar_acceso_linux import instalar_iconos, CARPETA; '
        'import sys; instalar_iconos(CARPETA, Path(sys.argv[1]))'
    )
    subprocess.run([str(python), '-c', command, str(data)], cwd=app, check=True)
    def escape(value):
        return str(value).replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%')
    entry = '\n'.join([
        '[Desktop Entry]', 'Version=1.0', 'Type=Application',
        'Name=Selector Moebius', 'Comment=Choose students in rounds without repeats',
        f'Exec="{escape(python)}" "{escape(app / "Selector.py")}"',
        'Icon=SelectorMoebius', 'Terminal=false', 'Categories=Education;',
        'StartupWMClass=Selectormoebius', 'StartupNotify=true', '',
    ])
    menu = data / 'applications/SelectorMoebius.desktop'
    menu.parent.mkdir(parents=True, exist_ok=True)
    menu.write_text(entry, encoding='utf-8')
    if desktop:
        folder = desktop_folder()
        if folder.resolve() == Path.home().resolve():
            print('The desktop is disabled in this session. The application menu shortcut is ready.')
        else:
            folder.mkdir(parents=True, exist_ok=True)
            target = folder / menu.name
            shutil.copy2(menu, target)
            target.chmod(0o755)
            gio = shutil.which('gio')
            if gio:
                subprocess.run([gio, 'set', str(target), 'metadata::trusted', 'true'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            print('Some desktops require right-clicking the shortcut and choosing Allow Launching.')
    for tool, arguments in (
        ('update-desktop-database', [str(menu.parent)]),
        ('gtk-update-icon-cache', ['--force', '--ignore-theme-index', str(data / 'icons/hicolor')]),
    ):
        executable = shutil.which(tool)
        if executable:
            subprocess.run([executable, *arguments], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def install(base, desktop='ask', source=SOURCE):
    source, base = Path(source).resolve(), Path(base).resolve()
    payload_paths(source)
    if base == source or base in source.parents:
        raise ValueError('The installation directory must be separate from the installer source.')
    base.mkdir(parents=True, exist_ok=True)
    lock = base / '.install-lock'
    try:
        lock.mkdir()
    except FileExistsError as error:
        raise RuntimeError(f'Another installation may be running. If it stopped, remove {lock} and retry.') from error
    stage = None
    try:
        print('Close Selector Moebius before continuing the installation.')
        desktop = desktop_requested(desktop)
        environment = base / 'environment'
        print('Preparing the private Python environment...')
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
        print('Installing required libraries...')
        subprocess.run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check',
                        '-r', str(source / 'requirements.txt')], check=True)
        subprocess.run([str(python), '-c', 'import tkinter, openpyxl'], check=True)
        app = base / 'app'
        stage = Path(tempfile.mkdtemp(prefix='.app-new-', dir=base))
        prepare_app(source, stage, app)
        check = 'from configuracion import cargar_configuracion; from textos import iniciar_textos; iniciar_textos(cargar_configuracion())'
        subprocess.run([str(python), '-c', check], cwd=stage, check=True)
        # Keep a backup until the new application is fully registered.
        backup = base / 'app.previous'
        if backup.exists():
            raise RuntimeError(f'A previous backup exists at {backup}. Preserve its data and move it before retrying.')
        if app.exists():
            app.rename(backup)
        try:
            stage.rename(app)
            stage = None
            if sys.platform == 'win32':
                subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                '-File', str(source / 'instaladores/register-windows.ps1'),
                                '-Base', str(base), '-DesktopShortcut', 'yes' if desktop else 'no'], check=True)
            else:
                register_linux(app, python, desktop)
        except Exception:
            if app.exists():
                shutil.rmtree(app)
            if backup.exists():
                backup.rename(app)
            raise
        if backup.exists():
            shutil.rmtree(backup)
        (base / 'installation.json').write_text(json.dumps({
            'version': (app / 'VERSION').read_text().strip(), 'app': str(app),
            'python': str(python), 'desktop_shortcut': desktop,
        }, indent=2), encoding='utf-8')
        print(f'Installation complete: {app}')
        print('Open Selector Moebius from your application menu / Start menu.')
    finally:
        if stage is not None and stage.exists():
            shutil.rmtree(stage)
        lock.rmdir()


def main():
    parser = argparse.ArgumentParser(description='Install Selector Moebius for the current user.')
    parser.add_argument('--base', type=Path, default=default_base())
    parser.add_argument('--desktop', choices=('ask', 'yes', 'no'), default='ask')
    args = parser.parse_args()
    try:
        install(args.base, args.desktop)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f'Installation failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
