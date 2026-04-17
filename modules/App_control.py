"""
App_control.py - Contole de aplicativos no linux
Abre, fecha e gerencia apps via subprocess + xdg-open.
Detecta automaticamente o que está instalado.
"""

import subprocess
import shutil
import os
from dataclasses import dataclass

APP_CATALOG: dict[str, dict] = {
    "browser": {
        "aliases": ["browser", "navegador", "internet", "web"],
        "candidates": ["firefox", "google-chrome", "chromium", "chromium-browser", "brave-browser", "opera"],
        "label": "navegador",
    },

    "brave": {
        "aliases": ["brave", "brave browser"],
        "candidates": ["brave-browser"],
        "label": "Brave",
    },
    "firefox": {
        "aliases": ["firefox"],
        "candidates": ["firefox"],
        "label": "Firefox",
    },
    "chrome": {
        "aliases": ["chrome", "google chrome", "chromium"],
        "candidates": ["google-chrome", "chromium", "chromium-browser"],
        "label": "Chrome/Chromium",
    },
 
    "terminal": {
        "aliases": ["terminal", "console", "bash", "shell", "linha de comando"],
        "candidates": [
            "gnome-terminal", "konsole", "xfce4-terminal", "xterm",
            "alacritty", "kitty", "tilix", "terminator", "mate-terminal",
        ],
        "label": "terminal",
    },
 
    "vscode": {
        "aliases": ["vs code", "vscode", "visual studio code", "code", "editor", "código"],
        "candidates": ["code", "code-oss", "codium", "vscodium"],
        "label": "VS Code",
    },
 
    "files": {
        "aliases": [
            "gerenciador de arquivos", "arquivos", "explorador", "file manager",
            "nautilus", "dolphin", "thunar", "nemo",
        ],
        "candidates": ["nautilus", "dolphin", "thunar", "nemo", "pcmanfm", "caja", "xdg-open ."],
        "label": "gerenciador de arquivos",
    },
}

def _which(cmd: str) -> str | None:
    binary = cmd.split()[0]
    return shutil.which(binary)

def _resolve_app(app_key: str) -> tuple[str, str] | None:
    entry = APP_CATALOG.get(app_key)

    if not entry:
        return None
    
    for candidate in entry["candidates"]:
        if _which(candidate):
            return candidate, entry["label"]
    return None

def _match_app_key(text: str) -> str | None:
    text_lower = text.lower()

    for key, entry in APP_CATALOG.items():
        for alias in entry["aliases"]:
            if alias in text_lower:
                return key
    return None

def open_app(nome_app: str) -> str:
    key = _match_app_key(nome_app)

    if not key:
        return f"Não reconheci o aplicativo '{nome_app}'. Aplicativos disponíveis {list_available()}"
    
    resolved = _resolve_app(key)

    if not resolved:
        label = APP_CATALOG[key]["label"]
        return f"{label} não está instalado nesse sistema"
    
    cmd, label = resolved

    try:
        subprocess.Popen(
            cmd.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        return f"{label} aberto com sucesso"
    except Exception as e:
        return f"Erro ao abrir {label}: {e}"
    
def open_path(path: str) -> str:
    expanded = os.path.expanduser(path)

    if not os.path.exists(expanded):
        return f"Caminho não encontrado: {expanded}"
    
    try:
        subprocess.Popen(
            ["xdg-open", expanded],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return f"Abrindo: {expanded}"
    except Exception as e:
        return f"Erro ao abrir {expanded}: {e}"

def open_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        subprocess.Popen(
            ["xdg-open", url],
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL,
            start_new_session = True
        )

        return f"Abrindo no navegador: {url}"
    except Exception as e:
        return f"Erro ao abrir {url}: {e}"

def open_terminal_with_command(command: str = "") -> str:
    terminals_with_exec = {
        "gnome-terminal": ["gnome-terminal", "--", "bash", "-c", f"{command}; exec bash"],
        "konsole":        ["konsole", "-e", "bash", "-c", f"{command}; exec bash"],
        "xfce4-terminal": ["xfce4-terminal", "-e", f"bash -c '{command}; exec bash'"],
        "xterm":          ["xterm", "-e", f"bash -c '{command}; exec bash'"],
        "alacritty":      ["alacritty", "-e", "bash", "-c", f"{command}; exec bash"],
        "kitty":          ["kitty", "bash", "-c", f"{command}; exec bash"],
        "tilix":          ["tilix", "-e", f"bash -c '{command}; exec bash'"],
    }

    for term, full_cmd in terminals_with_exec.items():
        if _which(term):
            try:
                if command:
                    subprocess.Popen(
                        full_cmd,
                        stdout = subprocess.DEVNULL,
                        stderr = subprocess.DEVNULL,
                        start_new_session = True
                    )
                    return f"Terminal aberto executando: {command}"
                else:
                    subprocess.Popen(
                        [term],
                        stdout = subprocess.DEVNULL,
                        stderr = subprocess.DEVNULL,
                        start_new_session = True
                    )
                    return "Terminal aberto."
            except Exception as e:
                return f"Erro ao abrir o terminal: {e}"
            
    return "Nenhum terminal compativel encontrado"

def close_app(app_name: str) -> str:
    key = _match_app_key(app_name)
    resolved = _resolve_app(key) if key else None
    process_name = resolved[0].split()[0] if resolved else app_name.lower().split()[0]

    try:
        resulted = subprocess.run(
            ["pkill", "-f", process_name],
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL,
            start_new_session = True
        )

        if resulted.returncode == 0:
            return f"Aplicativo '{process_name}' fechado."
        else:
            return f"Nenhum processo '{process_name}' encontrado em execução."
        
    except Exception as e:
        return f"Erro ao fechar {process_name}: {e}"
    
def list_available() -> str:
    available = []

    for key, entry in APP_CATALOG.items():
        if _resolve_app(key):
            available.append(entry["label"])
    
    if available:
        return ", ".join(sorted(set(available)))
    
    return "Nenhum app do catálogo encontrado"

def list_running() -> str:
    running = []

    for key, entry in APP_CATALOG.items():
        resolved = _resolve_app(key)

        if not resolved:
            continue

        cmd = resolved[0].split()[0]

        result = subprocess.run(
            ["pgrep", "-x", cmd],
            capture_output = True,
        )

        if result.returncode == 0:
            running.append(entry["label"])

    if running:
        return f"Rodando agora:" + ", ".join(sorted(set(running)))
    
    return "Nenhum app monitorado em execução."