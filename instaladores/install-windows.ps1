param([ValidateSet('ask', 'yes', 'no')][string]$DesktopShortcut = 'ask')
$ErrorActionPreference = 'Stop'

function Find-Python {
    # An incompatible/missing interpreter is a candidate to skip, not a setup error.
    $ErrorActionPreference = 'SilentlyContinue'
    $candidates = @()
    $launcher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($launcher) {
        $found = & $launcher.Source -3 -c 'import sys; print(sys.executable)' 2>$null
        if ($LASTEXITCODE -eq 0) { $candidates += $found }
    }
    foreach ($root in @('HKCU:\Software\Python\PythonCore', 'HKLM:\Software\Python\PythonCore')) {
        if (Test-Path $root) {
            foreach ($version in Get-ChildItem $root) {
                $key = Join-Path $version.PSPath 'InstallPath'
                if (Test-Path $key) {
                    $path = (Get-Item $key).GetValue('ExecutablePath')
                    if ($path) { $candidates += $path }
                }
            }
        }
    }
    $candidates += Join-Path $env:LOCALAPPDATA 'Programs\Python\Python314\python.exe'
    foreach ($candidate in $candidates | Select-Object -Unique) {
        if (Test-Path -LiteralPath $candidate) {
            & $candidate -c 'import sys, tkinter, venv, ensurepip; assert sys.version_info >= (3, 10)' 2>$null
            if ($LASTEXITCODE -eq 0) { return $candidate }
        }
    }
    return $null
}

try {
    $python = Find-Python
    if (-not $python) {
        Write-Host 'Downloading Python 3.14.7 from python.org...'
        $architecture = $env:PROCESSOR_ARCHITECTURE
        if ($env:PROCESSOR_ARCHITEW6432) { $architecture = $env:PROCESSOR_ARCHITEW6432 }
        switch ($architecture) {
            'ARM64' { $suffix = '-arm64'; $hash = '9a3fe120cc81bc2cb099550f794d8356811f96a86c7f438519243c3485db928d' }
            'AMD64' { $suffix = '-amd64'; $hash = '9d9eb2709ef81bf5cd30db3c2096bdbc4ea10087c22e62f27d356b36f6ae9649' }
            'x86' { $suffix = ''; $hash = '097fc03d4ac2de66ee1d73a0c5d2d323b5c0f14923f7207686ce93149a80f0a6' }
            default { throw "Unsupported Windows architecture: $architecture" }
        }
        $download = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString() + '.exe')
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -UseBasicParsing -Uri "https://www.python.org/ftp/python/3.14.7/python-3.14.7$suffix.exe" -OutFile $download
            if ((Get-FileHash -LiteralPath $download -Algorithm SHA256).Hash -ne $hash) {
                throw 'The Python download failed its SHA-256 integrity check.'
            }
            $signature = Get-AuthenticodeSignature -LiteralPath $download
            if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Python Software Foundation') {
                throw 'The Python installer signature could not be verified.'
            }
            Write-Host 'Installing Python for the current user...'
            $target = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python314'
            $options = '/quiet InstallAllUsers=0 Include_pip=1 Include_tcltk=1 Include_test=0 Include_launcher=0 PrependPath=0 Shortcuts=0 TargetDir="' + $target + '"'
            $process = Start-Process -FilePath $download -ArgumentList $options -PassThru -Wait
            if ($process.ExitCode -notin @(0, 3010)) { throw "Python installation failed (exit code $($process.ExitCode))." }
        } finally {
            Remove-Item -LiteralPath $download -Force -ErrorAction SilentlyContinue
        }
        $python = Find-Python
        if (-not $python) { throw 'Python is not ready. Restart Windows if requested, then run the installer again.' }
    }
    & $python (Join-Path $PSScriptRoot 'install.py') --desktop $DesktopShortcut
    if ($LASTEXITCODE -ne 0) { throw 'Application installation failed.' }
} catch {
    Write-Host ("Installation failed: " + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
