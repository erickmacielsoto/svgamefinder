"""
Configuración y constantes de la aplicación
"""
import os
from pathlib import Path

# Archivo de configuración del usuario
CONFIG_FILE = Path.home() / ".consulta_juegos_xbox_config.json"

# Patrones de archivos JSON a cargar automáticamente
DEFAULT_JSON_GLOBS = ["*.json"]

def get_app_root() -> str:
    """Obtiene el directorio raíz de la aplicación (EXE o .py)"""
    import sys
    if getattr(sys, "frozen", False):
        # PyInstaller
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))



