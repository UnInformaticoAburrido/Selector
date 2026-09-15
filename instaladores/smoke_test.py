"""Exercise a real installation and its launchers in an isolated test directory."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from install import SOURCE


def main():
    with tempfile.TemporaryDirectory(prefix='Selector install test ') as directory:
        root = Path(directory)
        base = root / 'Program Files' / 'Selector Moebius'
        environment = os.environ.copy()
        if sys.platform != 'win32':
            environment['XDG_DATA_HOME'] = str(root / 'data')
        command = [sys.executable, str(SOURCE / 'instaladores/install.py'), '--base', str(base), '--desktop', 'no']
        subprocess.run(command, env=environment, check=True)
        app = base / 'app'
        python = base / ('environment/Scripts/python.exe' if sys.platform == 'win32' else 'environment/bin/python')
        data = json.loads((app / 'configuracion.json').read_text(encoding='utf-8'))
        data['languaje'] = 'EN-uk'
        (app / 'configuracion.json').write_text(json.dumps(data), encoding='utf-8')
        (app / 'listas/Test.list').write_text('Test Person\n', encoding='utf-8')
        subprocess.run(command, env=environment, check=True)
        assert json.loads((app / 'configuracion.json').read_text())['languaje'] == 'EN-uk'
        assert (app / 'listas/Test.list').read_text() == 'Test Person\n'
        result = subprocess.run([str(python), str(app / 'Selector.py'), '--help'],
                                cwd=root, capture_output=True, text=True, check=True)
        assert 'Show this help message and exit' in result.stdout
        # Open the actual Tk application using each installed language.
        for language in ('ES', 'EN-uk', 'EN-us', 'PO', 'ES-la'):
            data['languaje'] = language
            (app / 'configuracion.json').write_text(json.dumps(data), encoding='utf-8')
            code = ('from interfaz import Aplicacion; from textos import tr; '
                    'app=Aplicacion(); app.update(); '
                    'assert app.title() == tr("app.nombre", "titulo"); '
                    'assert app.selector.alumnos == ["Test Person"]; app.destroy()')
            subprocess.run([str(python), '-c', code], cwd=app, env=environment, check=True)
        if sys.platform == 'win32':
            check = ('$s=New-Object -ComObject WScript.Shell; '
                     '$p=Join-Path ([Environment]::GetFolderPath("Programs")) "Selector Moebius/Selector Moebius.lnk"; '
                     '$l=$s.CreateShortcut($p); if (!(Test-Path $l.TargetPath)) {exit 1}; '
                     'if ($l.Arguments -notlike "*Selector.py*") {exit 1}; '
                     'Remove-Item -LiteralPath $p')
            subprocess.run(['powershell.exe', '-NoProfile', '-Command', check], check=True)
        else:
            menu = root / 'data/applications/SelectorMoebius.desktop'
            assert menu.exists()
            assert str(python) in menu.read_text()
            assert (root / 'data/icons/hicolor/32x32/apps/SelectorMoebius.png').exists()
        print('Installation, reinstallation, menu registration and five GUI languages passed.')


if __name__ == '__main__':
    main()
