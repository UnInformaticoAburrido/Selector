"""Paletas y detección del tema del sistema sin bloquear el hilo de Tk."""
import re
import subprocess
import sys

CLARO = dict(fondo='#F0B7C9', superficie='#FFFFFF', texto='#000000', suave='#000080',
             principal='#D57896', sobre_principal='#000000', borde='#91445E',
             activo='#91445E', sobre_activo='#FFFFFF', seleccion='#000080',
             sobre_seleccion='#FFFFFF', visto='#78D5B7', sobre_visto='#000000')
OSCURO = dict(fondo='#19151D', superficie='#29232F', texto='#F8EEF3', suave='#F0B7C9',
              principal='#D57896', sobre_principal='#170E13', borde='#9D6F82',
              activo='#91445E', sobre_activo='#FFFFFF', seleccion='#91445E',
              sobre_seleccion='#FFFFFF', visto='#214E40', sobre_visto='#D5F8EB')


def detectar_tema_sistema():
    if sys.platform == 'win32':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize') as clave:
                valor, _ = winreg.QueryValueEx(clave, 'AppsUseLightTheme')
            return 'oscuro' if valor == 0 else 'claro'
        except OSError:
            return 'claro'
    if sys.platform.startswith('linux'):
        consultas = [
            ['gdbus', 'call', '--session', '--dest', 'org.freedesktop.portal.Desktop',
             '--object-path', '/org/freedesktop/portal/desktop', '--method',
             'org.freedesktop.portal.Settings.Read', 'org.freedesktop.appearance', 'color-scheme'],
            ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
            ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
        ]
        for comando in consultas:
            try:
                resultado = subprocess.run(comando, capture_output=True, text=True, timeout=0.7, check=False)
            except (OSError, subprocess.TimeoutExpired):
                continue
            if resultado.returncode:
                continue
            texto = resultado.stdout.casefold()
            valor = re.search(r'uint32\s+([12])\b', texto)
            if valor:
                return 'oscuro' if valor.group(1) == '1' else 'claro'
            if 'dark' in texto:
                return 'oscuro'
            if 'light' in texto:
                return 'claro'
    return 'claro'


def aplicar_estilos(root, tema, familia='DejaVu Sans', tamano=10):
    from tkinter import ttk
    p = OSCURO if tema == 'oscuro' else CLARO
    root.paleta = p
    root.configure(background=p['fondo'])
    estilo = ttk.Style(root)
    if estilo.theme_use() != 'clam':
        estilo.theme_use('clam')
    estilo.configure('.', background=p['fondo'], foreground=p['texto'],
                     bordercolor=p['borde'], lightcolor=p['superficie'], darkcolor=p['borde'],
                     font=(familia,tamano))
    estilo.configure('TFrame', background=p['fondo'])
    estilo.configure('TLabel', background=p['fondo'], foreground=p['texto'], font=(familia,tamano))
    estilo.configure('Titulo.TLabel', foreground=p['suave'], font=(familia,tamano+7,'bold'))
    estilo.configure('Suave.TLabel', foreground=p['suave'])
    estilo.configure('Tarjeta.TFrame', background=p['superficie'])
    estilo.configure('Tarjeta.TLabel', background=p['superficie'])
    estilo.configure('Resultado.TLabel', background=p['superficie'], foreground=p['suave'], font=(familia,tamano+7,'bold'))
    estilo.configure('TButton', background=p['superficie'], foreground=p['texto'], padding=(10,7), font=(familia,tamano))
    estilo.configure('TMenubutton', background=p['superficie'], foreground=p['texto'], padding=(8,6))
    for widget in ('TButton','TMenubutton'):
        estilo.map(widget, background=[('disabled',p['fondo']),('pressed',p['activo']),('active',p['activo'])],
                   foreground=[('disabled',p['borde']),('pressed',p['sobre_activo']),('active',p['sobre_activo'])])
    estilo.configure('Principal.TButton', background=p['principal'], foreground=p['sobre_principal'])
    estilo.configure('TEntry', fieldbackground=p['superficie'], foreground=p['texto'], insertcolor=p['texto'])
    estilo.map('TEntry', selectbackground=[('!disabled',p['seleccion'])], selectforeground=[('!disabled',p['sobre_seleccion'])])
    estilo.configure('Treeview', rowheight=max(30,tamano*2+10), font=(familia,tamano), background=p['superficie'],
                     fieldbackground=p['superficie'], foreground=p['texto'])
    estilo.map('Treeview', background=[('selected',p['seleccion'])], foreground=[('selected',p['sobre_seleccion'])])
    estilo.configure('Treeview.Heading', background=p['principal'], foreground=p['sobre_principal'], font=(familia,tamano,'bold'),padding=8)
    estilo.map('Treeview.Heading', background=[('active',p['activo'])], foreground=[('active',p['sobre_activo'])])
    estilo.configure('Vertical.TScrollbar', background=p['principal'], troughcolor=p['fondo'], arrowcolor=p['texto'])
    estilo.map('Vertical.TScrollbar', background=[('pressed',p['activo']),('active',p['principal'])])
    estilo.configure('Horizontal.TProgressbar', background='#78D5B7', troughcolor=p['superficie'])
    if hasattr(root,'menu_listas'):
        root.menu_listas.configure(background=p['superficie'], foreground=p['texto'],
                                  activebackground=p['activo'], activeforeground=p['sobre_activo'])
    if hasattr(root,'tabla'):
        root.tabla.tag_configure('visto', foreground=p['sobre_visto'], background=p['visto'])
