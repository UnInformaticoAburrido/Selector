"""Build release ZIPs from an explicit public-file allowlist."""
import hashlib
from pathlib import Path
import zipfile

from install import SOURCE, payload_paths


def build(destination=SOURCE / 'dist'):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    version = (SOURCE / 'VERSION').read_text().strip()
    common = payload_paths() + ['instaladores/install.py', 'instaladores/README.md']
    systems = {
        'Windows': ['Install-Windows.cmd', 'instaladores/install-windows.ps1', 'instaladores/register-windows.ps1'],
        'Linux': ['install-linux.sh'],
    }
    checksums = []
    for system, extra in systems.items():
        archive = destination / f'Selector-Moebius-{version}-{system}.zip'
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
            for name in common + extra:
                if name.endswith('.cmd'):
                    content = (SOURCE / name).read_text().replace('\n', '\r\n')
                    output.writestr(f'Selector-Moebius-{version}/{name}', content)
                else:
                    output.write(SOURCE / name, f'Selector-Moebius-{version}/{name}')
        checksums.append(f'{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}')
    (destination / 'SHA256SUMS.txt').write_text('\n'.join(checksums) + '\n', encoding='utf-8')


if __name__ == '__main__':
    build()
