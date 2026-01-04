"""
Utilidades generales: texto, formato, etc.
"""
import re
import unicodedata
import os
from datetime import datetime


def strip_accents(s: str) -> str:
    """Elimina acentos y caracteres especiales de un string"""
    if not isinstance(s, str):
        s = str(s or "")
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def norm_text(s: str) -> str:
    """Normaliza texto: elimina acentos, espacios múltiples, convierte a minúsculas"""
    return re.sub(r"\s+", " ", strip_accents(s)).strip().lower()


def guess_system_from_filename(path: str) -> str | None:
    """Intenta adivinar el sistema desde el nombre del archivo"""
    name = os.path.basename(path).lower()
    if "series" in name:
        return "Xbox Series"
    if re.search(r"\bone\b", name):
        return "Xbox One"
    if "360" in name:
        return "Xbox 360"
    if "classic" in name or "og" in name:
        return "Xbox (OG)"
    if "xbox" in name:
        return "Xbox (OG)"
    return None


def fmt_size(n: int) -> str:
    """Formatea un tamaño en bytes a formato legible (B, KB, MB, GB, TB)"""
    try:
        n = int(n)
    except Exception:
        return "-"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"


def fmt_mtime(ts: float) -> str:
    """Formatea un timestamp a formato legible"""
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "-"


