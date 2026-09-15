param(
    [Parameter(Mandatory=$true)][string]$Base,
    [ValidateSet('yes', 'no')][string]$DesktopShortcut = 'no'
)
$ErrorActionPreference = 'Stop'
$shell = New-Object -ComObject WScript.Shell
$app = Join-Path $Base 'app'
$python = Join-Path $Base 'environment\Scripts\pythonw.exe'
$programs = [Environment]::GetFolderPath('Programs')
$menu = Join-Path $programs 'Selector Moebius'
New-Item -ItemType Directory -Path $menu -Force | Out-Null

function New-AppShortcut([string]$destination) {
    $shortcut = $shell.CreateShortcut($destination)
    $shortcut.TargetPath = $python
    $shortcut.Arguments = '"' + (Join-Path $app 'Selector.py') + '"'
    $shortcut.WorkingDirectory = $app
    $shortcut.IconLocation = (Join-Path $app 'recursos\iconos\selector.ico') + ',0'
    $shortcut.Description = 'Choose students in rounds without repeats'
    $shortcut.Save()
}

New-AppShortcut (Join-Path $menu 'Selector Moebius.lnk')
if ($DesktopShortcut -eq 'yes') {
    $desktop = [Environment]::GetFolderPath('DesktopDirectory')
    New-Item -ItemType Directory -Path $desktop -Force | Out-Null
    New-AppShortcut (Join-Path $desktop 'Selector Moebius.lnk')
}
Write-Host 'Selector Moebius is registered in the Start menu.'
