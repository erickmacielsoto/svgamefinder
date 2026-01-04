"""
Manejo de datos de juegos: carga de JSONs, índices, búsqueda
"""
import json
import os
import sys
import time
from pathlib import Path
from config import DEFAULT_JSON_GLOBS, get_app_root
from utils import norm_text, guess_system_from_filename


def normalize_item(raw: dict, default_system: str | None) -> dict | None:
    """Normaliza un item de juego desde el formato JSON"""
    if not isinstance(raw, dict):
        return None
    lower = {str(k).lower(): v for k, v in raw.items()}
    tid = lower.get("titleid") or lower.get("title_id") or lower.get("tid") or lower.get("id")
    if tid is None:
        return None
    if isinstance(tid, int):
        tid = f"{tid:08X}"
    tid = str(tid).strip().upper()
    if not tid:
        return None
    name = str(lower.get("title") or lower.get("name") or "").strip()
    sys_val = lower.get("system") or lower.get("platform") or lower.get("console") or lower.get("consola")
    if isinstance(sys_val, str):
        systems = [s.strip() for s in sys_val.split(",") if s.strip()]
    elif isinstance(sys_val, list):
        systems = [str(s).strip() for s in sys_val if str(s).strip()]
    else:
        systems = []
    system = systems[0] if systems else (default_system or "Desconocido")
    return {"title_id": tid, "name": name, "system": system}


# -------------------- Índices en memoria --------------------
_loaded_files: list[str] = []
_items_by_key: dict[tuple, dict] = {}
_index_tid: dict[str, list[dict]] = {}
_index_name: list[tuple[str, dict]] = []


def clear_db():
    """Limpia todos los datos cargados"""
    _loaded_files.clear()
    _items_by_key.clear()
    _index_tid.clear()
    _index_name.clear()


def add_items(items: list[dict]):
    """Agrega items al índice"""
    for it in items:
        key = (it["title_id"], it["system"])
        if key in _items_by_key:
            continue
        _items_by_key[key] = it
        _index_tid.setdefault(it["title_id"], []).append(it)
        _index_name.append((norm_text(it["name"]), it))


def load_json_file(path: str):
    """Carga un archivo JSON de juegos"""
    default_system = guess_system_from_filename(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    raw_items = data["items"] if isinstance(data, dict) and "items" in data else data
    if not isinstance(raw_items, list):
        raise ValueError("Formato JSON no soportado: se esperaba lista o {'items': [...]}.")

    add_items([it for it in (normalize_item(r, default_system) for r in raw_items) if it])
    _loaded_files.append(os.path.abspath(path))


def load_default_jsons():
    """Carga los JSONs por defecto desde la carpeta 'bd' y AppData"""
    loaded_count = 0
    
    # 1) Buscar en la carpeta 'bd' del directorio de la aplicación
    base = Path(get_app_root())
    bd_path = base / "bd"
    if bd_path.is_dir():
        for pat in DEFAULT_JSON_GLOBS:
            for fname in sorted(bd_path.glob(pat)):
                absf = os.path.abspath(str(fname))
                if absf in _loaded_files:
                    continue
                try:
                    load_json_file(absf)
                    loaded_count += 1
                    print(f"Cargado: {os.path.basename(absf)}")
                except Exception as e:
                    print(f"Error cargando {absf}: {e}")
    
    # 2) Buscar en AppData del usuario (C:\Users\<Usuario>\AppData)
    try:
        appdata_path = Path(os.environ.get('APPDATA', ''))
        if appdata_path and appdata_path.is_dir():
            search_paths = [
                appdata_path,  # C:\Users\<Usuario>\AppData\Roaming
                appdata_path.parent / "Local",  # C:\Users\<Usuario>\AppData\Local
                appdata_path.parent,  # C:\Users\<Usuario>\AppData
            ]
            
            start_time = time.time()
            max_search_time = 3.0  # Máximo 3 segundos buscando en AppData
            
            for search_path in search_paths:
                if time.time() - start_time > max_search_time:
                    print(f"Timeout: búsqueda en AppData interrumpida después de {max_search_time}s")
                    break
                    
                if not search_path.is_dir():
                    continue
                try:
                    items = os.listdir(str(search_path))
                    for item in items[:1000]:
                        if time.time() - start_time > max_search_time:
                            break
                        if not item.lower().endswith('.json'):
                            continue
                        fname = search_path / item
                        if not fname.is_file():
                            continue
                        absf = os.path.abspath(str(fname))
                        if absf in _loaded_files:
                            continue
                        try:
                            load_json_file(absf)
                            loaded_count += 1
                            print(f"Cargado desde AppData: {os.path.basename(absf)}")
                        except Exception as e:
                            print(f"Error cargando {absf}: {e}")
                except (PermissionError, OSError) as e:
                    print(f"No se puede acceder a {search_path}: {e}")
                    continue
                except Exception as e:
                    print(f"Error en {search_path}: {e}")
                    continue
    except Exception as e:
        print(f"Error buscando en AppData: {e}")
    
    if loaded_count > 0:
        print(f"Precargados {loaded_count} archivo(s) JSON")
    else:
        print("No se encontraron archivos JSON para precargar")


def summarize_by_system() -> str:
    """Resume los datos por sistema"""
    counts: dict[str, int] = {}
    for it in _items_by_key.values():
        counts[it["system"]] = counts.get(it["system"], 0) + 1
    parts = [f'{sys}: {n}' for sys, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
    return " | ".join(parts) if parts else "Sin datos"


def get_loaded_files_count() -> int:
    """Retorna el número de archivos JSON cargados"""
    return len(_loaded_files)


def get_items_count() -> int:
    """Retorna el número de items cargados"""
    return len(_items_by_key)


def search_by_tid(tid: str) -> list[dict]:
    """Busca juegos por Title ID"""
    tid = tid.strip().upper()
    return _index_tid.get(tid, [])


def search_by_name(query: str) -> list[dict]:
    """Busca juegos por nombre (búsqueda flexible)"""
    query_norm = norm_text(query)
    if not query_norm:
        return []
    
    results = []
    query_words = query_norm.split()
    
    for name_norm, item in _index_name:
        # Búsqueda flexible: todas las palabras deben estar presentes
        if all(word in name_norm for word in query_words):
            results.append(item)
    
    return results


def get_all_items() -> list[dict]:
    """Retorna todos los items cargados"""
    return list(_items_by_key.values())


# Funciones de acceso a índices internos (para compatibilidad con código existente)
def get_index_tid() -> dict[str, list[dict]]:
    """Retorna el índice por Title ID"""
    return _index_tid


def get_index_name() -> list[tuple[str, dict]]:
    """Retorna el índice por nombre"""
    return _index_name


def get_items_by_key() -> dict[tuple, dict]:
    """Retorna el diccionario de items por clave"""
    return _items_by_key

