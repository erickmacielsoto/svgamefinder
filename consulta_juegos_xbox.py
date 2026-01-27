# consulta_juegos_xbox.py
# SVXboxGamesFinder (Local) - By: @erickmacielsoto - Reviewed by: @jasontorresb

import customtkinter as ctk
from tkinter import ttk, messagebox, Menu, filedialog
import re
import locale
import json
import os
import sys
HAVE_WIN32_SHELL = False
WIN32_SHELL_IMPORT_ERROR = None

if sys.platform.startswith("win"):
    try:
        # Import correcto (no basta "import win32com")
        from win32com.shell import shell as _SHELL, shellcon as _SHELLCON
        HAVE_WIN32_SHELL = True
    except Exception as _e:
        WIN32_SHELL_IMPORT_ERROR = _e

# (Opcional, ayuda a PyInstaller cuando está empacado)
if getattr(sys, "frozen", False) and sys.platform.startswith("win"):
    try:
        import win32com  # noqa
        from win32com.shell import shell as _SHELL, shellcon as _SHELLCON  # noqa
        import pythoncom, pywintypes  # noqa
        HAVE_WIN32_SHELL = True
    except Exception as _e:
        WIN32_SHELL_IMPORT_ERROR = _e
import subprocess
import unicodedata
from pathlib import Path
import shutil
import threading
import time
from datetime import datetime


# -------------------- Config --------------------
CONFIG_FILE = Path.home() / ".consulta_juegos_xbox_config.json"
ctk.set_default_color_theme("blue")
DEFAULT_JSON_GLOBS = ["*.json"]  # json(s) locales que se cargan automáticamente

# -------------------- Traducciones --------------------
traducciones = {
    "es": {
        "modo_oscuro": "Modo Oscuro",
        "solo_marcados": "Solo marcados",
        "idioma": "Idioma",
        "title_ids": "Title IDs (Local)",
        "ingresa_texto": "Ingresa Title ID o Nombre del juego:",
        "buscar": "Buscar",
        "error": "Error",
        "info": "Información",
        "error_busqueda": "Ocurrió un error durante la búsqueda.",
        "no_results_found": "No se encontraron resultados.",
        "col_title_id": "Title ID",
        "col_name": "Nombre",
        "col_system": "Consola",
        "copiar_celda": "Copiar celda",
        "copiar_fila": "Copiar fila",
        "cargando": "Cargando...",
        "busqueda_completada": "Búsqueda completada.",
        "cargar_json": "Cargar .json",
        "limpiar_db": "Limpiar .json",
        "resumen_db": "Archivos: {files}  |  Registros: {rows}  |  {by_system}",
        "agregar_carpeta": "Agregar carpeta",
        "ver_carpetas": "Ver carpetas",
        "carpetas_agregadas": "Carpetas agregadas",
        "carpetas_agregadas_desc": "Carpetas indexadas ({total}):",
        "ninguna_carpeta_agregada": "No hay carpetas agregadas",
        "eliminar": "Eliminar",
        "carpeta_eliminada": "Carpeta eliminada",
        "abrir_carpeta": "Abrir carpeta",
        "ver_archivos": "Ver archivos…",
        "copiar_a": "Copiar a…",
        "carpeta_indexada": "Carpeta indexada.",
        "indexando_carpeta": "Indexando carpeta",
        "escaneando_carpeta": "Escaneando",
        "procesando_lista": "Procesando lista",
        "copiando": "Copiando...",
        "copia_completada": "Copia completada.",
        "error_copiar": "Error al copiar",
        "no_carpeta_tid": "No se encontró carpeta para ese Title ID.\nAgrega una 'carpeta origen' y reintenta.",
        "elige_carpeta_juego": "Selecciona la carpeta del juego",
        "elige_destino": "Selecciona la carpeta de destino",
        "ok": "OK",
        "cancelar": "Cancelar",
        "cerrar": "Cerrar",
        "copia_cancelada": "Copia cancelada.",
        # Explorador
        "explorador": "Explorador de archivos",
        "ruta": "Ruta:",
        "abrir_explorer": "Abrir en Explorer",
        "subir": "Subir nivel",
        "cambiar_carpeta": "Cambiar…",
        "copiar_seleccion": "Copiar selección",
        "copiar_marcados": "Copiar marcados",
        "eliminar_marcados": "Eliminar marcados",
        "eliminar_marcados_tooltip": "Elimina permanentemente los elementos marcados",
        "eliminar_marcados_confirmacion": "¿Estás seguro de que deseas eliminar {count} elemento(s) marcado(s)?\n\nEsta acción no se puede deshacer.",
        "eliminando": "Eliminando...",
        "eliminacion_completada": "Eliminación completada",
        "eliminacion_error": "Error al eliminar",
        "elementos_eliminados": "{count} elemento(s) eliminado(s) correctamente",
        "elementos_fallidos": "{count} elemento(s) no se pudieron eliminar",
        "seleccionar_todo": "Seleccionar todo",
        "nombre": "Nombre",
        "tipo": "Tipo",
        "tamano": "Tamaño",
        "modificado": "Modificado",
        "mostrar_en_explorer": "Mostrar en Explorer",
        "abrir": "Abrir",
        # Filtro
        "filtro_placeholder": "Filtrar por nombre, tipo o ruta…",
        "aplicar_filtro": "Buscar",
        "limpiar_filtro": "Limpiar",
        # Navegación
        "atras": "Atrás",
        "adelante": "Adelante",
        "calculando": "Calculando…",
        # Checkboxes
        "col_sel": "✔",
        "marcar_visibles": "Marcar visibles",
        "desmarcar_visibles": "Desmarcar visibles",
        "limpiar_seleccion": "Limpiar selección",
        "ninguno_marcado": "No hay elementos marcados.",
        "minimizar": "Minimizar",
        # Contador
        "seleccionados": "Seleccionados",
        "marcados": "Marcados",
        # Generar lista y comparar
        "generar_lista_marcados": "Generar lista marcados",
        "generar_lista_marcados_tooltip": "Genera una lista de nombres de juegos marcados separados por comas",
        "lista_marcados_titulo": "Lista de juegos marcados",
        "lista_marcados_desc": "Juegos marcados ({total}):",
        "copiar_lista": "Copiar lista",
        "lista_copiada": "Lista copiada al portapapeles",
        "comparar_listas": "Comparar con lista original",
        "comparar_listas_titulo": "Comparar listas",
        "comparar_listas_desc": "Pega tu lista original para comparar:",
        "comparar": "Comparar",
        "coincidencias": "Coincidencias",
        "faltantes": "Faltantes",
        "sobrantes": "Sobrantes",
        "coincidencias_desc": "Juegos encontrados en ambas listas ({total}):",
        "faltantes_desc": "Juegos en tu lista original pero no marcados ({total}):",
        "sobrantes_desc": "Juegos marcados pero no en tu lista original ({total}):",
        # Comparar ubicación destino
        "comparar_ubicacion": "Comparar ubicación destino",
        "comparar_ubicacion_tooltip": "Compara los juegos en una ubicación destino con la lista cargada",
        "seleccionar_ubicacion_destino": "Selecciona la carpeta de destino a comparar",
        "comparando_ubicacion": "Comparando ubicación...",
        "comparacion_completada": "Comparación completada",
        "juegos_encontrados_destino": "Juegos encontrados en destino: {count}",
        "juegos_faltantes": "Juegos faltantes: {count}",
        "juegos_diferencia_tamano": "Juegos con diferencia de tamaño: {count}",
        "marcando_faltantes": "Marcando faltantes y con diferencias de tamaño...",
        # Log de transferencias
        "log_transferencias": "Log de transferencias",
        "log_transferencias_tooltip": "Ver y gestionar el log de archivos copiados",
        "restaurar_desde_log": "Restaurar desde log",
        "restaurar_desde_log_tooltip": "Elimina los archivos que se copiaron según el log",
        "continuar_desde_log": "Continuar desde log",
        "continuar_desde_log_tooltip": "Marca solo los archivos que faltan según el log",
        "log_vacio": "No hay log de transferencias disponible",
        "log_restaurado": "Log restaurado: {deleted} elementos eliminados",
        "log_continuado": "Continuando desde log: {count} elementos marcados",
        "guardando_log": "Guardando log de transferencia...",
        "log_guardado": "Log guardado en: {path}",
        "sin_coincidencias": "No hay coincidencias",
        "sin_faltantes": "No hay faltantes",
        "sin_sobrantes": "No hay sobrantes",
        # Archivo actual
        "archivo": "Archivo",
        # Método de copia
        "metodo_copia": "Método de copia",
        "auto_explorer": "Auto (Explorer si hay)",
        "explorer_forzar": "Explorer (forzar)",
        "interno": "Interno (propio)",
        # Ordenamiento
        "ordenar_por": "Ordenar por:",
        "orden_nombre": "Nombre",
        "orden_tamano": "Tamaño",
        "orden_tipo": "Tipo",
        "orden_modificado": "Modificado",
    },
    "en": {
        "modo_oscuro": "Dark Mode",
        "solo_marcados": "Only marked",
        "idioma": "Language",
        "title_ids": "Title IDs (Local)",
        "ingresa_texto": "Enter Title ID or Game Name:",
        "buscar": "Search",
        "error": "Error",
        "info": "Info",
        "error_busqueda": "An error occurred during the search.",
        "no_results_found": "No results found.",
        "col_title_id": "Title ID",
        "col_name": "Name",
        "col_system": "Console",
        "copiar_celda": "Copy Cell",
        "copiar_fila": "Copy Row",
        "cargando": "Loading...",
        "busqueda_completada": "Search completed.",
        "cargar_json": "Load .json",
        "limpiar_db": "Clear .json",
        "resumen_db": "Files: {files}  |  Rows: {rows}  |  {by_system}",
        "agregar_carpeta": "Add folder",
        "ver_carpetas": "View folders",
        "carpetas_agregadas": "Added folders",
        "carpetas_agregadas_desc": "Indexed folders ({total}):",
        "ninguna_carpeta_agregada": "No folders added",
        "eliminar": "Delete",
        "carpeta_eliminada": "Folder deleted",
        "abrir_carpeta": "Open folder",
        "ver_archivos": "Browse files…",
        "copiar_a": "Copy to…",
        "carpeta_indexada": "Folder indexed.",
        "indexando_carpeta": "Indexing folder",
        "escaneando_carpeta": "Scanning",
        "procesando_lista": "Processing list",
        "copiando": "Copying...",
        "copia_completada": "Copy completed.",
        "error_copiar": "Copy error",
        "no_carpeta_tid": "No folder found for that Title ID.\nAdd a 'source folder' and try again.",
        "elige_carpeta_juego": "Choose the game folder",
        "elige_destino": "Choose destination folder",
        "ok": "OK",
        "cancelar": "Cancel",
        "cerrar": "Close",
        "copia_cancelada": "Copy canceled.",
        "explorador": "File explorer",
        "ruta": "Path:",
        "abrir_explorer": "Open in Explorer",
        "subir": "Up",
        "cambiar_carpeta": "Change…",
        "copiar_seleccion": "Copy selection",
        "copiar_marcados": "Copy checked",
        "eliminar_marcados": "Delete checked",
        "eliminar_marcados_tooltip": "Permanently deletes the checked items",
        "eliminar_marcados_confirmacion": "Are you sure you want to delete {count} checked item(s)?\n\nThis action cannot be undone.",
        "eliminando": "Deleting...",
        "eliminacion_completada": "Deletion completed",
        "eliminacion_error": "Deletion error",
        "elementos_eliminados": "{count} item(s) deleted successfully",
        "elementos_fallidos": "{count} item(s) could not be deleted",
        "seleccionar_todo": "Select all",
        "nombre": "Name",
        "tipo": "Type",
        "tamano": "Size",
        "modificado": "Modified",
        "mostrar_en_explorer": "Show in Explorer",
        "abrir": "Open",
        "filtro_placeholder": "Filter by name, type or path…",
        "aplicar_filtro": "Search",
        "limpiar_filtro": "Clear",
        "atras": "Back",
        "adelante": "Forward",
        "calculando": "Calculating…",
        "col_sel": "✔",
        "marcar_visibles": "Check visible",
        "desmarcar_visibles": "Uncheck visible",
        "limpiar_seleccion": "Clear selection",
        "ninguno_marcado": "No items checked.",
        "minimizar": "Minimize",
        "seleccionados": "Selected",
        "marcados": "Checked",
        # Generar lista y comparar
        "generar_lista_marcados": "Generate marked list",
        "generar_lista_marcados_tooltip": "Generates a comma-separated list of marked game names",
        "lista_marcados_titulo": "Marked games list",
        "lista_marcados_desc": "Marked games ({total}):",
        "copiar_lista": "Copy list",
        "lista_copiada": "List copied to clipboard",
        "comparar_listas": "Compare with original list",
        "comparar_listas_titulo": "Compare lists",
        "comparar_listas_desc": "Paste your original list to compare:",
        "comparar": "Compare",
        "coincidencias": "Matches",
        "faltantes": "Missing",
        "sobrantes": "Extra",
        "coincidencias_desc": "Games found in both lists ({total}):",
        "faltantes_desc": "Games in your original list but not marked ({total}):",
        "sobrantes_desc": "Games marked but not in your original list ({total}):",
        "sin_coincidencias": "No matches",
        "sin_faltantes": "No missing games",
        "sin_sobrantes": "No extra games",
        "archivo": "File",
        "metodo_copia": "Copy method",
        "auto_explorer": "Auto (Explorer if available)",
        "explorer_forzar": "Explorer (force)",
        "interno": "Internal (built-in)",
        # Ordenamiento
        "ordenar_por": "Sort by:",
        "orden_nombre": "Name",
        "orden_tamano": "Size",
        "orden_tipo": "Type",
        "orden_modificado": "Modified",
    },
    "pt": {
        "modo_oscuro": "Modo Escuro",
        "solo_marcados": "Apenas marcados",
        "idioma": "Idioma",
        "title_ids": "Title IDs (Local)",
        "ingresa_texto": "Digite Title ID ou nome do jogo:",
        "buscar": "Buscar",
        "error": "Erro",
        "info": "Informação",
        "error_busqueda": "Ocorreu um erro durante a pesquisa.",
        "no_results_found": "Nenhum resultado encontrado.",
        "col_title_id": "Title ID",
        "col_name": "Nome",
        "col_system": "Console",
        "copiar_celda": "Copiar célula",
        "copiar_fila": "Copiar linha",
        "cargando": "Carregando...",
        "busqueda_completada": "Pesquisa concluída.",
        "cargar_json": "Carregar .json",
        "limpiar_db": "Limpar .json",
        "resumen_db": "Arquivos: {files}  |  Registros: {rows}  |  {by_system}",
        "agregar_carpeta": "Adicionar pasta",
        "ver_carpetas": "Ver pastas",
        "carpetas_agregadas": "Pastas adicionadas",
        "carpetas_agregadas_desc": "Pastas indexadas ({total}):",
        "ninguna_carpeta_agregada": "Nenhuma pasta adicionada",
        "eliminar": "Excluir",
        "carpeta_eliminada": "Pasta excluída",
        "abrir_carpeta": "Abrir pasta",
        "ver_archivos": "Ver arquivos…",
        "copiar_a": "Copiar para…",
        "carpeta_indexada": "Pasta indexada.",
        "indexando_carpeta": "Indexando pasta",
        "escaneando_carpeta": "Escaneando",
        "procesando_lista": "Processando lista",
        "copiando": "Copiando...",
        "copia_completada": "Cópia concluída.",
        "error_copiar": "Erro ao copiar",
        "no_carpeta_tid": "Nenhuma pasta encontrada para esse Title ID.\nAdicione uma 'pasta de origem' e tente novamente.",
        "elige_carpeta_juego": "Escolha a pasta do jogo",
        "elige_destino": "Escolha a pasta de destino",
        "ok": "OK",
        "cancelar": "Cancelar",
        "cerrar": "Fechar",
        "copia_cancelada": "Cópia cancelada.",
        "explorador": "Explorador de arquivos",
        "ruta": "Caminho:",
        "abrir_explorer": "Abrir no Explorer",
        "subir": "Subir",
        "cambiar_carpeta": "Alterar…",
        "copiar_seleccion": "Copiar seleção",
        "copiar_marcados": "Copiar marcados",
        "eliminar_marcados": "Excluir marcados",
        "eliminar_marcados_tooltip": "Exclui permanentemente os itens marcados",
        "eliminar_marcados_confirmacion": "Tem certeza de que deseja excluir {count} item(ns) marcado(s)?\n\nEsta ação não pode ser desfeita.",
        "eliminando": "Excluindo...",
        "eliminacion_completada": "Exclusão concluída",
        "eliminacion_error": "Erro ao excluir",
        "elementos_eliminados": "{count} item(ns) excluído(s) com sucesso",
        "elementos_fallidos": "{count} item(ns) não puderam ser excluídos",
        "seleccionar_todo": "Selecionar tudo",
        "nombre": "Nome",
        "tipo": "Tipo",
        "tamano": "Tamanho",
        "modificado": "Modificado",
        "mostrar_en_explorer": "Mostrar no Explorer",
        "abrir": "Abrir",
        "filtro_placeholder": "Filtrar por nome, tipo ou caminho…",
        "aplicar_filtro": "Buscar",
        "limpiar_filtro": "Limpar",
        "atras": "Voltar",
        "adelante": "Avançar",
        "calculando": "Calculando…",
        "col_sel": "✔",
        "marcar_visibles": "Marcar visíveis",
        "desmarcar_visibles": "Desmarcar visíveis",
        "limpiar_seleccion": "Limpar seleção",
        "ninguno_marcado": "Nenhum item marcado.",
        "minimizar": "Minimizar",
        "seleccionados": "Selecionados",
        "marcados": "Marcados",
        # Generar lista y comparar
        "generar_lista_marcados": "Gerar lista marcados",
        "generar_lista_marcados_tooltip": "Gera uma lista de nomes de jogos marcados separados por vírgulas",
        "lista_marcados_titulo": "Lista de jogos marcados",
        "lista_marcados_desc": "Jogos marcados ({total}):",
        "copiar_lista": "Copiar lista",
        "lista_copiada": "Lista copiada para a área de transferência",
        "comparar_listas": "Comparar com lista original",
        "comparar_listas_titulo": "Comparar listas",
        "comparar_listas_desc": "Cole sua lista original para comparar:",
        "comparar": "Comparar",
        "coincidencias": "Correspondências",
        "faltantes": "Faltantes",
        "sobrantes": "Extras",
        "coincidencias_desc": "Jogos encontrados em ambas as listas ({total}):",
        "faltantes_desc": "Jogos na sua lista original mas não marcados ({total}):",
        "sobrantes_desc": "Jogos marcados mas não na sua lista original ({total}):",
        "sin_coincidencias": "Sem correspondências",
        "sin_faltantes": "Sem jogos faltantes",
        "sin_sobrantes": "Sem jogos extras",
        "archivo": "Arquivo",
        "metodo_copia": "Método de cópia",
        "auto_explorer": "Auto (Explorer se houver)",
        "explorer_forzar": "Explorer (forçar)",
        "interno": "Interno",
        # Ordenamiento
        "ordenar_por": "Ordenar por:",
        "orden_nombre": "Nome",
        "orden_tamano": "Tamanho",
        "orden_tipo": "Tipo",
        "orden_modificado": "Modificado",
    }
}

# -------------------- Utilidades de texto --------------------
def strip_accents(s: str) -> str:
    if not isinstance(s, str):
        s = str(s or "")
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))

def norm_text(s: str) -> str:
    return re.sub(r"\s+", " ", strip_accents(s)).strip().lower()

def guess_system_from_filename(path: str) -> str | None:
    name = os.path.basename(path).lower()
    if "series" in name: return "Xbox Series"
    if re.search(r"\bone\b", name): return "Xbox One"
    if "360" in name: return "Xbox 360"
    if "classic" in name or "og" in name: return "Xbox (OG)"
    if "xbox" in name: return "Xbox (OG)"
    return None

def normalize_item(raw: dict, default_system: str | None) -> dict | None:
    if not isinstance(raw, dict): return None
    lower = {str(k).lower(): v for k, v in raw.items()}
    tid = lower.get("titleid") or lower.get("title_id") or lower.get("tid") or lower.get("id")
    if tid is None: return None
    if isinstance(tid, int): tid = f"{tid:08X}"
    tid = str(tid).strip().upper()
    if not tid: return None
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

def _app_root() -> str:
    # Directorio del programa (EXE o .py)
    if getattr(sys, "frozen", False):
        # PyInstaller
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def clear_db():
    _loaded_files.clear(); _items_by_key.clear(); _index_tid.clear(); _index_name.clear()

def add_items(items: list[dict]):
    for it in items:
        key = (it["title_id"], it["system"])
        if key in _items_by_key: continue
        _items_by_key[key] = it
        _index_tid.setdefault(it["title_id"], []).append(it)
        _index_name.append((norm_text(it["name"]), it))

def load_json_file(path: str):
    default_system = guess_system_from_filename(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    raw_items = data["items"] if isinstance(data, dict) and "items" in data else data
    if not isinstance(raw_items, list):
        raise ValueError("Formato JSON no soportado: se esperaba lista o {'items': [...]}.")

    add_items([it for it in (normalize_item(r, default_system) for r in raw_items) if it])
    _loaded_files.append(os.path.abspath(path))

def load_default_jsons():
    loaded_count = 0
    
    # 1) Buscar en la carpeta 'bd' del directorio de la aplicación
    base = Path(_app_root())
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
    # Optimizado: solo buscar en el nivel raíz de cada carpeta para evitar escanear miles de archivos
    # Con límite de tiempo para no bloquear la aplicación
    try:
        appdata_path = Path(os.environ.get('APPDATA', ''))
        if appdata_path and appdata_path.is_dir():
            # Buscar JSONs directamente en AppData y en subcarpetas comunes
            # Solo en el nivel raíz para evitar escanear recursivamente
            search_paths = [
                appdata_path,  # C:\Users\<Usuario>\AppData\Roaming
                appdata_path.parent / "Local",  # C:\Users\<Usuario>\AppData\Local
                appdata_path.parent,  # C:\Users\<Usuario>\AppData
            ]
            
            start_time = time.time()
            max_search_time = 3.0  # Máximo 3 segundos buscando en AppData
            
            for search_path in search_paths:
                # Verificar timeout
                if time.time() - start_time > max_search_time:
                    print(f"Timeout: búsqueda en AppData interrumpida después de {max_search_time}s")
                    break
                    
                if not search_path.is_dir():
                    continue
                try:
                    # Usar os.listdir con try/except para manejar errores rápidamente
                    items = os.listdir(str(search_path))
                    # Limitar a los primeros 1000 archivos para no tardar mucho
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
                    # Ignorar errores de permisos o acceso
                    print(f"No se puede acceder a {search_path}: {e}")
                    continue
                except Exception as e:
                    # Cualquier otro error, continuar
                    print(f"Error en {search_path}: {e}")
                    continue
    except Exception as e:
        print(f"Error buscando en AppData: {e}")
    
    if loaded_count > 0:
        print(f"Precargados {loaded_count} archivo(s) JSON")
    else:
        print("No se encontraron archivos JSON para precargar")


def summarize_by_system() -> str:
    counts: dict[str, int] = {}
    for it in _items_by_key.values():
        counts[it["system"]] = counts.get(it["system"], 0) + 1
    parts = [f'{sys}: {n}' for sys, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
    return " | ".join(parts) if parts else "Sin datos"

# -------------------- Helpers del explorador --------------------
def fmt_size(n: int) -> str:
    try: n = int(n)
    except Exception: return "-"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"

def fmt_mtime(ts: float) -> str:
    try: return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except Exception: return "-"

# -------------------- App --------------------
class XboxGameLookupApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        icon_path = os.path.abspath("icon.ico")
        if os.path.exists(icon_path):
            try: self.iconbitmap(icon_path)
            except Exception: pass

        self.geometry("1200x880")

        # Preferencias
        self.idioma_actual = self._detectar_idioma_sistema()
        self.modo_oscuro_inicial = self._detectar_modo_oscuro_sistema()
        self.solo_marcados_inicial = False  # Por defecto mostrar todos
        self.copy_method = "explorer"  # "auto" | "explorer" | "internal"
        self.nombre_cliente = ""  # Nombre del cliente personalizable
        self._cargar_config()
        self._actualizar_titulo()
        self._aplicar_estilo_treeview("dark" if self.modo_oscuro_inicial else "light")
        ctk.set_appearance_mode("dark" if self.modo_oscuro_inicial else "light")
        
        # Inicializar variables antes de crear la UI (para evitar AttributeError)
        self._checked_paths = set()
        self._last_checked_paths_for_size = set()
        self._marked_size_thread = None
        self._marked_size_stop = threading.Event()
        self.original_game_names = []  # Lista original de nombres de juegos cargados
        
        # Cargar iconos (si existen)
        self._load_icons()

        # UI
        self._setup_ui()
        self._update_ui_texts()
        # Aplicar iconos a los botones después de crear la UI
        self._apply_icons_to_buttons()
        
        # Configurar ajuste responsivo de botones
        self.bind("<Configure>", self._on_window_resize)
        self._resize_job = None
        
        # Mostrar indicador de carga
        self.status_label.configure(text="Cargando datos...", text_color="orange")
        self.update_idletasks()
        
        # Cargar datos en un hilo para no bloquear la UI
        def load_data():
            try:
                # Cargar JSONs (esto puede tardar si hay muchos archivos en AppData)
                load_default_jsons()
                
                # Escanear raíces en segundo plano (no bloquea la UI)
                # Esto se hace en segundo plano, no esperamos a que termine
                if hasattr(self, "_scan_roots") and self._scan_roots:
                    def scan_roots_background():
                        try:
                            # Solo hay una carpeta indexada ahora
                            r = self._scan_roots[0]
                            if os.path.isdir(r): 
                                self._scan_root(r)
                            else:
                                try: self._scan_roots.remove(r)
                                except ValueError: pass
                        except Exception as e:
                            print(f"Error escaneando raíz: {e}")
                    # Escanear en otro hilo para no bloquear
                    threading.Thread(target=scan_roots_background, daemon=True).start()
                
                # Actualizar UI en el hilo principal - SIEMPRE actualizar
                self.after(0, lambda: (
                    self._update_db_summary(),
                    self.status_label.configure(text="Carga completada", text_color="green"),
                    self.after(2000, lambda: self.status_label.configure(text="", text_color="gray"))
                ))
            except Exception as e:
                import traceback
                error_msg = f"Error al cargar: {e}\n{traceback.format_exc()}"
                print(error_msg)
                # Asegurarse de actualizar el mensaje incluso si hay error
                self.after(0, lambda: (
                    self._update_db_summary(),
                    self.status_label.configure(text=f"Carga completada (con advertencias)", text_color="orange"),
                    self.after(2000, lambda: self.status_label.configure(text="", text_color="gray"))
                ))
        
        # Iniciar el hilo de carga
        load_thread = threading.Thread(target=load_data, daemon=True)
        load_thread.start()
        
        # Timeout de seguridad: si después de 10 segundos no se actualiza, forzar actualización
        def timeout_check():
            time.sleep(10)
            if self.status_label.cget("text") == "Cargando datos...":
                self.after(0, lambda: (
                    self._update_db_summary(),
                    self.status_label.configure(text="Carga completada", text_color="green"),
                    self.after(2000, lambda: self.status_label.configure(text="", text_color="gray"))
                ))
        threading.Thread(target=timeout_check, daemon=True).start()
        
        # Ajustar tamaños iniciales después de que la ventana se renderice
        self.after(100, self._adjust_button_sizes)

        # Navegación + tamaños + checks
        self._nav_history = []
        self._nav_index = -1
        self._folder_size_cache = {}
        self._size_thread = None
        self._size_thread_stop = threading.Event()
        self._files_row_by_path = {}
        self._current_entries = []
        self._filter_job = None
        self._sort_order = "nombre"  # "nombre", "tamano", "tipo", "modificado"
        # _checked_paths ya se inicializó antes de _setup_ui()
        self._user_changed_folder = False  # Rastrea si el usuario cambió manualmente la carpeta

        self._update_nav_buttons()

    def _load_icons(self):
        """Carga los iconos desde la carpeta 'icons' si existen"""
        try:
            from PIL import Image, ImageTk
        except ImportError:
            print("PIL/Pillow no está instalado. Los iconos no se cargarán.")
            self.icons = {}
            return
        
        self.icons = {}
        icons_dir = Path(_app_root()) / "icons"
        
        if not icons_dir.exists():
            # Crear carpeta de ejemplo si no existe
            icons_dir.mkdir(exist_ok=True)
            return
        
        # Mapeo de nombres de iconos a sus archivos
        icon_mapping = {
            # Botones superiores
            'limpiar_lista': 'trash.png',
            'pegar_lista': 'clipboard.png',
            'cargar_lista': 'folder.png',
            'limpiar_json': 'clean.png',
            'cargar_json': 'download.png',
            'agregar_carpeta': 'add_folder.png',
            # Botones explorador
            'atras': 'back.png',
            'adelante': 'forward.png',
            'subir': 'up.png',
            'abrir_explorer': 'open.png',
            'cambiar_carpeta': 'refresh.png',
            'seleccionar_todo': 'select_all.png',
            'marcar_visibles': 'check.png',
            'desmarcar_visibles': 'uncheck.png',
            'copiar_seleccion': 'copy.png',
            'copiar_marcados': 'copy_marked.png',
            'limpiar_seleccion': 'clear.png',
            'buscar': 'search.png',
            'limpiar_filtro': 'clear_filter.png',
            'ver_carpetas': 'eye.png',
        }
        
        for key, filename in icon_mapping.items():
            icon_path = icons_dir / filename
            # Si no existe, intentar con variantes comunes (typos)
            if not icon_path.exists() and key == 'cargar_json':
                icon_path = icons_dir / 'dowload.png'  # Variante con typo común
            if icon_path.exists():
                try:
                    # Cargar imagen y redimensionar a 20x20 píxeles
                    img = Image.open(str(icon_path))
                    img = img.resize((20, 20), Image.Resampling.LANCZOS)
                    self.icons[key] = ctk.CTkImage(light_image=img, dark_image=img, size=(20, 20))
                except Exception as e:
                    print(f"Error cargando icono {filename}: {e}")
    
    def _apply_icons_to_buttons(self):
        """Aplica los iconos cargados a los botones correspondientes"""
        if not hasattr(self, 'icons') or not self.icons:
            return
        
        # Mapeo de botones a claves de iconos
        button_icon_map = {
            # Botones superiores
            'btn_limpiar_lista': 'limpiar_lista',
            'btn_paste_list': 'pegar_lista',
            'btn_cargar_lista': 'cargar_lista',
            'btn_limpiar': 'limpiar_json',
            'btn_cargar': 'cargar_json',
            'btn_add_root': 'agregar_carpeta',
            'btn_view_roots': 'ver_carpetas',
            # Botones explorador
            'btn_back': 'atras',
            'btn_forward': 'adelante',
            'btn_up': 'subir',
            'btn_open_explorer': 'abrir_explorer',
            'btn_change_folder': 'cambiar_carpeta',
            'btn_select_all': 'seleccionar_todo',
            'btn_mark_all': 'marcar_visibles',
            'btn_unmark_all': 'desmarcar_visibles',
            'btn_copy_rows': 'copiar_seleccion',
            'btn_copy_marked': 'copiar_marcados',
            'btn_limpiar_seleccion': 'limpiar_seleccion',
            'btn_filter': 'buscar',
            'btn_filter_clear': 'limpiar_filtro',
            'boton_buscar': 'buscar',
        }
        
        for button_attr, icon_key in button_icon_map.items():
            if hasattr(self, button_attr) and icon_key in self.icons:
                button = getattr(self, button_attr)
                try:
                    # Obtener el texto actual del botón (sin emoji)
                    current_text = button.cget("text")
                    # Extraer solo el texto después del emoji (si existe)
                    text_parts = current_text.split(" ", 1)
                    button_text = text_parts[-1] if len(text_parts) > 1 else current_text
                    # Configurar el botón con el icono y el texto
                    button.configure(image=self.icons[icon_key], text=button_text, compound="left")
                except Exception as e:
                    print(f"Error aplicando icono a {button_attr}: {e}")

    # ---------- traducción y preferencias ----------
    def traducir(self, clave): 
        resultado = traducciones.get(self.idioma_actual, {}).get(clave)
        if resultado is None:
            # Si falta en el idioma actual, intentar español como fallback
            resultado = traducciones.get("es", {}).get(clave)
        if resultado is None:
            return f"MISSING_TRANSLATION_{clave}"
        return resultado

    def _guardar_config(self):
        config = {
            "idioma": self.idioma_actual,
            "modo_oscuro": self.switch_var.get(),
            "solo_marcados": getattr(self, "switch_solo_marcados_var", ctk.BooleanVar(value=False)).get(),
            "scan_roots": getattr(self, "_scan_roots", []),
            "copy_method": self.copy_method,
            "nombre_cliente": getattr(self, "nombre_cliente", ""),
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f)
        except IOError as e:
            messagebox.showerror(self.traducir("error"), f"Error al guardar configuración: {e}")

    def _cargar_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                if config.get("idioma") in traducciones: self.idioma_actual = config["idioma"]
                if config.get("modo_oscuro") is not None: self.modo_oscuro_inicial = config["modo_oscuro"]
                if config.get("solo_marcados") is not None: self.solo_marcados_inicial = config["solo_marcados"]
                self._scan_roots = config.get("scan_roots", [])
                if config.get("copy_method") in ("auto","explorer","internal"):
                    self.copy_method = config["copy_method"]
                if config.get("nombre_cliente"):
                    self.nombre_cliente = config["nombre_cliente"]
            except Exception as e:
                messagebox.showwarning(self.traducir("info"), f"Error al cargar configuración, usando valores predeterminados: {e}")
    
    def _actualizar_titulo(self):
        """Actualiza el título de la ventana con el nombre del cliente si está configurado"""
        titulo_base = "SVXboxGamesFinder (Local) - By: @erickmacielsoto - Reviewed by: @jasontorresb"
        if hasattr(self, "nombre_cliente") and self.nombre_cliente.strip():
            self.title(f"{titulo_base} - Cliente: {self.nombre_cliente}")
        else:
            self.title(titulo_base)
    
    def _editar_nombre_cliente(self):
        """Abre un diálogo para editar el nombre del cliente"""
        dlg = ctk.CTkToplevel(self)
        dlg.title("Editar nombre del cliente")
        dlg.geometry("500x200")
        dlg.transient(self)
        dlg.grab_set()
        
        frame = ctk.CTkFrame(dlg)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        label = ctk.CTkLabel(
            frame,
            text="Nombre del cliente:",
            font=ctk.CTkFont(size=12)
        )
        label.pack(pady=(0, 10))
        
        entry = ctk.CTkEntry(frame, width=450, height=35)
        entry.pack(pady=(0, 20))
        entry.insert(0, getattr(self, "nombre_cliente", ""))
        entry.focus()
        
        def guardar():
            nuevo_nombre = entry.get().strip()
            self.nombre_cliente = nuevo_nombre
            self._guardar_config()
            self._actualizar_titulo()
            dlg.destroy()
        
        def cancelar():
            dlg.destroy()
        
        buttons_frame = ctk.CTkFrame(frame)
        buttons_frame.pack(fill="x")
        
        btn_guardar = ctk.CTkButton(
            buttons_frame,
            text="Guardar",
            command=guardar,
            width=120
        )
        btn_guardar.pack(side="left", padx=5)
        
        btn_cancelar = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            command=cancelar,
            width=120
        )
        btn_cancelar.pack(side="right", padx=5)
        
        # Permitir guardar con Enter
        entry.bind("<Return>", lambda e: guardar())

    def _detectar_idioma_sistema(self):
        lang, _ = locale.getdefaultlocale()
        if lang:
            if lang.startswith("es"): return "es"
            if lang.startswith("pt"): return "pt"
            if lang.startswith("en"): return "en"
        return "es"

    def _detectar_modo_oscuro_linux(self):
        try:
            res = subprocess.run(['gsettings','get','org.gnome.desktop.interface','color-scheme'],
                                 capture_output=True, text=True)
            if res.returncode == 0:
                return res.stdout.strip().strip("'") == "prefer-dark"
        except Exception:
            pass
        return False

    def _detectar_modo_oscuro_windows(self):
        try: import winreg
        except ImportError: return None
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except Exception:
            return None

    def _detectar_modo_oscuro_sistema(self):
        if sys.platform.startswith("win"):
            m = self._detectar_modo_oscuro_windows()
            if m is not None: return m
        elif sys.platform.startswith("linux"):
            return self._detectar_modo_oscuro_linux()
        return False

    # ---------- apariencia ----------
    def _aplicar_estilo_treeview(self, modo):
        style = ttk.Style()
        font_name = 'Segoe UI' if sys.platform.startswith('win') else 'Ubuntu'
        if modo == "dark":
            style.theme_use('clam')
            style.configure("Treeview", background="#2b2b2b", foreground="white",
                            fieldbackground="#2b2b2b", font=(font_name, 10))
            style.map("Treeview", background=[('selected','#0a64a4')], foreground=[('selected','white')])
            style.configure("Treeview.Heading", background="#3c3f41", foreground="white", font=(font_name, 11, 'bold'))
        else:
            style.theme_use('default')
            style.configure("Treeview", background="white", foreground="black",
                            fieldbackground="white", font=(font_name, 10))
            style.map("Treeview", background=[('selected','#3399FF')], foreground=[('selected','white')])
            style.configure("Treeview.Heading", background="#f0f0f0", foreground="black", font=(font_name, 11, 'bold'))
    
    def _toggle_mode(self):
        ctk.set_appearance_mode("dark" if self.switch_var.get() else "light")
        self._aplicar_estilo_treeview("dark" if self.switch_var.get() else "light")
        self._guardar_config()
    
    def _toggle_solo_marcados(self):
        """Filtra el explorador para mostrar solo los elementos marcados"""
        self._guardar_config()
        # Refrescar la vista actual
        if hasattr(self, "_current_entries") and self._current_entries:
            self._render_files(self._current_entries)

    # ---------- copiar texto ----------
    def _copiar_fila(self, tree):
        selected = tree.focus()
        if selected:
            values = tree.item(selected, "values")
            texto = "\t".join(str(v) for v in values)
            self.clipboard_clear(); self.clipboard_append(texto); self.update()

    def _copiar_celda(self, tree):
        if hasattr(tree, "_selected_column") and hasattr(tree, "_selected_row"):
            value = tree.set(tree._selected_row, tree._selected_column)
            self.clipboard_clear(); self.clipboard_append(value); self.update()

    # ---------- menús contextuales ----------
    def _crear_menu_contextual(self, tree):
        menu = Menu(tree, tearoff=0)
        menu.add_command(label=self.traducir("copiar_celda"), command=lambda: self._copiar_celda(tree))
        menu.add_command(label=self.traducir("copiar_fila"), command=lambda: self._copiar_fila(tree))
        if tree is self.tree_title_ids:
            menu.add_separator()
            menu.add_command(label=self.traducir("abrir_carpeta"), command=self._open_selected_folder)
            menu.add_command(label=self.traducir("ver_archivos"), command=self._browse_selected_game)
            menu.add_command(label=self.traducir("copiar_a"), command=self._copy_selected_game_folder)
        elif tree is getattr(self, "tree_files", None):
            menu.add_separator()
            menu.add_command(label=self.traducir("abrir"), command=self._open_selected_files)
            menu.add_command(label=self.traducir("mostrar_en_explorer"), command=self._show_selected_in_explorer)
            menu.add_separator()
            menu.add_command(label=self.traducir("copiar_seleccion"),
                             command=self._copy_selected_rows_browser)
            menu.add_command(label=self.traducir("copiar_marcados"),
                             command=self._copy_checked_items_from_browser)
            menu.add_separator()
            menu.add_command(label=self.traducir("seleccionar_todo"),
                             command=lambda: self.tree_files.selection_set(self.tree_files.get_children()))
        return menu

    def _mostrar_menu_contextual(self, event, tree, menu):
        row = tree.identify_row(event.y); column = tree.identify_column(event.x)
        if row:
            tree.selection_set(row); tree.focus(row); tree._selected_row = row
            if column and column.startswith('#'):
                col_index = int(column[1:]) - 1
                if 0 <= col_index < len(tree["columns"]): tree._selected_column = tree["columns"][col_index]
            menu.tk_popup(event.x_root, event.y_root)

    def _copiar_ctrl_c(self, event, tree):
        if hasattr(tree, "_selected_column") and hasattr(tree, "_selected_row"): self._copiar_celda(tree)
        else: self._copiar_fila(tree)

    # ---------- UI ----------
    def _setup_ui(self):
        # Top bar
        frame_top = ctk.CTkFrame(self); frame_top.pack(fill="x", padx=10, pady=5)

        left = ctk.CTkFrame(frame_top, fg_color="transparent"); left.pack(side="left")
        self.switch_var = ctk.BooleanVar(value=self.modo_oscuro_inicial)
        self.switch = ctk.CTkSwitch(left, text=self.traducir("modo_oscuro"),
                                    variable=self.switch_var, command=self._toggle_mode)
        self.switch.pack(side="left", padx=(10, 10))
        self.switch_solo_marcados_var = ctk.BooleanVar(value=self.solo_marcados_inicial)
        self.switch_solo_marcados = ctk.CTkSwitch(left, text=self.traducir("solo_marcados"),
                                                  variable=self.switch_solo_marcados_var, command=self._toggle_solo_marcados)
        self.switch_solo_marcados.pack(side="left", padx=(10, 10))
        self.idioma_menu_label = ctk.CTkLabel(left, text=f"🌐 {self.traducir('idioma')}:")
        self.idioma_menu_label.pack(side="left", padx=(10, 5))
        self.selector_idioma = ctk.CTkOptionMenu(left, values=["Español", "English", "Português"],
                                                 command=self._cambiar_idioma)
        self.selector_idioma.pack(side="left")
        self.selector_idioma.set({"es":"Español","en":"English","pt":"Português"}.get(self.idioma_actual,"Español"))
        
        # Botón para editar nombre del cliente
        self.btn_editar_cliente = ctk.CTkButton(
            left,
            text="👤 Cliente",
            command=self._editar_nombre_cliente,
            width=100,
            height=28
        )
        self.btn_editar_cliente.pack(side="left", padx=(10, 0))

        # Frame derecho con botones organizados en múltiples filas
        right = ctk.CTkFrame(frame_top, fg_color="transparent")
        right.pack(side="right")
        
        # Fila 1: Método de copia y botones de lista
        ctk.CTkLabel(right, text=f"🚚 {self.traducir('metodo_copia')}:").grid(row=0, column=0, padx=(0,6), pady=2, sticky="w")
        self.copy_method_var = ctk.StringVar(value=self.copy_method)
        self.copy_method_menu = ctk.CTkOptionMenu(
            right,
            values=[ "auto", "explorer", "internal" ],
            variable=self.copy_method_var,
            command=self._on_change_copy_method,
            width=120
        )
        self.copy_method_menu.grid(row=0, column=1, padx=(0,6), pady=2, sticky="w")
        
        self.btn_limpiar_lista = ctk.CTkButton(right, text="🗑️ Limpiar lista", command=self._limpiar_lista_cargada, width=110)
        self.btn_limpiar_lista.grid(row=0, column=2, padx=(6, 6), pady=2, sticky="w")
        self.btn_paste_list = ctk.CTkButton(right, text="📋 Pegar lista", command=self._pegar_lista_dialog, width=110)
        self.btn_paste_list.grid(row=0, column=3, padx=(6, 6), pady=2, sticky="w")
        self.btn_cargar_lista = ctk.CTkButton(right, text="📁 Cargar lista", command=self._cargar_lista, width=110)
        self.btn_cargar_lista.grid(row=0, column=4, padx=(6, 6), pady=2, sticky="w")
        
        # Fila 2: Botones de JSON y carpeta
        self.btn_limpiar = ctk.CTkButton(right, text=f"🧹 {self.traducir('limpiar_db')}", command=self._limpiar_db, width=110)
        self.btn_limpiar.grid(row=1, column=0, padx=(6, 6), pady=2, sticky="w")
        self.btn_cargar = ctk.CTkButton(right, text=f"📥 {self.traducir('cargar_json')}", command=self._cargar_json, width=110)
        self.btn_cargar.grid(row=1, column=1, padx=(6, 6), pady=2, sticky="w")
        self.btn_add_root = ctk.CTkButton(right, text=f"📂 {self.traducir('agregar_carpeta')}", command=self._add_scan_root, width=110)
        self.btn_add_root.grid(row=1, column=2, padx=(6, 6), pady=2, sticky="w")
        self.btn_view_roots = ctk.CTkButton(right, text=self.traducir('ver_carpetas'), command=self._show_scan_roots_dialog, width=110)
        self.btn_view_roots.grid(row=1, column=3, padx=(6, 6), pady=2, sticky="e")
        
        # Guardar anchos originales de los botones superiores
        self._top_button_widths = {
            'copy_method_menu': 120,
            'btn_limpiar_lista': 110,
            'btn_paste_list': 110,
            'btn_cargar_lista': 110,
            'btn_limpiar': 110,
            'btn_cargar': 110,
            'btn_add_root': 110,
        }

        # Frame para entrada de búsqueda (responsivo)
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(10, 0))
        self.label_entrada = ctk.CTkLabel(search_frame, text=self.traducir("ingresa_texto"))
        self.label_entrada.pack(pady=(0, 5))
        entry_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        entry_frame.pack(fill="x", pady=5)
        self.entry = ctk.CTkEntry(entry_frame, placeholder_text="Ej: 4D530AA4 o Forza Horizon")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry.bind("<Return>", self._buscar_todo)
        self.boton_buscar = ctk.CTkButton(entry_frame, text=f"🔍 {self.traducir('buscar')}", command=self._buscar_todo)
        self.boton_buscar.pack(side="right")

        self.status_label = ctk.CTkLabel(self, text="", fg_color="transparent"); self.status_label.pack(pady=(0, 6))
        
        # Resumen de base de datos con opción de colapsar
        summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        summary_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        self.summary_collapsed = ctk.BooleanVar(value=False)
        self.summary_toggle = ctk.CTkButton(
            summary_frame, 
            text="📊", 
            width=30, 
            height=25,
            command=lambda: self._toggle_summary()
        )
        self.summary_toggle.pack(side="left", padx=(0, 5))
        
        self.db_summary = ctk.CTkLabel(summary_frame, text="", fg_color="transparent", anchor="w")
        self.db_summary.pack(side="left", fill="x", expand=True)

        # Tabla Title IDs (altura reducida para dar más espacio al explorador)
        self.frame_title = ctk.CTkFrame(self); self.frame_title.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        title_header = ctk.CTkFrame(self.frame_title, fg_color="transparent")
        title_header.pack(fill="x", padx=5, pady=5)
        self.label_title = ctk.CTkLabel(title_header, text=self.traducir("title_ids"), font=ctk.CTkFont(size=14, weight="bold"))
        self.label_title.pack(side="left")
        self.title_hint = ctk.CTkLabel(title_header, text="💡 Busca un juego arriba para ver resultados aquí", 
                                      text_color="gray", font=ctk.CTkFont(size=11))
        self.title_hint.pack(side="right", padx=10)

        wrap_titles = ctk.CTkFrame(self.frame_title, fg_color="transparent"); wrap_titles.pack(fill="both", expand=True)
        columns_title = ("title_id","name","system")
        self.tree_title_ids = ttk.Treeview(wrap_titles, columns=columns_title, show="headings", height=8, selectmode="browse")
        for col in columns_title:
            self.tree_title_ids.heading(col, text=self.traducir("col_"+col))
            self.tree_title_ids.column(col, width=520 if col=="name" else 160, stretch=(col=="name"))
        sb_y_t = ttk.Scrollbar(wrap_titles, orient="vertical", command=self.tree_title_ids.yview)
        sb_x_t = ttk.Scrollbar(wrap_titles, orient="horizontal", command=self.tree_title_ids.xview)
        self.tree_title_ids.configure(yscrollcommand=sb_y_t.set, xscrollcommand=sb_x_t.set)
        wrap_titles.grid_columnconfigure(0, weight=1); wrap_titles.grid_rowconfigure(0, weight=1)
        self.tree_title_ids.grid(row=0,column=0,sticky="nsew"); sb_y_t.grid(row=0,column=1,sticky="ns"); sb_x_t.grid(row=1,column=0,sticky="ew")
        self.menu_title = self._crear_menu_contextual(self.tree_title_ids)
        self.tree_title_ids.bind("<Button-3>", lambda e: self._mostrar_menu_contextual(e, self.tree_title_ids, self.menu_title))
        self.tree_title_ids.bind("<Control-c>", lambda e: self._copiar_ctrl_c(e, self.tree_title_ids))
        self.tree_title_ids.bind("<Double-1>", lambda e: self._browse_selected_game())

        # Explorador
        self.frame_explorer = ctk.CTkFrame(self); self.frame_explorer.pack(fill="both", expand=True, padx=10, pady=(0, 12))
        header = ctk.CTkFrame(self.frame_explorer, fg_color="transparent"); header.pack(fill="x", padx=4, pady=(6, 4))
        
        # Primera fila: Título e información (todo en una línea)
        header_info = ctk.CTkFrame(header, fg_color="transparent")
        header_info.pack(fill="x", pady=(0, 4))
        explorer_title = ctk.CTkLabel(header_info, text=self.traducir("explorador"), font=ctk.CTkFont(size=14, weight="bold"))
        explorer_title.pack(side="left", padx=(2, 8))
        self.path_label = ctk.CTkLabel(header_info, text=f"{self.traducir('ruta')} -"); self.path_label.pack(side="left")
        # ← Contador de seleccionados | marcados
        self.counts_label = ctk.CTkLabel(header_info, text="  |  0/0"); self.counts_label.pack(side="left", padx=(8, 0))
        # Hint para el explorador
        self.explorer_hint = ctk.CTkLabel(header_info, text="💡 Agrega una carpeta arriba para navegar", 
                                       text_color="gray", font=ctk.CTkFont(size=11))
        self.explorer_hint.pack(side="left", padx=(10, 0))

        # Segunda fila y siguientes: Botones del explorador - organizados de 4 en 4, alineados a la derecha
        buttons_frame = ctk.CTkFrame(self.frame_explorer, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=4, pady=(0, 4))
        
        # Frame para alinear botones a la derecha
        buttons_container = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        buttons_container.pack(side="right")
        
        # Fila 1: Navegación básica (6 botones)
        self.btn_back = ctk.CTkButton(buttons_container, text=f"⬅️ {self.traducir('atras')}", width=90, command=self._nav_back)
        self.btn_back.grid(row=0, column=0, padx=(6,4), pady=2)
        self.btn_forward = ctk.CTkButton(buttons_container, text=f"➡️ {self.traducir('adelante')}", width=90, command=self._nav_forward)
        self.btn_forward.grid(row=0, column=1, padx=(6,4), pady=2)
        self.btn_up = ctk.CTkButton(buttons_container, text=f"⬆️ {self.traducir('subir')}", width=100, command=self._go_up)
        self.btn_up.grid(row=0, column=2, padx=(6,4), pady=2)
        self.btn_open_explorer = ctk.CTkButton(buttons_container, text=f"📂 {self.traducir('abrir_explorer')}", width=120, command=self._open_current_in_explorer)
        self.btn_open_explorer.grid(row=0, column=3, padx=(6,4), pady=2)
        self.btn_change_folder = ctk.CTkButton(buttons_container, text=f"🔄 {self.traducir('cambiar_carpeta')}", width=120, command=self._change_browser_folder)
        self.btn_change_folder.grid(row=0, column=4, padx=(6,4), pady=2)
        self.btn_select_all = ctk.CTkButton(buttons_container, text=f"✅ {self.traducir('seleccionar_todo')}", width=120, command=self._select_all_files)
        self.btn_select_all.grid(row=0, column=5, padx=(6,4), pady=2)
        
        # Fila 2: Marcado y copia (6 botones)
        self.btn_mark_all = ctk.CTkButton(buttons_container, text=f"☑️ {self.traducir('marcar_visibles')}", width=120, command=self._mark_visible_rows)
        self.btn_mark_all.grid(row=1, column=0, padx=(6,4), pady=2)
        self.btn_unmark_all = ctk.CTkButton(buttons_container, text=f"☐ {self.traducir('desmarcar_visibles')}", width=120, command=self._unmark_visible_rows)
        self.btn_unmark_all.grid(row=1, column=1, padx=(6,4), pady=2)
        self.btn_copy_rows = ctk.CTkButton(buttons_container, text=f"📋 {self.traducir('copiar_seleccion')}", width=120, command=self._copy_selected_rows_browser)
        self.btn_copy_rows.grid(row=1, column=2, padx=(6,4), pady=2)
        self.btn_copy_marked = ctk.CTkButton(buttons_container, text=f"📦 {self.traducir('copiar_marcados')}", width=120, command=self._copy_checked_items_from_browser)
        self.btn_copy_marked.grid(row=1, column=3, padx=(6,4), pady=2)
        self.btn_generar_lista = ctk.CTkButton(buttons_container, text=f"📝 {self.traducir('generar_lista_marcados')}", width=140, command=self._generar_lista_marcados)
        self.btn_generar_lista.grid(row=1, column=4, padx=(6,4), pady=2)
        self.btn_limpiar_seleccion = ctk.CTkButton(buttons_container, text=f"🗑️ {self.traducir('limpiar_seleccion')}", width=120, command=self._limpiar_lista_cargada)
        self.btn_limpiar_seleccion.grid(row=1, column=5, padx=(6,4), pady=2)
        
        # Fila 3: Acciones avanzadas (6 botones)
        self.btn_eliminar_marcados = ctk.CTkButton(
            buttons_container, 
            text=f"🗑️ {self.traducir('eliminar_marcados')}", 
            width=140, 
            command=self._eliminar_marcados,
            fg_color="#d32f2f",
            hover_color="#b71c1c"
        )
        self.btn_eliminar_marcados.grid(row=2, column=0, padx=(6,4), pady=2)
        self.btn_comparar_ubicacion = ctk.CTkButton(
            buttons_container,
            text=f"🔍 {self.traducir('comparar_ubicacion')}",
            width=160,
            command=self._comparar_ubicacion_destino
        )
        self.btn_comparar_ubicacion.grid(row=2, column=1, padx=(6,4), pady=2)
        self.btn_log_transferencias = ctk.CTkButton(
            buttons_container,
            text=f"📋 {self.traducir('log_transferencias')}",
            width=140,
            command=self._mostrar_log_dialog
        )
        self.btn_log_transferencias.grid(row=2, column=2, padx=(6,4), pady=2)
        self.btn_restaurar_log = ctk.CTkButton(
            buttons_container,
            text=f"↩️ {self.traducir('restaurar_desde_log')}",
            width=160,
            command=self._restaurar_desde_log,
            fg_color="#ff9800",
            hover_color="#f57c00"
        )
        self.btn_restaurar_log.grid(row=2, column=3, padx=(6,4), pady=2)
        self.btn_continuar_log = ctk.CTkButton(
            buttons_container,
            text=f"▶️ {self.traducir('continuar_desde_log')}",
            width=160,
            command=self._continuar_desde_log
        )
        self.btn_continuar_log.grid(row=2, column=4, padx=(6,4), pady=2)
        
        # Guardar anchos originales de los botones del explorador
        self._explorer_button_widths = {
            'btn_back': 90,
            'btn_forward': 90,
            'btn_up': 100,
            'btn_open_explorer': 120,
            'btn_change_folder': 120,
            'btn_copy_rows': 120,
            'btn_select_all': 120,
            'btn_mark_all': 120,
            'btn_unmark_all': 120,
            'btn_limpiar_seleccion': 120,
            'btn_copy_marked': 120,
        }

        # Filtro y ordenamiento
        filter_bar = ctk.CTkFrame(self.frame_explorer, fg_color="transparent"); filter_bar.pack(fill="x", padx=6, pady=(0,6))
        self.files_filter_var = ctk.StringVar(value="")
        self.files_filter_entry = ctk.CTkEntry(filter_bar, textvariable=self.files_filter_var,
                                               placeholder_text=self.traducir("filtro_placeholder"), width=400)
        self.files_filter_entry.pack(side="left", padx=(0,6))
        self.files_filter_entry.bind("<Return>", lambda e: self._apply_files_filter())
        self.files_filter_entry.bind("<KeyRelease>", lambda e: self._apply_files_filter(debounce=True))
        self.btn_filter = ctk.CTkButton(filter_bar, text=f"🔍 {self.traducir('aplicar_filtro')}", width=90, command=self._apply_files_filter)
        self.btn_filter.pack(side="left", padx=(0,6))
        self.btn_filter_clear = ctk.CTkButton(filter_bar, text=f"🧹 {self.traducir('limpiar_filtro')}", width=90, command=self._clear_files_filter)
        self.btn_filter_clear.pack(side="left", padx=(0,12))
        
        # Ordenamiento
        self.sort_label = ctk.CTkLabel(filter_bar, text=self.traducir("ordenar_por"))
        self.sort_label.pack(side="left", padx=(0,6))
        sort_options = [
            ("nombre", self.traducir("orden_nombre")),
            ("tamano", self.traducir("orden_tamano")),
            ("tipo", self.traducir("orden_tipo")),
            ("modificado", self.traducir("orden_modificado"))
        ]
        # Mapeo de valores mostrados a valores internos
        self._sort_value_map = {label: value for value, label in sort_options}
        self._sort_reverse_map = {value: label for value, label in sort_options}
        self.sort_order_var = ctk.StringVar(value=self._sort_reverse_map.get("nombre", sort_options[0][1]))
        self.sort_combo = ctk.CTkComboBox(
            filter_bar,
            values=[label for _, label in sort_options],
            variable=self.sort_order_var,
            width=120,
            command=self._on_sort_changed
        )
        self.sort_combo.pack(side="left")

        # Tabla de archivos (con columna de check y nombre de juego)
        wrap_files = ctk.CTkFrame(self.frame_explorer, fg_color="transparent"); wrap_files.pack(fill="both", expand=True)
        columns_files = ("mark","name","game_name","type","size","modified","path")
        self.tree_files = ttk.Treeview(wrap_files, columns=columns_files, show="headings", height=12, selectmode="extended")
        self.tree_files["displaycolumns"] = ("mark","name","game_name","type","size","modified")

        self.tree_files.heading("mark", text=self.traducir("col_sel"))
        self.tree_files.heading("name", text=self.traducir("nombre"))
        self.tree_files.heading("game_name", text="Juego")
        self.tree_files.heading("type", text=self.traducir("tipo"))
        self.tree_files.heading("size", text=self.traducir("tamano"))
        self.tree_files.heading("modified", text=self.traducir("modificado"))
        self.tree_files.heading("path", text="Path")

        self.tree_files.column("mark", width=60, stretch=False, anchor="center")
        self.tree_files.column("name", width=300, stretch=True)
        self.tree_files.column("game_name", width=260, stretch=True)
        self.tree_files.column("type", width=140, stretch=False)
        self.tree_files.column("size", width=120, stretch=False, anchor="e")
        self.tree_files.column("modified", width=160, stretch=False)
        self.tree_files.column("path", width=10, stretch=False)

        sb_y_f = ttk.Scrollbar(wrap_files, orient="vertical", command=self.tree_files.yview)
        sb_x_f = ttk.Scrollbar(wrap_files, orient="horizontal", command=self.tree_files.xview)
        self.tree_files.configure(yscrollcommand=sb_y_f.set, xscrollcommand=sb_x_f.set)
        wrap_files.grid_columnconfigure(0, weight=1); wrap_files.grid_rowconfigure(0, weight=1)
        self.tree_files.grid(row=0,column=0,sticky="nsew"); sb_y_f.grid(row=0,column=1,sticky="ns"); sb_x_f.grid(row=1,column=0,sticky="ew")

        self.menu_files = self._crear_menu_contextual(self.tree_files)
        self.tree_files.bind("<Button-3>", lambda e: self._mostrar_menu_contextual(e, self.tree_files, self.menu_files))
        self.tree_files.bind("<Double-1>", lambda e: self._open_or_enter())
        # Toggle de checkbox con click
        self.tree_files.bind("<Button-1>", self._on_tree_files_click)
        # Actualizar contador cuando cambia la selección
        self.tree_files.bind("<<TreeviewSelect>>", lambda e: self._update_counts())

    def _update_ui_texts(self):
        self.label_entrada.configure(text=self.traducir("ingresa_texto"))
        self.boton_buscar.configure(text=f"🔍 {self.traducir('buscar')}")
        self.switch.configure(text=self.traducir("modo_oscuro"))
        self.idioma_menu_label.configure(text=f"🌐 {self.traducir('idioma')}:")
        # etiquetas del método de copia (mostrar texto amistoso en tooltip rápido)
        method = self.copy_method_var.get()
        self.copy_method_menu.configure(values=["auto","explorer","internal"])
        self.btn_cargar.configure(text=f"📥 {self.traducir('cargar_json')}")
        self.btn_limpiar.configure(text=f"🧹 {self.traducir('limpiar_db')}")
        self.btn_add_root.configure(text=f"📂 {self.traducir('agregar_carpeta')}")
        self.label_title.configure(text=self.traducir("title_ids"))
        self.btn_back.configure(text=f"⬅️ {self.traducir('atras')}")
        self.btn_forward.configure(text=f"➡️ {self.traducir('adelante')}")
        self.btn_up.configure(text=f"⬆️ {self.traducir('subir')}")
        self.btn_open_explorer.configure(text=f"📂 {self.traducir('abrir_explorer')}")
        self.btn_change_folder.configure(text=f"🔄 {self.traducir('cambiar_carpeta')}")
        self.btn_copy_rows.configure(text=f"📋 {self.traducir('copiar_seleccion')}")
        self.btn_copy_marked.configure(text=f"📦 {self.traducir('copiar_marcados')}")
        self.btn_select_all.configure(text=f"✅ {self.traducir('seleccionar_todo')}")
        self.btn_mark_all.configure(text=f"☑️ {self.traducir('marcar_visibles')}")
        self.btn_unmark_all.configure(text=f"☐ {self.traducir('desmarcar_visibles')}")
        self.path_label.configure(text=f"{self.traducir('ruta')} -")
        self.files_filter_entry.configure(placeholder_text=self.traducir("filtro_placeholder"))
        self.btn_filter.configure(text=f"🔍 {self.traducir('aplicar_filtro')}")
        self.btn_filter_clear.configure(text=f"🧹 {self.traducir('limpiar_filtro')}")
        # Actualizar ComboBox de ordenamiento
        if hasattr(self, "sort_label"):
            self.sort_label.configure(text=self.traducir("ordenar_por"))
        if hasattr(self, "sort_combo"):
            sort_options = [
                ("nombre", self.traducir("orden_nombre")),
                ("tamano", self.traducir("orden_tamano")),
                ("tipo", self.traducir("orden_tipo")),
                ("modificado", self.traducir("orden_modificado"))
            ]
            self._sort_value_map = {label: value for value, label in sort_options}
            self._sort_reverse_map = {value: label for value, label in sort_options}
            # Obtener el valor actual interno y actualizar el texto mostrado
            current_value = self.sort_order_var.get()
            current_internal = self._sort_value_map.get(current_value, "nombre")
            self.sort_combo.configure(values=[label for _, label in sort_options])
            self.sort_order_var.set(self._sort_reverse_map.get(current_internal, sort_options[0][1]))
        self.tree_files.heading("mark", text=self.traducir("col_sel"))
        self.tree_files.heading("name", text=self.traducir("nombre"))
        self.tree_files.heading("type", text=self.traducir("tipo"))
        self.tree_files.heading("size", text=self.traducir("tamano"))
        self.tree_files.heading("modified", text=self.traducir("modificado"))
        # refrescar contador
        self._update_counts()

    def _on_window_resize(self, event=None):
        """Ajusta el tamaño de los botones cuando la ventana se redimensiona"""
        if event and event.widget != self:
            return
        
        if self._resize_job:
            self.after_cancel(self._resize_job)
        
        # Debounce: esperar 100ms después del último evento de redimensionamiento
        self._resize_job = self.after(100, self._adjust_button_sizes)
    
    def _adjust_button_sizes(self):
        """Ajusta el tamaño de los botones según el ancho de la ventana"""
        try:
            window_width = self.winfo_width()
            if window_width < 100:  # Aún no se ha renderizado completamente
                return
            
            # Ancho de referencia (1200px es el tamaño inicial)
            reference_width = 1200
            # Ancho mínimo para mantener funcionalidad (800px)
            min_width = 800
            
            # Calcular factor de escala (1.0 cuando es >= reference_width, menor cuando es más pequeño)
            if window_width >= reference_width:
                scale = 1.0
            elif window_width <= min_width:
                scale = 0.65  # Reducir a 65% del tamaño original
            else:
                # Escala lineal entre min_width y reference_width
                scale = 0.65 + (0.35 * (window_width - min_width) / (reference_width - min_width))
            
            # Ajustar botones del explorador
            if hasattr(self, '_explorer_button_widths'):
                for btn_name, original_width in self._explorer_button_widths.items():
                    if hasattr(self, btn_name):
                        btn = getattr(self, btn_name)
                        new_width = max(int(original_width * scale), 60)  # Mínimo 60px
                        btn.configure(width=new_width)
            
            # Ajustar botones superiores
            if hasattr(self, 'copy_method_menu'):
                original_width = self._top_button_widths.get('copy_method_menu', 120)
                new_width = max(int(original_width * scale), 80)
                self.copy_method_menu.configure(width=new_width)
            
            # Ajustar otros botones superiores
            top_buttons = [
                'btn_limpiar_lista', 'btn_paste_list', 'btn_cargar_lista',
                'btn_limpiar', 'btn_cargar', 'btn_add_root'
            ]
            for btn_name in top_buttons:
                if hasattr(self, btn_name):
                    btn = getattr(self, btn_name)
                    original_width = self._top_button_widths.get(btn_name, 110)
                    new_width = max(int(original_width * scale), 70)
                    btn.configure(width=new_width)
                    
        except Exception as e:
            # Silenciar errores durante el redimensionamiento
            pass

    def _on_change_copy_method(self, value):
        # value: "auto" | "explorer" | "internal"
        self.copy_method = value
        self._guardar_config()

    def _cambiar_idioma(self, val):
        self.idioma_actual = {'Español':'es','English':'en','Português':'pt'}[val]
        self.selector_idioma.set(val); self._guardar_config(); self._update_ui_texts(); self._update_db_summary()

    def _limpiar_db(self):
        clear_db(); self._update_db_summary()
        for item in self.tree_title_ids.get_children(): self.tree_title_ids.delete(item)

    def _cargar_json(self):
        paths = filedialog.askopenfilenames(title=self.traducir("cargar_json"),
                                            filetypes=[("JSON files","*.json"),("All files","*.*")])
        if not paths: return
        
        # Mostrar pantalla de carga siempre (puede tardar con archivos grandes)
        if len(paths) > 0:
            dlg = ctk.CTkToplevel(self)
            dlg.title(self.traducir("cargando"))
            dlg.geometry("500x150")
            dlg.transient(self)
            dlg.grab_set()
            
            frame = ctk.CTkFrame(dlg)
            frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            status_label = ctk.CTkLabel(
                frame,
                text=f"{self.traducir('cargando')} {len(paths)} archivo(s)...",
                font=ctk.CTkFont(size=12)
            )
            status_label.pack(pady=(0, 10))
            
            progress_bar = ctk.CTkProgressBar(frame, width=460, mode="determinate")
            progress_bar.pack(pady=(0, 10))
            progress_bar.set(0)
            
            detail_label = ctk.CTkLabel(
                frame,
                text="Iniciando...",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            detail_label.pack()
            
            def load_in_thread():
                loaded = 0
                errors = []
                for i, p in enumerate(paths):
                    try:
                        self.after(0, lambda idx=i, total=len(paths), file=os.path.basename(p): (
                            progress_bar.set((idx + 1) / total),
                            detail_label.configure(text=f"Cargando: {file}...")
                        ))
                        load_json_file(p)
                        loaded += 1
                    except Exception as e:
                        errors.append(f"{os.path.basename(p)}: {e}")
                
                self.after(0, lambda: (
                    dlg.destroy(),
                    self._update_db_summary(),
                    self.status_label.configure(
                        text=f"{self.traducir('busqueda_completada')} ({loaded} archivo(s) cargado(s))" if loaded else self.traducir("error"),
                        text_color="green" if loaded else "red"
                    )
                ))
                if errors:
                    self.after(0, lambda errs=errors: messagebox.showwarning(
                        self.traducir("info"),
                        f"Errores al cargar algunos archivos:\n" + "\n".join(errs[:5]) + ("..." if len(errs) > 5 else "")
                    ))
            
            threading.Thread(target=load_in_thread, daemon=True).start()
        else:
            # Si es solo un archivo, cargar directamente
            loaded = 0
            for p in paths:
                try: load_json_file(p); loaded += 1
                except Exception as e: messagebox.showwarning(self.traducir("info"), f"{os.path.basename(p)}: {e}")
            self._update_db_summary()
            if loaded: self.status_label.configure(text=self.traducir("busqueda_completada"), text_color="green")

    def _toggle_summary(self):
        """Alterna entre resumen completo y compacto"""
        if not hasattr(self, 'summary_collapsed'):
            return
        self.summary_collapsed.set(not self.summary_collapsed.get())
        self._update_db_summary()
    
    def _update_db_summary(self):
        files = len(_loaded_files)
        rows  = len(_items_by_key)
        by_sys = summarize_by_system()
        tid_paths = sum(len(v) for v in getattr(self, "_paths_by_tid", {}).values()) if hasattr(self, "_paths_by_tid") else 0
        roots = len(getattr(self, "_scan_roots", []) or [])
        
        # Resumen completo
        full_text = self.traducir("resumen_db").format(files=files, rows=rows, by_system=by_sys) + f" | Carpetas origen: {roots} | Coincidencias TID↔ruta: {tid_paths}"
        
        # Resumen compacto (solo lo esencial)
        compact_text = f"📁 {files} JSON | 📊 {rows} juegos | 🎮 {by_sys.split('|')[0].strip() if '|' in by_sys else by_sys} | 📂 {roots} carpetas | 🔗 {tid_paths} rutas"
        
        # Mostrar según estado
        if hasattr(self, 'summary_collapsed') and self.summary_collapsed.get():
            self.db_summary.configure(text=compact_text)
            self.summary_toggle.configure(text="📊")
        else:
            self.db_summary.configure(text=full_text)
            self.summary_toggle.configure(text="📊")

    # ---------- búsqueda local ----------
    def _buscar_todo(self, event=None):
        query = self.entry.get().strip()
        if not query:
            messagebox.showerror(self.traducir("error"), self.traducir("ingresa_texto")); return

        for item in self.tree_title_ids.get_children(): self.tree_title_ids.delete(item)
        # Ocultar hint cuando hay búsqueda
        if hasattr(self, 'title_hint'):
            self.title_hint.pack_forget()
        self.status_label.configure(text=self.traducir("cargando"), text_color="orange"); self.update_idletasks()
        try:
            results = []
            if re.fullmatch(r"[A-Fa-f0-9]{8}", query):
                tid = query.upper(); results = sorted(_index_tid.get(tid, []), key=lambda it: (it["system"], it["name"].lower()))
            else:
                qn = norm_text(query); limit, count = 500, 0
                for nname, it in _index_name:
                    if qn in nname:
                        results.append(it); count += 1
                        if count >= limit: break
                results = sorted(results, key=lambda it: (it["name"].lower(), it["system"]))
            if not results:
                self.status_label.configure(text=self.traducir("no_results_found"), text_color="orange")
                # Mostrar hint si no hay resultados
                if hasattr(self, 'title_hint'):
                    self.title_hint.configure(text="❌ No se encontraron resultados. Intenta con otro término.")
                    self.title_hint.pack(side="right", padx=10)
                return
            for it in results:
                self.tree_title_ids.insert("", "end", values=(it["title_id"], it["name"], it["system"]))
            self.status_label.configure(text=self.traducir("busqueda_completada"), text_color="green")
            # Ocultar hint cuando hay resultados
            if hasattr(self, 'title_hint'):
                self.title_hint.pack_forget()
        except Exception as e:
            messagebox.showerror(self.traducir("error"), f"{self.traducir('error_busqueda')}\n{e}")
            self.status_label.configure(text=self.traducir("error_busqueda"), text_color="red")

    # ---------- índice de carpetas de juegos ----------
    def _add_scan_root(self):
        path = filedialog.askdirectory(title=self.traducir("agregar_carpeta"))
        if not path: return
        
        # Solo permitir una carpeta indexada a la vez
        if not hasattr(self, "_scan_roots"): 
            self._scan_roots = []
        
        # Si ya hay una carpeta indexada, preguntar si quiere reemplazarla
        if self._scan_roots:
            existing_path = self._scan_roots[0]
            if path == existing_path:
                messagebox.showinfo(self.traducir("info"), "Esta carpeta ya está indexada.")
                return
            
            respuesta = messagebox.askyesno(
                self.traducir("info"),
                f"Ya hay una carpeta indexada:\n{existing_path}\n\n¿Deseas reemplazarla con:\n{path}?"
            )
            if not respuesta:
                return
            
            # Limpiar TODO completamente para empezar limpio con la nueva carpeta
            # Limpiar índices de paths
            if hasattr(self, "_paths_by_tid"):
                self._paths_by_tid.clear()
            if hasattr(self, "_paths_by_name"):
                self._paths_by_name.clear()
            
            # Limpiar paths marcados
            if hasattr(self, "_checked_paths"):
                self._checked_paths.clear()
            
            # Limpiar el set de raíces indexadas
            if hasattr(self, "_indexed_roots"):
                self._indexed_roots.clear()
            
            # Limpiar la vista del explorador
            if hasattr(self, "_current_entries"):
                self._current_entries = []
            if hasattr(self, "tree_files"):
                for item in self.tree_files.get_children():
                    self.tree_files.delete(item)
            
            # Actualizar contadores
            self._update_counts()
        
        # Llamar a la función auxiliar para indexar directamente
        self._index_folder_directly(path)
    
    def _index_folder_directly(self, path):
        """
        Indexa una carpeta directamente sin abrir diálogo de selección.
        Limpia todo antes de indexar para empezar limpio.
        """
        # Reemplazar con la nueva carpeta (solo una)
        self._scan_roots = [path]
        self._guardar_config()
        
        # Limpiar TODO antes de indexar la nueva carpeta (asegurar que esté todo limpio)
        # Limpiar índices de paths
        if not hasattr(self, "_paths_by_tid"):
            self._paths_by_tid = {}
        else:
            self._paths_by_tid.clear()
        
        if not hasattr(self, "_paths_by_name"):
            self._paths_by_name = {}
        else:
            self._paths_by_name.clear()
        
        # Limpiar paths marcados
        if not hasattr(self, "_checked_paths"):
            self._checked_paths = set()
        else:
            self._checked_paths.clear()
        
        # Limpiar el set de raíces indexadas
        if not hasattr(self, "_indexed_roots"):
            self._indexed_roots = set()
        else:
            self._indexed_roots.clear()
        
        # Limpiar la vista del explorador si no se limpió antes
        if hasattr(self, "_current_entries"):
            self._current_entries = []
        if hasattr(self, "tree_files"):
            for item in self.tree_files.get_children():
                self.tree_files.delete(item)
        
        # Actualizar contadores
        self._update_counts()
        
        # Crear diálogo de progreso
        dlg = ctk.CTkToplevel(self)
        dlg.title(self.traducir("indexando_carpeta"))
        dlg.geometry("500x200")
        dlg.transient(self)
        dlg.grab_set()
        
        frame = ctk.CTkFrame(dlg)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Label de estado
        status_label = ctk.CTkLabel(
            frame,
            text=f"{self.traducir('indexando_carpeta')}: {os.path.basename(path)}",
            font=ctk.CTkFont(size=12)
        )
        status_label.pack(pady=(0, 10))
        
        # Barra de progreso (indeterminada)
        progress_bar = ctk.CTkProgressBar(frame, width=460, mode="indeterminate")
        progress_bar.pack(pady=(0, 10))
        progress_bar.start()
        
        # Label de detalle
        detail_label = ctk.CTkLabel(
            frame,
            text=self.traducir("escaneando_carpeta"),
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        detail_label.pack()
        
        # Estado compartido
        state = {"done": False, "error": None, "folders_scanned": 0, "games_found": 0}
        
        def scan_in_thread():
            try:
                # Ejecutar el escaneo
                self._scan_root(path, recursive=True, progress_callback=lambda folders, games: self.after(0, lambda f=folders, g=games: update_progress(f, g)))
                state["done"] = True
            except Exception as e:
                state["error"] = str(e)
                state["done"] = True
        
        def update_progress(folders, games):
            state["folders_scanned"] = folders
            state["games_found"] = games
            detail_label.configure(text=f"{self.traducir('escaneando_carpeta')}... {folders} carpetas, {games} juegos encontrados")
        
        # Iniciar escaneo en hilo separado
        threading.Thread(target=scan_in_thread, daemon=True).start()
        
        def check_progress():
            if state["done"]:
                progress_bar.stop()
                dlg.destroy()
                if state["error"]:
                    messagebox.showerror(self.traducir("error"), f"Error al indexar carpeta:\n{state['error']}")
                    self.status_label.configure(text=self.traducir("error"), text_color="red")
                else:
                    self._update_db_summary()
                    self.status_label.configure(
                        text=f"{self.traducir('carpeta_indexada')} ({state['games_found']} juegos encontrados)",
                        text_color="green"
                    )
                    # Navegar a la carpeta indexada en el explorador (siempre, ya que solo hay una carpeta)
                    if os.path.exists(path) and os.path.isdir(path):
                        self._enter_folder(path, user_initiated=False)
            else:
                dlg.after(100, check_progress)
        
        check_progress()

    def _show_scan_roots_dialog(self):
        """Muestra un diálogo con las carpetas indexadas y permite eliminarlas"""
        if not hasattr(self, "_scan_roots") or not self._scan_roots:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguna_carpeta_agregada"))
            return
        
        dlg = ctk.CTkToplevel(self)
        dlg.title(self.traducir("carpetas_agregadas"))
        dlg.geometry("700x500")
        dlg.transient(self)
        dlg.grab_set()
        
        frame = ctk.CTkFrame(dlg)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            frame,
            text=self.traducir("carpetas_agregadas_desc").format(total=len(self._scan_roots)),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Lista de carpetas con scroll
        scroll_frame = ctk.CTkScrollableFrame(frame, width=660, height=350)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Crear un frame para cada carpeta
        for i, folder_path in enumerate(self._scan_roots):
            folder_frame = ctk.CTkFrame(scroll_frame)
            folder_frame.pack(fill="x", pady=5, padx=5)
            
            # Label con la ruta
            path_label = ctk.CTkLabel(
                folder_frame,
                text=folder_path,
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            path_label.pack(side="left", padx=10, fill="x", expand=True)
            
            # Botón eliminar
            def eliminar_carpeta(idx=i, path=folder_path):
                if messagebox.askyesno(
                    self.traducir("eliminar"),
                    f"¿Eliminar la carpeta?\n{path}"
                ):
                    self._scan_roots.pop(idx)
                    self._guardar_config()
                    # Limpiar índices relacionados con esta carpeta
                    if hasattr(self, "_paths_by_tid"):
                        paths_to_remove = [p for p in self._paths_by_tid.values() if isinstance(p, str) and p.startswith(path)]
                        for p in paths_to_remove:
                            for tid, paths in list(self._paths_by_tid.items()):
                                if isinstance(paths, list) and p in paths:
                                    paths.remove(p)
                                elif paths == p:
                                    del self._paths_by_tid[tid]
                    if hasattr(self, "_paths_by_name"):
                        paths_to_remove = [p for p in self._paths_by_name.values() if isinstance(p, str) and p.startswith(path)]
                        for p in paths_to_remove:
                            for name, paths in list(self._paths_by_name.items()):
                                if isinstance(paths, list) and p in paths:
                                    paths.remove(p)
                                elif paths == p:
                                    del self._paths_by_name[name]
                    self._update_db_summary()
                    dlg.destroy()
                    messagebox.showinfo(self.traducir("info"), self.traducir("carpeta_eliminada"))
            
            btn_eliminar = ctk.CTkButton(
                folder_frame,
                text=self.traducir("eliminar"),
                command=eliminar_carpeta,
                width=80,
                height=28,
                fg_color="red",
                hover_color="darkred"
            )
            btn_eliminar.pack(side="right", padx=5)
        
        # Botón cerrar
        btn_cerrar = ctk.CTkButton(
            frame,
            text=self.traducir("cerrar"),
            command=dlg.destroy,
            width=120
        )
        btn_cerrar.pack(pady=(10, 0))

    def _scan_root(self, root, recursive=True, progress_callback=None):
        """
        Escanea una carpeta raíz e indexa los juegos encontrados.
        Si recursive=False, solo escanea el nivel actual (no recursivo).
        progress_callback: función(folders_scanned, games_found) para actualizar progreso
        """
        if not hasattr(self, "_paths_by_tid"):
            self._paths_by_tid = {}
        if not hasattr(self, "_paths_by_name"):
            self._paths_by_name = {}

        folders_scanned = 0
        games_found = 0

        if recursive:
            # Escaneo optimizado: solo la raíz (los juegos están directamente en la carpeta principal)
            # Crear un índice rápido de nombres normalizados de la BD
            bd_names_by_tid = {}
            bd_names_normalized = {}
            for it in _items_by_key.values():
                tid = it["title_id"]
                norm_name = norm_text(it["name"])
                bd_names_by_tid[tid] = norm_name
                bd_names_normalized[norm_name] = it
            
            # Solo escanear el nivel raíz (no recursivo)
            try:
                items = os.listdir(root)
                total_items = len([item for item in items if os.path.isdir(os.path.join(root, item))])
                
                for item in items:
                    item_path = os.path.join(root, item)
                    if not os.path.isdir(item_path):
                        continue
                    
                    folders_scanned += 1
                    if progress_callback and folders_scanned % 50 == 0:
                        progress_callback(folders_scanned, games_found)
                    
                    base = item
                    base_norm = norm_text(base)
                    
                    # Buscar Title ID en el nombre de la carpeta
                    m = re.search(r'([0-9A-Fa-f]{8})', base)
                    if m:
                        tid = m.group(1).upper()
                        self._paths_by_tid.setdefault(tid, set()).add(item_path)
                        games_found += 1
                        
                        # Si encontramos el TID, agregar también el nombre de la BD
                        if tid in bd_names_by_tid:
                            norm_name = bd_names_by_tid[tid]
                            self._paths_by_name.setdefault(norm_name, set()).add(item_path)
                    
                    # Si la carpeta es exactamente un Title ID
                    elif re.fullmatch(r'[0-9A-Fa-f]{8}', base):
                        tid = base.upper()
                        self._paths_by_tid.setdefault(tid, set()).add(item_path)
                        games_found += 1
                        
                        # Si encontramos el TID, agregar también el nombre de la BD
                        if tid in bd_names_by_tid:
                            norm_name = bd_names_by_tid[tid]
                            self._paths_by_name.setdefault(norm_name, set()).add(item_path)
                    
                    # Buscar por nombre de carpeta (coincidencia con nombres de la BD)
                    # Solo si no encontramos por TID
                    else:
                        for norm_name, it in bd_names_normalized.items():
                            # Coincidencia exacta o parcial
                            if norm_name == base_norm or norm_name in base_norm or base_norm in norm_name:
                                self._paths_by_name.setdefault(norm_name, set()).add(item_path)
                                # También agregar el TID si lo tenemos
                                tid = it["title_id"]
                                self._paths_by_tid.setdefault(tid, set()).add(item_path)
                                games_found += 1
                                break  # Solo el primer match para esta carpeta
            except Exception as e:
                print(f"Error escaneando {root}: {e}")
        
        if progress_callback:
            progress_callback(folders_scanned, games_found)
        else:
            # Escaneo solo del nivel actual (rápido para cuando se pega lista)
            try:
                for item in os.listdir(root):
                    item_path = os.path.join(root, item)
                    if os.path.isdir(item_path):
                        # Buscar Title ID en el nombre de la carpeta
                        m = re.search(r'([0-9A-Fa-f]{8})', item)
                        if m:
                            tid = m.group(1).upper()
                            self._paths_by_tid.setdefault(tid, set()).add(item_path)
                        
                        # Indexar por nombre normalizado
                        item_norm = norm_text(item)
                        self._paths_by_name.setdefault(item_norm, set()).add(item_path)
            except Exception:
                pass

        self._update_db_summary()

    def _find_paths_for_tid(self, tid_hex):
        if not hasattr(self, "_paths_by_tid"): return []
        return sorted(list(self._paths_by_tid.get(tid_hex.upper(), [])))

    def _get_selected_tid(self):
        sel = self.tree_title_ids.focus()
        if not sel: return None
        vals = self.tree_title_ids.item(sel, "values")
        return str(vals[0]).strip() if vals else None

    def _open_selected_folder(self):
        tid = self._get_selected_tid()
        if not tid: return
        paths = self._find_paths_for_tid(tid)
        if not paths:
            messagebox.showinfo(self.traducir("info"), self.traducir("no_carpeta_tid")); return
        src = self._choose_path_dialog(paths, title=self.traducir("abrir_carpeta"))
        if not src: return
        try: os.startfile(src)
        except Exception as e: messagebox.showerror(self.traducir("error"), f"{self.traducir('error_busqueda')}\n{e}")

    def _copy_selected_game_folder(self):
        tid = self._get_selected_tid()
        if not tid: return
        paths = self._find_paths_for_tid(tid)
        if not paths:
            messagebox.showinfo(self.traducir("info"), self.traducir("no_carpeta_tid")); return
        src = self._choose_path_dialog(paths, title=self.traducir("elige_carpeta_juego"))
        if not src: return
        dst_root = filedialog.askdirectory(title=self.traducir("elige_destino"))
        if not dst_root: return
        self._copy_items_with_progress([src], dest_base=dst_root, keep_names=True, include_top_dir=True)

    def _choose_path_dialog(self, paths, title=None):
        if not paths: return None
        if len(paths) == 1: return paths[0]
        title = title or self.traducir("elige_carpeta_juego")
        win = ctk.CTkToplevel(self); win.title(title); win.geometry("760x160"); win.grab_set()
        ctk.CTkLabel(win, text=title).pack(pady=(10, 6))
        var = ctk.StringVar(value=paths[0])
        opt = ctk.CTkOptionMenu(win, values=list(paths), variable=var, width=680); opt.pack(pady=6)
        chosen = {"path": None}
        def ok(): chosen["path"] = var.get(); win.destroy()
        ctk.CTkButton(win, text=self.traducir("ok"), command=ok).pack(pady=(8, 10))
        win.wait_window(); return chosen["path"]

    # ---------- Navegación del explorador ----------
    def _update_nav_buttons(self):
        self.btn_back.configure(state=("normal" if self._nav_index > 0 else "disabled"))
        self.btn_forward.configure(state=("normal" if self._nav_index < len(self._nav_history) - 1 else "disabled"))
        folder = getattr(self, "current_folder", None)
        up_enabled = bool(folder and os.path.dirname(folder.rstrip("\\/")) and os.path.dirname(folder.rstrip("\\/")) != folder)
        self.btn_up.configure(state=("normal" if up_enabled else "disabled"))

    def _enter_folder(self, folder, user_initiated=False):
        folder = os.path.normpath(folder)
        if not self._nav_history or self._nav_history[self._nav_index] != folder:
            self._nav_history = self._nav_history[: self._nav_index + 1]
            self._nav_history.append(folder); self._nav_index += 1
        self._list_folder(folder); self._update_nav_buttons()
        # Si el usuario navegó manualmente, marcar como cambio manual
        if user_initiated:
            self._user_changed_folder = True

    def _nav_back(self):
        if self._nav_index > 0:
            self._nav_index -= 1
            self._enter_folder(self._nav_history[self._nav_index], user_initiated=True)

    def _nav_forward(self):
        if self._nav_index < len(self._nav_history) - 1:
            self._nav_index += 1
            self._enter_folder(self._nav_history[self._nav_index], user_initiated=True)

    # ---------- Explorador ----------
    def _browse_selected_game(self):
        tid = self._get_selected_tid()
        if not tid: return
        paths = self._find_paths_for_tid(tid)
        if not paths:
            messagebox.showinfo(self.traducir("info"), self.traducir("no_carpeta_tid")); return
        src = self._choose_path_dialog(paths, title=self.traducir("ver_archivos"))
        if not src: return
        self._enter_folder(src, user_initiated=True)

    def _get_game_name_for_path(self, path):
        """Obtiene el nombre del juego basado en el Title ID encontrado en la ruta"""
        # Buscar Title ID en el nombre de la carpeta o en el path
        base = os.path.basename(path)
        m = re.search(r'([0-9A-Fa-f]{8})', base)
        if m:
            tid = m.group(1).upper()
            # Buscar en el índice de TIDs
            if tid in _index_tid:
                # Tomar el primer resultado (puede haber múltiples por consola)
                game_item = _index_tid[tid][0]
                return game_item.get("name", "")
        return ""

    def _list_folder(self, folder):
        try: self._size_thread_stop.set()
        except Exception: pass
        self._size_thread_stop = threading.Event()

        self.current_folder = folder
        self.path_label.configure(text=f"{self.traducir('ruta')} {folder}")
        # Ocultar hint cuando hay una carpeta abierta
        if hasattr(self, 'explorer_hint'):
            self.explorer_hint.pack_forget()

        entries = []
        try:
            with os.scandir(folder) as it:
                for e in it:
                    is_dir = e.is_dir()
                    try:
                        stat = e.stat()
                        mtime = stat.st_mtime
                        size = (stat.st_size if not is_dir else None)
                    except Exception:
                        mtime, size = 0, None
                    if is_dir and e.path in self._folder_size_cache:
                        size = self._folder_size_cache[e.path]
                    ftype = "Carpeta" if is_dir else "Archivo"
                    # Obtener nombre del juego si es una carpeta
                    game_name = self._get_game_name_for_path(e.path) if is_dir else ""
                    # Normalizar el path para asegurar coincidencias exactas
                    path_norm = os.path.normpath(e.path)
                    entries.append((e.name, game_name, ftype, size, mtime, path_norm))

            # Ordenar según el criterio seleccionado
            self._sort_entries(entries)
            self._current_entries = entries
            self._render_files(entries)
            self._clear_files_filter()
            self._start_dirsize_worker(entries, folder, self._size_thread_stop)
            self._update_counts()

        except Exception as e:
            messagebox.showerror(self.traducir("error"), str(e))

    def _sort_entries(self, entries):
        """Ordena las entradas según el criterio seleccionado"""
        sort_order = self._sort_value_map.get(self.sort_order_var.get(), "nombre")
        
        if sort_order == "nombre":
            # Ordenar por tipo (carpetas primero) y luego por nombre
            entries.sort(key=lambda x: (x[2] != "Carpeta", x[0].lower()))
        elif sort_order == "tamano":
            # Ordenar por tipo (carpetas primero) y luego por tamaño (mayor primero)
            # Manejar None como 0 para elementos sin tamaño calculado
            entries.sort(key=lambda x: (x[2] != "Carpeta", -(x[3] if x[3] is not None else 0), x[0].lower()))
        elif sort_order == "tipo":
            # Ordenar por tipo y luego por nombre
            entries.sort(key=lambda x: (x[2], x[0].lower()))
        elif sort_order == "modificado":
            # Ordenar por tipo (carpetas primero) y luego por fecha de modificación (más reciente primero)
            entries.sort(key=lambda x: (x[2] != "Carpeta", -x[4], x[0].lower()))

    def _on_sort_changed(self, value):
        """Se llama cuando cambia el criterio de ordenamiento"""
        if hasattr(self, "_current_entries") and self._current_entries:
            # Reordenar las entradas actuales
            self._sort_entries(self._current_entries)
            # Re-renderizar
            self._render_files(self._current_entries)

    def _apply_files_filter(self, debounce=False):
        if debounce:
            if self._filter_job:
                try: self.after_cancel(self._filter_job)
                except Exception: pass
            self._filter_job = self.after(250, self._apply_files_filter); return

        self._filter_job = None
        q = self.files_filter_var.get().strip().lower()
        entries = self._current_entries or []
        if not q: self._render_files(entries); return

        filtered = []
        for name, game_name, ftype, size, mtime, path in entries:
            if (q in name.lower()) or (q in game_name.lower()) or (q in ftype.lower()) or (q in path.lower()):
                filtered.append((name, game_name, ftype, size, mtime, path))
        self._render_files(filtered)

    def _clear_files_filter(self):
        self.files_filter_var.set("")
        if self._current_entries: self._render_files(self._current_entries)

    def _update_counts(self):
        # Verificar que _checked_paths existe (por si se llama antes de la inicialización completa)
        if not hasattr(self, '_checked_paths'):
            return
        # seleccionados visibles
        sel_count = len(self.tree_files.selection())
        # marcados visibles
        marked_visible = 0
        for row in self.tree_files.get_children():
            vals = self.tree_files.item(row, "values")
            if not vals: continue
            path = vals[-1]
            if path in self._checked_paths:
                marked_visible += 1
        # Total de marcados (solo paths que existen, igual que en "Generar lista marcados")
        total_marked = len([p for p in self._checked_paths if os.path.exists(p)])
        # Mostrar "visibles (de total)" si hay diferencia, o solo el total si son iguales
        if total_marked > marked_visible:
            self.counts_label.configure(
                text=f"  |  {self.traducir('seleccionados')}: {sel_count}  |  {self.traducir('marcados')}: {marked_visible} (de {total_marked} totales)"
            )
        else:
            self.counts_label.configure(
                text=f"  |  {self.traducir('seleccionados')}: {sel_count}  |  {self.traducir('marcados')}: {total_marked}"
            )

    def _on_tree_files_click(self, event):
        # Toggle de check si se clickea la primera columna
        region = self.tree_files.identify("region", event.x, event.y)
        if region != "cell": return
        col = self.tree_files.identify_column(event.x)  # '#1' es 'mark'
        if col != "#1": return
        row = self.tree_files.identify_row(event.y)
        if not row: return "break"
        vals = self.tree_files.item(row, "values")
        if not vals: return "break"
        # Valores: mark, name, game_name, type, size, modified, path
        path = vals[-1]  # path es siempre el último
        path_norm = os.path.normpath(path)
        # toggle
        if path_norm in self._checked_paths:
            self._checked_paths.remove(path_norm); new_mark = "☐"
        else:
            self._checked_paths.add(path_norm); new_mark = "☑"
        self.tree_files.set(row, "mark", new_mark)
        self._update_counts()
        return "break"  # evita seleccionar fila al hacer clic en el check

    def _mark_visible_rows(self):
        for row in self.tree_files.get_children():
            vals = self.tree_files.item(row, "values")
            if not vals: continue
            path = vals[-1]
            path_norm = os.path.normpath(path)
            self._checked_paths.add(path_norm)
            self.tree_files.set(row, "mark", "☑")
        self._update_counts()

    def _unmark_visible_rows(self):
        for row in self.tree_files.get_children():
            vals = self.tree_files.item(row, "values")
            if not vals: continue
            path = vals[-1]
            path_norm = os.path.normpath(path)
            if path_norm in self._checked_paths: self._checked_paths.remove(path_norm)
            self.tree_files.set(row, "mark", "☐")
        self._update_counts()

    def _select_all_files(self):
        """Selecciona todas las filas visibles y las marca con check"""
        all_items = self.tree_files.get_children()
        if not all_items:
            return
        # Seleccionar todas las filas
        self.tree_files.selection_set(all_items)
        # Marcar todas con check
        for row in all_items:
            vals = self.tree_files.item(row, "values")
            if not vals: continue
            path = vals[-1]
            path_norm = os.path.normpath(path)
            self._checked_paths.add(path_norm)
            self.tree_files.set(row, "mark", "☑")
        self._update_counts()

    def _limpiar_lista_cargada(self):
        """Limpia todos los checks y reinicia la vista del explorador"""
        # Limpiar todos los checks
        self._checked_paths.clear()
        # Refrescar la vista actual si hay entradas
        if getattr(self, "_current_entries", None):
            self._render_files(self._current_entries)
        # Limpiar selección
        self.tree_files.selection_remove(self.tree_files.selection())
        # Resetear el flag de cambio manual
        self._user_changed_folder = False
        # Actualizar contadores
        self._update_counts()
        self.status_label.configure(text="Lista limpiada", text_color="green")

    def _open_or_enter(self):
        sel = self.tree_files.focus()
        if not sel: return
        vals = self.tree_files.item(sel, "values")
        if not vals: return
        # Valores: mark, name, game_name, type, size, modified, path
        path = vals[-1]  # path es siempre el último
        try:
            if os.path.isdir(path): self._enter_folder(path, user_initiated=True)
            else: os.startfile(path)
        except Exception as e:
            messagebox.showerror(self.traducir("error"), str(e))

    def _open_selected_files(self):
        sels = self.tree_files.selection()
        for sid in sels:
            vals = self.tree_files.item(sid, "values")
            if not vals: continue
            path = vals[-1]
            try: os.startfile(path)
            except Exception as e: messagebox.showerror(self.traducir("error"), str(e))

    def _show_selected_in_explorer(self):
        sels = self.tree_files.selection()
        if not sels: return
        path = self.tree_files.item(sels[0], "values")[-1]
        try:
            if os.path.isdir(path): os.startfile(path)
            else: os.startfile(os.path.dirname(path))
        except Exception as e:
            messagebox.showerror(self.traducir("error"), str(e))

    def _go_up(self):
        folder = getattr(self, "current_folder", None)
        if not folder: return
        parent = os.path.dirname(folder.rstrip("\\/"))
        if parent and parent != folder: self._enter_folder(parent, user_initiated=True)

    def _open_current_in_explorer(self):
        folder = getattr(self, "current_folder", None)
        if not folder: return
        try: os.startfile(folder)
        except Exception as e: messagebox.showerror(self.traducir("error"), str(e))

    def _change_browser_folder(self):
        folder = filedialog.askdirectory(title=self.traducir("cambiar_carpeta"))
        if not folder:
            return
        
        # Verificar si hay una carpeta indexada y si es diferente a la seleccionada
        has_indexed = hasattr(self, "_scan_roots") and self._scan_roots
        indexed_path = self._scan_roots[0] if has_indexed else None
        folder_norm = os.path.normpath(folder)
        indexed_norm = os.path.normpath(indexed_path) if indexed_path else None
        
        # Si hay una carpeta indexada diferente, preguntar si quiere indexar la nueva carpeta
        if has_indexed and indexed_norm != folder_norm:
            respuesta = messagebox.askyesno(
                self.traducir("info"),
                f"La carpeta indexada actual es:\n{indexed_path}\n\n"
                f"¿Deseas indexar la nueva carpeta seleccionada?\n{folder}\n\n"
                f"(Esto reemplazará la carpeta indexada actual)"
            )
            if respuesta:
                # Indexar la nueva carpeta directamente (esto limpiará todo y la indexará)
                self._index_folder_directly(folder)
                return  # _index_folder_directly ya navegará a la carpeta
        
        # Si no quiere indexar o no hay carpeta indexada, solo cambiar la vista del explorador
        # Crear diálogo de progreso
        dlg = ctk.CTkToplevel(self)
        dlg.title(self.traducir("cambiar_carpeta"))
        dlg.geometry("500x200")
        dlg.transient(self)
        dlg.grab_set()
        
        frame = ctk.CTkFrame(dlg)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Label de estado
        status_label_dlg = ctk.CTkLabel(
            frame,
            text="Cargando carpeta...",
            font=ctk.CTkFont(size=12)
        )
        status_label_dlg.pack(pady=(0, 10))
        
        # Barra de progreso (indeterminada)
        progress_bar = ctk.CTkProgressBar(frame, width=460, mode="indeterminate")
        progress_bar.pack(pady=(0, 10))
        progress_bar.start()
        
        # Label de detalle
        detail_label = ctk.CTkLabel(
            frame,
            text="Escaneando archivos...",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        detail_label.pack()
        
        def load_folder():
            try:
                # Actualizar mensaje
                self.after(0, lambda: (
                    status_label_dlg.configure(text="Cargando carpeta..."),
                    detail_label.configure(text="Escaneando archivos y carpetas...")
                ))
                # Cargar la carpeta (esto puede tardar si hay muchos archivos)
                self._enter_folder(folder, user_initiated=True)
                # Cerrar diálogo cuando termine
                self.after(0, dlg.destroy)
            except Exception as e:
                self.after(0, lambda: (
                    dlg.destroy(),
                    messagebox.showerror(self.traducir("error"), f"Error al cargar carpeta:\n{e}")
                ))
        
        # Función para verificar si terminó (por si el diálogo no se cierra automáticamente)
        def check_done():
            try:
                if not dlg.winfo_exists():
                    return
                # Verificar si la carpeta ya se cargó (current_folder coincide)
                if hasattr(self, 'current_folder') and os.path.normpath(self.current_folder) == folder_norm:
                    progress_bar.stop()
                    dlg.destroy()
                else:
                    dlg.after(100, check_done)
            except:
                pass
        
        check_done()
        
        # Ejecutar en hilo separado
        threading.Thread(target=load_folder, daemon=True).start()

    # ---------- Worker: tamaños de carpeta ----------
    def _start_dirsize_worker(self, entries, folder, stop_event: threading.Event):
        def dir_size(p: str) -> int:
            total = 0
            for root, _dirs, files in os.walk(p):
                if stop_event.is_set(): return -1
                for f in files:
                    fp = os.path.join(root, f)
                    try: total += os.path.getsize(fp)
                    except Exception: pass
            return total

        def worker():
            for _name, _game_name, _ftype, size, _mt, path in entries:
                if stop_event.is_set(): return
                if not os.path.isdir(path): continue
                if size is not None: continue
                total = dir_size(path)
                if total < 0 or stop_event.is_set(): return
                self._folder_size_cache[path] = total
                def _apply():
                    if getattr(self, "current_folder", None) != folder: return
                    # Actualizar el tamaño en _current_entries
                    if hasattr(self, "_current_entries"):
                        for i, entry in enumerate(self._current_entries):
                            if entry[5] == path:  # path es el último elemento (índice 5)
                                # Actualizar la tupla: (name, game_name, ftype, size, mtime, path)
                                self._current_entries[i] = (entry[0], entry[1], entry[2], total, entry[4], entry[5])
                                break
                    # Actualizar la visualización
                    row_id = self._files_row_by_path.get(path)
                    if row_id: self.tree_files.set(row_id, "size", fmt_size(total))
                    # Si está ordenando por tamaño, reordenar
                    if hasattr(self, "sort_order_var"):
                        sort_order = self._sort_value_map.get(self.sort_order_var.get(), "nombre")
                        if sort_order == "tamano":
                            self._sort_entries(self._current_entries)
                            self._render_files(self._current_entries)
                try: self.after(0, _apply)
                except Exception: pass

        self._size_thread = threading.Thread(target=worker, daemon=True); self._size_thread.start()

    # ---------- Copias ----------
    def _copy_selected_rows_browser(self):
        """
        Copia lo que esté seleccionado en la tabla de archivos (self.tree_files).
        Muestra una ventana de confirmación antes de copiar.
        """
        rows = self.tree_files.selection()
        if not rows:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado"))
            return

        items = []
        for row in rows:
            vals = self.tree_files.item(row, "values")
            if not vals:
                continue
            # La última columna ('path') es la ruta absoluta
            path = vals[-1]
            if path and os.path.exists(path):
                items.append(path)

        if not items:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado"))
            return

        # Mostrar ventana de confirmación
        confirmed_items = self._show_copy_confirmation_dialog(items)
        if not confirmed_items:
            return

        dst_root = filedialog.askdirectory(title=self.traducir("elige_destino"))
        if not dst_root:
            return

        self._copy_items_with_progress(confirmed_items, dest_base=dst_root, keep_names=True, include_top_dir=True)

    def _show_copy_confirmation_dialog(self, items):
        """
        Muestra una ventana de confirmación con los juegos seleccionados.
        Permite desmarcar algunos antes de copiar.
        Retorna la lista de items marcados para copiar, o None si se cancela.
        """
        if not items:
            return None
        
        # Preparar datos: Title ID, Nombre, Tamaño, Path
        game_data = []
        for path in items:
            if not os.path.exists(path):
                continue
            
            # Obtener Title ID del nombre de la carpeta
            base = os.path.basename(path)
            tid = ""
            m = re.search(r'([0-9A-Fa-f]{8})', base)
            if m:
                tid = m.group(1).upper()
            
            # Obtener nombre del juego
            game_name = ""
            if tid and tid in _index_tid:
                game_name = _index_tid[tid][0].get("name", "")
            elif not game_name:
                game_name = self._get_game_name_for_path(path)
            
            # Calcular tamaño (usar cache si está disponible, sino calcular)
            total_size = 0
            if os.path.isdir(path):
                if path in self._folder_size_cache:
                    total_size = self._folder_size_cache[path]
                else:
                    # Usar tamaño de "Calculando..." como placeholder, se calculará después
                    total_size = -1  # Marcador para calcular después
            else:
                try:
                    total_size = os.path.getsize(path)
                except:
                    total_size = 0
            
            game_data.append({
                'tid': tid or "N/A",
                'name': game_name or base,
                'size': total_size,
                'path': path,
                'selected': True
            })
        
        if not game_data:
            return None
        
        # Crear ventana de confirmación
        dlg = ctk.CTkToplevel(self)
        dlg.title("Confirmar copia")
        dlg.geometry("900x600")
        dlg.grab_set()
        
        # Título y resumen
        total_size = sum(g['size'] for g in game_data if g['size'] >= 0)
        total_size_str = fmt_size(total_size) if total_size > 0 else "Calculando..."
        ctk.CTkLabel(dlg, text=f"Juegos seleccionados para copiar ({len(game_data)}):", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        header_label = ctk.CTkLabel(dlg, text=f"Tamaño total: {total_size_str}", 
                    font=ctk.CTkFont(size=12))
        header_label.pack(pady=(0, 10))
        
        # Frame para la tabla con scroll
        table_frame = ctk.CTkFrame(dlg)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Treeview para mostrar los juegos
        columns = ("sel", "tid", "name", "size")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15, selectmode="none")
        tree.heading("sel", text="✓")
        tree.heading("tid", text="Title ID")
        tree.heading("name", text="Nombre del juego")
        tree.heading("size", text="Tamaño")
        
        tree.column("sel", width=50, anchor="center")
        tree.column("tid", width=120, anchor="center")
        tree.column("name", width=500, anchor="w")
        tree.column("size", width=120, anchor="e")
        
        # Scrollbars
        sb_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        sb_x = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        sb_y.grid(row=0, column=1, sticky="ns")
        sb_x.grid(row=1, column=0, sticky="ew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Insertar datos
        row_ids = {}
        items_to_calculate = []
        for i, game in enumerate(game_data):
            mark = "☑" if game['selected'] else "☐"
            if game['size'] == -1:
                size_str = "Calculando..."
                items_to_calculate.append((i, game['path']))
            else:
                size_str = fmt_size(game['size'])
            row_id = tree.insert("", "end", values=(mark, game['tid'], game['name'], size_str))
            row_ids[row_id] = i
        
        # Calcular tamaños en segundo plano si es necesario
        if items_to_calculate:
            def calculate_sizes():
                for idx, path in items_to_calculate:
                    if not os.path.isdir(path):
                        continue
                    total = 0
                    try:
                        for root, dirs, files in os.walk(path):
                            for f in files:
                                try:
                                    total += os.path.getsize(os.path.join(root, f))
                                except:
                                    pass
                    except:
                        pass
                    game_data[idx]['size'] = total
                    # Actualizar en la UI
                    for row_id, data_idx in row_ids.items():
                        if data_idx == idx:
                            tree.set(row_id, "size", fmt_size(total))
                            # Actualizar tamaño total si está seleccionado
                            if game_data[idx]['selected']:
                                selected_size = sum(g['size'] for g in game_data if g['selected'] and g['size'] >= 0)
                                dlg.after(0, lambda s=selected_size: total_label.configure(
                                    text=f"Tamaño total seleccionado: {fmt_size(s)}"
                                ))
                                # Actualizar también el tamaño total en el header
                                total_size = sum(g['size'] for g in game_data if g['size'] >= 0)
                                dlg.after(0, lambda t=total_size: header_label.configure(
                                    text=f"Tamaño total: {fmt_size(t)}"
                                ))
                            break
            
            threading.Thread(target=calculate_sizes, daemon=True).start()
        
        # Función para toggle de check
        def toggle_check(event):
            region = tree.identify("region", event.x, event.y)
            if region != "cell":
                return
            col = tree.identify_column(event.x)
            if col != "#1":  # Solo la primera columna (sel)
                return
            row = tree.identify_row(event.y)
            if not row or row not in row_ids:
                return
            idx = row_ids[row]
            game_data[idx]['selected'] = not game_data[idx]['selected']
            new_mark = "☑" if game_data[idx]['selected'] else "☐"
            tree.set(row, "sel", new_mark)
            # Actualizar tamaño total seleccionado (solo contar los que tienen tamaño calculado)
            selected_size = sum(g['size'] for g in game_data if g['selected'] and g['size'] >= 0)
            if selected_size > 0:
                total_label.configure(text=f"Tamaño total seleccionado: {fmt_size(selected_size)}")
            else:
                total_label.configure(text="Tamaño total seleccionado: Calculando...")
            return "break"
        
        tree.bind("<Button-1>", toggle_check)
        
        # Label para tamaño total seleccionado
        selected_size = sum(g['size'] for g in game_data if g['selected'] and g['size'] >= 0)
        selected_size_str = fmt_size(selected_size) if selected_size > 0 else "Calculando..."
        total_label = ctk.CTkLabel(dlg, text=f"Tamaño total seleccionado: {selected_size_str}", 
                                   font=ctk.CTkFont(size=12))
        total_label.pack(pady=(5, 10))
        
        # Botones
        btn_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_frame.pack(pady=(0, 10))
        
        result = {"confirmed": False, "items": []}
        
        def on_confirm():
            result["items"] = [g['path'] for g in game_data if g['selected']]
            result["confirmed"] = True
            dlg.destroy()
        
        def on_cancel():
            result["confirmed"] = False
            dlg.destroy()
        
        ctk.CTkButton(btn_frame, text="Copiar seleccionados", command=on_confirm, 
                     width=150).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancelar", command=on_cancel, 
                     width=120).pack(side="left", padx=5)
        
        dlg.wait_window()
        
        if result["confirmed"] and result["items"]:
            return result["items"]
        return None

    def _copy_checked_items_from_browser(self):
        """
        Copia TODO lo marcado (aunque no esté visible) usando el copiador nativo.
        Muestra una ventana de confirmación antes de copiar.
        """
        if not self._checked_paths:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado"))
            return

        items = [p for p in self._checked_paths if os.path.exists(p)]
        if not items:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado"))
            return

        # Mostrar ventana de confirmación
        confirmed_items = self._show_copy_confirmation_dialog(items)
        if not confirmed_items:
            return

        dst_root = filedialog.askdirectory(title=self.traducir("elige_destino"))
        if not dst_root:
            return

        # Guardar información del destino para el log
        self._last_copy_destination = dst_root
        self._last_copy_sources = confirmed_items
        self._copy_items_with_progress(confirmed_items, dest_base=dst_root, keep_names=True, include_top_dir=True)

    def _comparar_ubicacion_destino(self):
        """
        Compara los juegos en una ubicación destino con la lista cargada.
        Marca solo los que faltan o tienen diferencias de tamaño.
        """
        if not hasattr(self, "original_game_names") or not self.original_game_names:
            messagebox.showinfo(
                self.traducir("info"),
                "Primero debes cargar una lista de juegos (Pegar lista)"
            )
            return

        # Seleccionar carpeta destino
        dest_folder = filedialog.askdirectory(title=self.traducir("seleccionar_ubicacion_destino"))
        if not dest_folder:
            return

        # Crear diálogo de progreso
        dlg = ctk.CTkToplevel(self)
        dlg.title(self.traducir("comparando_ubicacion"))
        dlg.geometry("500x200")
        dlg.transient(self)
        dlg.grab_set()

        frame = ctk.CTkFrame(dlg)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        status_label = ctk.CTkLabel(
            frame,
            text=self.traducir("comparando_ubicacion"),
            font=ctk.CTkFont(size=12)
        )
        status_label.pack(pady=(0, 10))

        progress_bar = ctk.CTkProgressBar(frame, width=460, mode="determinate")
        progress_bar.pack(pady=(0, 10))
        progress_bar.set(0)

        detail_label = ctk.CTkLabel(
            frame,
            text="Escaneando carpeta destino...",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        detail_label.pack()

        state = {"done": False, "found": [], "missing": [], "size_diff": [], "total_dest": 0}

        def compare_in_thread():
            # _index_tid y _index_name están definidos globalmente en este módulo
            # norm_text también está disponible globalmente
            
            # Normalizar nombres de la lista original
            original_normalized = {}
            for name in self.original_game_names:
                norm = norm_text(name)
                original_normalized[norm] = name

            # Escanear carpeta destino (solo primer nivel, sin recursión)
            dest_games = {}  # {normalized_name: (path, size)}
            
            # Crear índice invertido de _index_name para búsquedas rápidas
            index_name_dict = {}
            for nname, game_item in _index_name:
                # Crear múltiples claves para búsqueda rápida
                words = nname.split()
                for word in words:
                    if len(word) > 2:  # Solo palabras significativas
                        if word not in index_name_dict:
                            index_name_dict[word] = []
                        index_name_dict[word].append((nname, game_item))
            
            def get_game_name_fast(item_name):
                """Obtiene el nombre del juego de forma rápida"""
                # 1. Buscar por Title ID (más rápido)
                tid_match = re.search(r'([0-9A-Fa-f]{8})', item_name, re.IGNORECASE)
                if tid_match:
                    tid = tid_match.group(1).upper()
                    if tid in _index_tid:
                        return _index_tid[tid][0].get("name", "")
                
                # 2. Buscar por nombre usando índice invertido
                base_name = os.path.splitext(item_name)[0]
                norm_base = norm_text(base_name)
                base_words = [w for w in norm_base.split() if len(w) > 2]
                
                if base_words:
                    # Buscar en índice invertido
                    candidates = {}
                    for word in base_words:
                        if word in index_name_dict:
                            for nname, game_item in index_name_dict[word]:
                                if nname not in candidates:
                                    candidates[nname] = game_item
                    
                    # Encontrar la mejor coincidencia
                    for nname, game_item in candidates.items():
                        if norm_base == nname or norm_base in nname or nname in norm_base:
                            return game_item.get("name", "")
                
                # 3. Búsqueda lineal como último recurso (solo si no se encontró)
                for nname, game_item in _index_name:
                    if nname == norm_base or norm_base in nname or nname in norm_base:
                        return game_item.get("name", "")
                
                return None
            
            def calculate_size_fast(path):
                """Calcula el tamaño de forma rápida usando cache si existe"""
                # Intentar usar cache primero
                if hasattr(self, "_folder_size_cache") and path in self._folder_size_cache:
                    return self._folder_size_cache[path]
                
                # Calcular tamaño
                try:
                    total = 0
                    for root, _, files in os.walk(path):
                        for f in files:
                            try:
                                total += os.path.getsize(os.path.join(root, f))
                            except Exception:
                                pass
                    # Guardar en cache
                    if hasattr(self, "_folder_size_cache"):
                        self._folder_size_cache[path] = total
                    return total
                except Exception:
                    return 0
            
            # Escanear solo el primer nivel (no recursivo)
            self.after(0, lambda: detail_label.configure(text="Escaneando carpeta destino (solo primer nivel)..."))
            try:
                items = os.listdir(dest_folder)
                total_items = len([item for item in items if os.path.isdir(os.path.join(dest_folder, item))])
                processed = 0
                
                for item in items:
                    item_path = os.path.join(dest_folder, item)
                    if os.path.isdir(item_path):
                        processed += 1
                        # Actualizar progreso cada 10 carpetas
                        if processed % 10 == 0 or processed == total_items:
                            progress = 0.3 + (processed / total_items) * 0.2  # 30% a 50% del progreso total
                            self.after(0, lambda p=progress, proc=processed, tot=total_items: (
                                progress_bar.set(p),
                                detail_label.configure(text=f"Escaneando... {proc}/{tot} carpetas")
                            ))
                        
                        # Obtener nombre del juego (rápido)
                        game_name = get_game_name_fast(item)
                        if not game_name:
                            game_name = item
                        
                        # NO calcular tamaño aquí - se calculará solo si es necesario durante la comparación
                        # Esto hace el escaneo mucho más rápido
                        size = None  # Se calculará después si es necesario
                        
                        norm_name = norm_text(game_name)
                        if norm_name not in dest_games:
                            dest_games[norm_name] = []
                        dest_games[norm_name].append((item_path, size))
            except Exception as e:
                pass
            
            state["total_dest"] = len(dest_games)

            # Comparar con lista original
            self.after(0, lambda: detail_label.configure(text="Comparando con lista original..."))
            progress_bar.set(0.5)

            missing = []
            size_diff = []
            found = []

            # Comparar y calcular tamaños solo cuando sea necesario
            total_to_compare = len(original_normalized)
            compared = 0
            
            for norm_name, original_name in original_normalized.items():
                compared += 1
                # Actualizar progreso
                if compared % 10 == 0 or compared == total_to_compare:
                    progress = 0.5 + (compared / total_to_compare) * 0.5  # 50% a 100%
                    self.after(0, lambda p=progress, c=compared, t=total_to_compare: (
                        progress_bar.set(p),
                        detail_label.configure(text=f"Comparando... {c}/{t} juegos")
                    ))
                
                if norm_name in dest_games:
                    # Juego encontrado, verificar tamaño
                    dest_paths = dest_games[norm_name]
                    # Buscar el tamaño en la ubicación origen (si está indexado)
                    source_size = None
                    if hasattr(self, "_paths_by_name"):
                        for path in self._paths_by_name.get(original_name, []):
                            if os.path.exists(path):
                                # Usar cache si existe
                                if hasattr(self, "_folder_size_cache") and path in self._folder_size_cache:
                                    source_size = self._folder_size_cache[path]
                                else:
                                    try:
                                        source_size = sum(
                                            os.path.getsize(os.path.join(root, f))
                                            for root, _, files in os.walk(path)
                                            for f in files
                                        )
                                        # Guardar en cache
                                        if hasattr(self, "_folder_size_cache"):
                                            self._folder_size_cache[path] = source_size
                                    except Exception:
                                        pass
                                if source_size is not None:
                                    break
                    
                    # Comparar tamaños solo si tenemos tamaño origen
                    if source_size is not None:
                        for dest_path, dest_size in dest_paths:
                            # Calcular tamaño destino solo si es necesario (si es None)
                            if dest_size is None:
                                dest_size = calculate_size_fast(dest_path)
                                # Actualizar en el diccionario
                                for i, (dp, ds) in enumerate(dest_paths):
                                    if dp == dest_path:
                                        dest_paths[i] = (dest_path, dest_size)
                                        break
                            
                            if abs(dest_size - source_size) > 1024 * 1024:  # Diferencia > 1MB
                                size_diff.append((original_name, dest_path, source_size, dest_size))
                    else:
                        # No se puede comparar tamaño, pero está presente
                        found.append(original_name)
                else:
                    # Juego faltante
                    missing.append(original_name)

            state["missing"] = missing
            state["size_diff"] = size_diff
            state["found"] = found
            state["done"] = True

            # Marcar los faltantes y con diferencia de tamaño
            self.after(0, lambda: (
                progress_bar.set(1.0),
                detail_label.configure(text="Marcando faltantes y con diferencias..."),
                self._marcar_faltantes_y_diferencias(missing, size_diff, state),
                dlg.destroy(),
                self._mostrar_resultado_comparacion(state)
            ))

        threading.Thread(target=compare_in_thread, daemon=True).start()

    def _marcar_faltantes_y_diferencias(self, missing, size_diff, state):
        """Marca los juegos faltantes y con diferencias de tamaño"""
        # Limpiar marcados actuales
        self._checked_paths.clear()

        # Marcar faltantes
        if hasattr(self, "_paths_by_name") and self._paths_by_name:
            for name in missing:
                # Normalizar nombre para búsqueda
                norm_name = norm_text(name)
                found_paths = False
                
                # Buscar exacto primero
                if norm_name in self._paths_by_name:
                    for path in self._paths_by_name[norm_name]:
                        path_norm = os.path.normpath(path)
                        if os.path.exists(path_norm):
                            self._checked_paths.add(path_norm)
                            found_paths = True
                
                # Si no se encontró, búsqueda flexible por palabras
                if not found_paths:
                    name_words = [w for w in norm_name.split() if len(w) > 2]
                    if name_words:
                        for key_name, paths in self._paths_by_name.items():
                            # Verificar si al menos 2 palabras coinciden
                            matching_words = sum(1 for w in name_words if w in key_name)
                            if matching_words >= min(2, len(name_words)):
                                for path in paths:
                                    path_norm = os.path.normpath(path)
                                    if os.path.exists(path_norm):
                                        self._checked_paths.add(path_norm)
                                        found_paths = True
                                if found_paths:
                                    break

        # Marcar con diferencias de tamaño
        for name, dest_path, source_size, dest_size in size_diff:
            if hasattr(self, "_paths_by_name") and self._paths_by_name:
                # Normalizar nombre
                norm_name = norm_text(name)
                found_paths = False
                
                # Buscar exacto primero
                if norm_name in self._paths_by_name:
                    for path in self._paths_by_name[norm_name]:
                        path_norm = os.path.normpath(path)
                        if os.path.exists(path_norm):
                            self._checked_paths.add(path_norm)
                            found_paths = True
                
                # Si no se encontró, búsqueda flexible
                if not found_paths:
                    name_words = [w for w in norm_name.split() if len(w) > 2]
                    if name_words:
                        for key_name, paths in self._paths_by_name.items():
                            matching_words = sum(1 for w in name_words if w in key_name)
                            if matching_words >= min(2, len(name_words)):
                                for path in paths:
                                    path_norm = os.path.normpath(path)
                                    if os.path.exists(path_norm):
                                        self._checked_paths.add(path_norm)
                                        found_paths = True
                                if found_paths:
                                    break

        # Actualizar UI
        self._update_counts()
        # Refrescar la vista actual para mostrar los marcados
        current_folder = getattr(self, "current_folder", None)
        if current_folder:
            self._list_folder(current_folder)
        else:
            self._refresh_current_folder()

    def _mostrar_resultado_comparacion(self, state):
        """Muestra el resultado de la comparación"""
        msg = (
            f"{self.traducir('comparacion_completada')}\n\n"
            f"{self.traducir('juegos_encontrados_destino').format(count=state['total_dest'])}\n"
            f"{self.traducir('juegos_faltantes').format(count=len(state['missing']))}\n"
            f"{self.traducir('juegos_diferencia_tamano').format(count=len(state['size_diff']))}\n\n"
            f"Se han marcado {len(state['missing']) + len(state['size_diff'])} juegos para copiar."
        )
        messagebox.showinfo(self.traducir("comparacion_completada"), msg)
        self.status_label.configure(
            text=f"{self.traducir('comparacion_completada')} - {len(state['missing'])} faltantes, {len(state['size_diff'])} con diferencias",
            text_color="green"
        )

    def _get_transfer_log_path(self):
        """Obtiene la ruta del archivo de log de transferencias"""
        import tempfile
        log_dir = os.path.join(tempfile.gettempdir(), "xbox_game_finder")
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, "transfer_log.json")

    def _save_transfer_log(self, sources, destination, copied_files):
        """Guarda un log de la transferencia"""
        log_path = self._get_transfer_log_path()
        log_data = {
            "timestamp": time.time(),
            "destination": destination,
            "sources": sources,
            "copied_files": copied_files
        }
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            return log_path
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el log: {e}")
            return None

    def _load_transfer_log(self):
        """Carga el log de transferencias"""
        log_path = self._get_transfer_log_path()
        if not os.path.exists(log_path):
            return None
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def _restaurar_desde_log(self):
        """Elimina los archivos que se copiaron según el log"""
        log_data = self._load_transfer_log()
        if not log_data:
            messagebox.showinfo(self.traducir("info"), self.traducir("log_vacio"))
            return

        copied_files = log_data.get("copied_files", [])
        if not copied_files:
            messagebox.showinfo(self.traducir("info"), self.traducir("log_vacio"))
            return

        respuesta = messagebox.askyesno(
            "Restaurar desde log",
            f"¿Estás seguro de que deseas eliminar {len(copied_files)} archivo(s)/carpeta(s) que se copiaron?\n\n"
            f"Destino: {log_data.get('destination', 'N/A')}\n\n"
            "Esta acción no se puede deshacer."
        )
        if not respuesta:
            return

        deleted = 0
        failed = 0
        errors = []

        for file_path in copied_files:
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                deleted += 1
            except Exception as e:
                failed += 1
                errors.append(f"{os.path.basename(file_path)}: {str(e)}")

        msg = f"{self.traducir('log_restaurado').format(deleted=deleted)}"
        if failed > 0:
            msg += f"\n{failed} elemento(s) no se pudieron eliminar"
        messagebox.showinfo("Restauración completada", msg)
        self.status_label.configure(
            text=f"Log restaurado: {deleted} elementos eliminados",
            text_color="green"
        )

    def _continuar_desde_log(self):
        """Marca solo los archivos que faltan según el log"""
        log_data = self._load_transfer_log()
        if not log_data:
            messagebox.showinfo(self.traducir("info"), self.traducir("log_vacio"))
            return

        sources = log_data.get("sources", [])
        copied_files = log_data.get("copied_files", [])
        destination = log_data.get("destination", "")

        if not sources:
            messagebox.showinfo(self.traducir("info"), "El log no contiene información de origen")
            return

        # Crear conjunto de archivos copiados (normalizado)
        # Los archivos copiados son carpetas destino, necesitamos comparar con las fuentes
        copied_set = set(os.path.normpath(f) for f in copied_files if os.path.exists(f))
        
        # Obtener nombres base de las carpetas copiadas
        copied_basenames = set()
        for f in copied_files:
            if os.path.exists(f):
                copied_basenames.add(os.path.basename(os.path.normpath(f)))

        # Marcar solo los que no se copiaron
        self._checked_paths.clear()
        marked = 0

        for source in sources:
            if not os.path.exists(source):
                continue
            source_norm = os.path.normpath(source)
            source_basename = os.path.basename(source_norm)
            
            # Verificar si este origen ya fue copiado (por nombre base)
            if source_basename not in copied_basenames:
                self._checked_paths.add(source)
                marked += 1

        self._update_counts()
        self._refresh_current_folder()

        messagebox.showinfo(
            "Continuar desde log",
            f"{self.traducir('log_continuado').format(count=marked)}\n\n"
            f"Se han marcado {marked} elemento(s) que faltan copiar."
        )
        self.status_label.configure(
            text=f"Continuando desde log: {marked} elementos marcados",
            text_color="green"
        )

    def _mostrar_log_dialog(self):
        """Muestra información del log de transferencias"""
        log_data = self._load_transfer_log()
        if not log_data:
            messagebox.showinfo(self.traducir("info"), self.traducir("log_vacio"))
            return

        dlg = ctk.CTkToplevel(self)
        dlg.title(self.traducir("log_transferencias"))
        dlg.geometry("600x500")
        dlg.grab_set()

        frame = ctk.CTkFrame(dlg)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Información del log
        timestamp = log_data.get("timestamp", 0)
        from datetime import datetime
        fecha = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S") if timestamp else "N/A"
        
        info_text = (
            f"Fecha: {fecha}\n"
            f"Destino: {log_data.get('destination', 'N/A')}\n"
            f"Orígenes: {len(log_data.get('sources', []))} elemento(s)\n"
            f"Archivos copiados: {len(log_data.get('copied_files', []))} elemento(s)\n"
        )

        ctk.CTkLabel(frame, text=info_text, font=ctk.CTkFont(size=12), justify="left").pack(pady=(0, 10))

        # Lista de archivos copiados
        ctk.CTkLabel(frame, text="Archivos/Carpetas copiados:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        textbox = ctk.CTkTextbox(frame, width=560, height=250)
        textbox.pack(pady=(0, 10))
        
        copied_files = log_data.get("copied_files", [])
        if copied_files:
            textbox.insert("1.0", "\n".join(copied_files))
        else:
            textbox.insert("1.0", "No hay archivos registrados")
        textbox.configure(state="disabled")

        def on_close():
            dlg.destroy()

        ctk.CTkButton(frame, text="Cerrar", command=on_close).pack()

    def _eliminar_marcados(self):
        """
        Elimina permanentemente todos los elementos marcados.
        Muestra un diálogo de confirmación y una barra de progreso durante la eliminación.
        """
        if not self._checked_paths:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado"))
            return

        # Filtrar solo los que existen
        items = [p for p in self._checked_paths if os.path.exists(p)]
        if not items:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado"))
            return

        # Mostrar diálogo de confirmación
        respuesta = messagebox.askyesno(
            self.traducir("eliminar_marcados"),
            self.traducir("eliminar_marcados_confirmacion").format(count=len(items))
        )
        if not respuesta:
            return

        # Crear diálogo de progreso
        dlg = ctk.CTkToplevel(self)
        dlg.title(self.traducir("eliminando"))
        dlg.geometry("500x200")
        dlg.transient(self)
        dlg.grab_set()

        frame = ctk.CTkFrame(dlg)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        status_label = ctk.CTkLabel(
            frame,
            text=f"{self.traducir('eliminando')} {len(items)} elemento(s)...",
            font=ctk.CTkFont(size=12)
        )
        status_label.pack(pady=(0, 10))

        progress_bar = ctk.CTkProgressBar(frame, width=460, mode="determinate")
        progress_bar.pack(pady=(0, 10))
        progress_bar.set(0)

        detail_label = ctk.CTkLabel(
            frame,
            text="Iniciando...",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        detail_label.pack()

        state = {"done": False, "deleted": 0, "failed": 0, "errors": []}

        def delete_in_thread():
            import shutil
            total = len(items)
            for i, item_path in enumerate(items):
                try:
                    # Actualizar progreso (usar valores por defecto para evitar problemas de closure)
                    def update_progress(idx=i, total_items=total, path=item_path):
                        progress_bar.set((idx + 1) / total_items)
                        detail_label.configure(text=f"Eliminando: {os.path.basename(path)}...")
                    self.after(0, update_progress)

                    # Eliminar archivo o carpeta
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)

                    state["deleted"] += 1
                    # Remover de los marcados
                    if item_path in self._checked_paths:
                        self._checked_paths.remove(item_path)

                except Exception as e:
                    state["failed"] += 1
                    state["errors"].append(f"{os.path.basename(item_path)}: {str(e)}")

            state["done"] = True
            self.after(0, lambda: (
                dlg.destroy(),
                self._refresh_current_folder(),
                self._update_counts(),
                self._show_delete_result(state["deleted"], state["failed"], state["errors"])
            ))

        threading.Thread(target=delete_in_thread, daemon=True).start()

    def _show_delete_result(self, deleted_count, failed_count, errors):
        """Muestra el resultado de la eliminación"""
        if failed_count == 0:
            messagebox.showinfo(
                self.traducir("eliminacion_completada"),
                self.traducir("elementos_eliminados").format(count=deleted_count)
            )
            self.status_label.configure(
                text=f"{self.traducir('eliminacion_completada')} ({deleted_count} elementos)",
                text_color="green"
            )
        else:
            error_msg = self.traducir("elementos_eliminados").format(count=deleted_count)
            if failed_count > 0:
                error_msg += f"\n{self.traducir('elementos_fallidos').format(count=failed_count)}"
                if errors:
                    error_msg += "\n\nErrores:\n" + "\n".join(errors[:10])
                    if len(errors) > 10:
                        error_msg += f"\n... y {len(errors) - 10} más"
            
            messagebox.showwarning(
                self.traducir("eliminacion_error"),
                error_msg
            )
            self.status_label.configure(
                text=f"{self.traducir('eliminacion_completada')} ({deleted_count} eliminados, {failed_count} fallidos)",
                text_color="orange"
            )

    def _refresh_current_folder(self):
        """Refresca la vista del explorador actual"""
        if hasattr(self, "current_folder") and self.current_folder:
            self._list_folder(self.current_folder)

    # ---- Implementación interna (tu diálogo de progreso propio)
    def _copy_items_with_progress_internal(self, sources, dest_base, keep_names=True, include_top_dir=True):
        file_list = []
        for src in sources:
            if os.path.isdir(src):
                base = os.path.basename(src) if include_top_dir else ""
                for root, _dirs, filenames in os.walk(src):
                    for name in filenames:
                        fpath = os.path.join(root, name)
                        try: size = os.path.getsize(fpath)
                        except OSError: size = 0
                        rel_inside = os.path.relpath(fpath, src)
                        rel = os.path.join(base, rel_inside) if keep_names else os.path.relpath(fpath, os.path.dirname(src))
                        file_list.append((fpath, rel, size))
            else:
                try: size = os.path.getsize(src)
                except OSError: size = 0
                rel = os.path.basename(src) if keep_names else os.path.split(src)[1]
                file_list.append((src, rel, size))

        total_bytes = sum(sz for _, _, sz in file_list)
        os.makedirs(dest_base, exist_ok=True)

        dlg = ctk.CTkToplevel(self)
        dlg.title(self.traducir("copiando"))
        dlg.geometry("600x240")
        dlg.resizable(False, False)

        title_lbl = ctk.CTkLabel(dlg, text=f"{self.traducir('copiando')}...")
        title_lbl.pack(pady=(12, 6))

        file_lbl = ctk.CTkLabel(dlg, text=f"{self.traducir('archivo')}: —", wraplength=560, justify="left")
        file_lbl.pack(padx=16)

        pbar = ctk.CTkProgressBar(dlg)
        pbar.pack(fill="x", padx=16, pady=8)
        pbar.set(0)

        detail_lbl = ctk.CTkLabel(dlg, text="0%")
        detail_lbl.pack(pady=(0, 6))

        btns = ctk.CTkFrame(dlg, fg_color="transparent")
        btns.pack(pady=(4, 10))

        stop_event = threading.Event()

        def _minimize():
            try: dlg.iconify()
            except Exception: pass

        btn_min = ctk.CTkButton(btns, text=self.traducir("minimizar"), width=120, command=_minimize)
        btn_min.pack(side="left", padx=6)

        btn_cancel = ctk.CTkButton(btns, text=self.traducir("cancelar"), width=120, command=stop_event.set)
        btn_cancel.pack(side="left", padx=6)

        state = {"copied":0,"files_done":0,"speed":0.0,"eta":None,"error":None,"done":False,"canceled":False,"current_rel":"—"}
        start_time = time.time()

        copied_files_list = []  # Lista de archivos copiados para el log

        def worker():
            try:
                for srcfile, rel, size in file_list:
                    if stop_event.is_set():
                        state["canceled"]=True
                        break
                    state["current_rel"] = rel
                    destfile = os.path.join(dest_base, rel)
                    os.makedirs(os.path.dirname(destfile), exist_ok=True)
                    try: shutil.copy2(srcfile, destfile)
                    except Exception: shutil.copyfile(srcfile, destfile)
                    # Agregar a la lista de copiados
                    copied_files_list.append(destfile)
                    state["copied"] += size
                    state["files_done"] += 1
                    elapsed = max(time.time() - start_time, 0.001)
                    state["speed"] = state["copied"] / elapsed
                    if total_bytes > 0 and state["speed"] > 0:
                        rem = max(total_bytes - state["copied"], 0)
                        state["eta"] = rem / state["speed"]
                
                # Guardar log si hay archivos copiados
                if copied_files_list and not state["canceled"]:
                    # Obtener las carpetas únicas copiadas (no todos los archivos individuales)
                    copied_dirs = set()
                    for f in copied_files_list:
                        if os.path.isdir(f):
                            copied_dirs.add(f)
                        else:
                            # Agregar el directorio padre
                            copied_dirs.add(os.path.dirname(f))
                    
                    # Convertir a lista y normalizar
                    copied_dirs_list = [os.path.normpath(d) for d in copied_dirs]
                    
                    # Guardar log
                    if hasattr(self, "_last_copy_sources") and hasattr(self, "_last_copy_destination"):
                        self._save_transfer_log(
                            self._last_copy_sources,
                            self._last_copy_destination,
                            copied_dirs_list
                        )
                
                state["done"] = True
            except Exception as e:
                state["error"] = str(e); state["done"] = True

        threading.Thread(target=worker, daemon=True).start()

        def tick():
            file_lbl.configure(text=f"{self.traducir('archivo')}: {state['current_rel']}")
            frac = max(0.0, min(1.0, (state["copied"]/total_bytes) if total_bytes>0 else 0.0))
            pbar.set(frac)
            percent = int(frac*100)
            speed_mb = state["speed"]/(1024*1024)
            eta_txt = ""
            if state["eta"] is not None and state["speed"]>0:
                mins = int(state["eta"]//60); secs = int(state["eta"]%60)
                eta_txt = f"ETA {mins:02d}:{secs:02d}"
            detail_lbl.configure(text=f"{percent}%  |  {state['files_done']}/{len(file_list)}  |  {speed_mb:.1f} MB/s  {eta_txt}")

            if state["error"]:
                dlg.destroy()
                self.status_label.configure(text=self.traducir("error_copiar"), text_color="red")
                messagebox.showerror(self.traducir("error"), f"{self.traducir('error_copiar')}\n{state['error']}")
                return
            if state["done"]:
                dlg.destroy()
                if state["canceled"]:
                    self.status_label.configure(text=self.traducir("copia_cancelada"), text_color="orange")
                else:
                    self.status_label.configure(text=self.traducir("copia_completada"), text_color="green")
                    messagebox.showinfo(self.traducir("info"), f"{self.traducir('copia_completada')}")
                return
            dlg.after(100, tick)

        tick()

    # --- Explorer (diálogo nativo de Windows)
    def _copy_with_explorer(self, sources, dest_base, include_top_dir=True):
        """
        Copia con el diálogo nativo del Explorador (SHFileOperation).
        Importa localmente win32com.shell y muestra cualquier error real.
        """
        import threading, ctypes, os
        from ctypes import wintypes

        # Import aquí (mismo intérprete que corre la GUI)
        try:
            from win32com.shell import shell, shellcon
        except Exception as e:
            import sys as _sys
            messagebox.showerror(
                self.traducir("error"),
                "No se pudo importar 'win32com.shell'.\n"
                f"Detalle: {e}\n\nPython actual:\n{_sys.executable}\n\n"
                "Solución:\npython -m pip install pywin32\npython -m pywin32_postinstall install"
            )
            return

        os.makedirs(dest_base, exist_ok=True)

        # Normaliza rutas y arma el multistring \0..\0\0
        srcs = []
        for s in sources:
            s = os.path.abspath(s)
            if os.path.isdir(s) and not include_top_dir:
                srcs.append(os.path.join(s, "*"))   # solo contenido
            else:
                srcs.append(s)                       # carpeta/archivo tal cual

        from_str = "\0".join(srcs) + "\0\0"
        to_str   = os.path.abspath(dest_base) + "\0\0"  # ✅ doble null

        # HWND de la ventana (si falla, usa 0 y funciona igual)
        try:
            GetHWND = ctypes.windll.user32.FindWindowW
            GetHWND.restype = wintypes.HWND
            hwnd = GetHWND(None, self.title())
        except Exception:
            hwnd = 0

        def run():
            try:
                flags = shellcon.FOF_NOCONFIRMMKDIR  # muestra UI de progreso de Windows
                res, aborted = shell.SHFileOperation((hwnd, shellcon.FO_COPY, from_str, to_str, flags, None, None))
                if aborted:
                    self.after(0, lambda: self.status_label.configure(text=self.traducir("copia_cancelada"), text_color="orange"))
                elif res == 0:
                    self.after(0, lambda: self.status_label.configure(text=self.traducir("copia_completada"), text_color="green"))
                else:
                    self.after(0, lambda: messagebox.showerror(self.traducir("error"),
                        f"{self.traducir('error_copiar')}\nCódigo Shell: {res}"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(self.traducir("error"),
                    f"{self.traducir('error_copiar')}\n{e!r}"))

        threading.Thread(target=run, daemon=True).start()
        self.status_label.configure(text=self.traducir("copiando"), text_color="orange")


    # --- Wrapper: elige Explorer / Interno según preferencia y disponibilidad
    def _copy_items_with_progress(self, sources, dest_base, keep_names=True, include_top_dir=True):
        """
        Copia usando el motor del Explorador (SHFileOperation) vía ctypes.
        Muestra el diálogo nativo de Windows.
        """
        import os, sys

        if not sources:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado"))
            return
        if not sys.platform.startswith("win"):
            messagebox.showerror(self.traducir("error"), "Esta copia solo está disponible en Windows.")
            return

        # 1) Normaliza destino y asegura que exista
        dst = os.path.abspath(dest_base.rstrip("\\/"))
        os.makedirs(dst, exist_ok=True)

        # 2) Normaliza orígenes finales (expande “solo contenido” si aplica)
        srcs = []
        for s in sources:
            if not s:
                continue
            s_abs = os.path.abspath(s.rstrip("\\/"))
            if os.path.isdir(s_abs) and not include_top_dir:
                # copiar SOLO el contenido
                srcs.append(os.path.join(s_abs, "*"))
            else:
                # copiar carpeta/archivo tal cual
                srcs.append(s_abs)

        # 3) Validación: NO permitir copiar una carpeta dentro de sí misma (o a su descendiente)
        for s in srcs:
            # cuando copiamos con comodín "*", la carpeta real es su dirname
            s_cmp = os.path.dirname(s) if s.endswith("*") else s
            if dst == s_cmp or dst.startswith(s_cmp + os.sep):
                messagebox.showerror(
                    self.traducir("error"),
                    self.traducir("no_puedes_copiar_en_si_misma") if hasattr(self, "traducir")
                    else "No puedes copiar una carpeta dentro de sí misma."
                )
                return

        # 4) Filtra orígenes inexistentes (evita fallos del shell)
        srcs = [p for p in srcs if os.path.exists(p if not p.endswith("*") else os.path.dirname(p))]
        if not srcs:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado"))
            return

        # 5) Copia con el Explorador (ctypes).  _copy_with_explorer_ctypes ya usa \0\0 en pTo ✅
        return self._copy_with_explorer_ctypes(srcs, dst)


    def _copy_with_explorer_ctypes(self, src_list, dest_dir):
        """
        Implementación de SHFileOperationW (FO_COPY) con ctypes.
        Muestra UI de progreso del Explorador. Devuelve inmediatamente (hilo).
        """
        import os, threading, ctypes
        from ctypes import wintypes

        # Estructuras/constantes de shell32
        FO_COPY = 0x0002
        FOF_NOCONFIRMMKDIR = 0x0200  # crea carpetas sin preguntar (deja UI de progreso)
        # (si quieres evitar confirmaciones de overwrite, añade FOF_NOCONFIRMATION = 0x0010)

        class SHFILEOPSTRUCTW(ctypes.Structure):
            _fields_ = [
                ('hwnd', wintypes.HWND),
                ('wFunc', wintypes.UINT),
                ('pFrom', wintypes.LPCWSTR),
                ('pTo',   wintypes.LPCWSTR),
                ('fFlags', wintypes.USHORT),
                ('fAnyOperationsAborted', wintypes.BOOL),
                ('hNameMappings', wintypes.LPVOID),
                ('lpszProgressTitle', wintypes.LPCWSTR),
            ]

        shell32 = ctypes.windll.shell32

        # multistring (cada ruta terminada en '\0', y doble '\0' al final)
        from_str = "\0".join(os.path.abspath(p) for p in src_list) + "\0\0"
        to_str   = os.path.abspath(dest_dir) + "\0\0"   # ✅ doble null


        # intenta obtener HWND de la ventana principal; si falla, 0 (funciona igual)
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, self.title())
        except Exception:
            hwnd = 0

        def run():
            try:
                op = SHFILEOPSTRUCTW()
                op.hwnd = hwnd
                op.wFunc = FO_COPY
                op.pFrom = from_str
                op.pTo   = to_str
                op.fFlags = FOF_NOCONFIRMMKDIR
                op.fAnyOperationsAborted = False
                op.hNameMappings = None
                op.lpszProgressTitle = None

                res = shell32.SHFileOperationW(ctypes.byref(op))
                if op.fAnyOperationsAborted:
                    self.after(0, lambda: self.status_label.configure(
                        text=self.traducir("copia_cancelada"), text_color="orange"))
                elif res == 0:
                    self.after(0, lambda: self.status_label.configure(
                        text=self.traducir("copia_completada"), text_color="green"))
                else:
                    # Código de error del shell (no es excepción Python)
                    self.after(0, lambda: messagebox.showerror(
                        self.traducir("error"),
                        f"{self.traducir('error_copiar')}\nCódigo Shell: {res}"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(
                    self.traducir("error"),
                    f"{self.traducir('error_copiar')}\n{e!r}"))

        threading.Thread(target=run, daemon=True).start()
        self.status_label.configure(text=self.traducir("copiando"), text_color="orange")


    def _pegar_lista_dialog(self):
        """
        Abre una ventana emergente para que el usuario pegue una lista de juegos.
        """
        dlg = ctk.CTkToplevel(self)
        dlg.title("Pegar lista de juegos")
        dlg.geometry("600x400")
        dlg.grab_set()

        ctk.CTkLabel(dlg, text="Pega tu lista de juegos separada por comas:").pack(pady=10)
        
        textbox = ctk.CTkTextbox(dlg, width=580, height=280)
        textbox.pack(padx=10, pady=(0, 10))

        def on_paste_and_go():
            content = textbox.get("1.0", ctk.END).strip()
            if not content:
                dlg.destroy()
                return
            
            # Cerrar el diálogo de pegar primero
            dlg.destroy()
            # Llamar a process_game_list que tiene su propia pantalla de carga
            # Usar after(0) para asegurar que el diálogo se cierre antes de mostrar la nueva pantalla
            self.after(0, lambda: self._process_game_list(content))

        def on_cancel():
            dlg.destroy()

        btn_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_frame.pack(pady=(0, 10))
        ctk.CTkButton(btn_frame, text="Aceptar", command=on_paste_and_go).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancelar", command=on_cancel).pack(side="left", padx=5)

        dlg.wait_window()

    def _show_missing_games_dialog(self, missing_games: list[str]):
        """
        Muestra una ventana con la lista de juegos que no se encontraron, con conteo.
        """
        dlg = ctk.CTkToplevel(self)
        dlg.title(f"Juegos faltantes ({len(missing_games)})")
        dlg.geometry("500x400")
        dlg.grab_set()

        ctk.CTkLabel(dlg, text=f"Se encontraron {len(missing_games)} juegos faltantes:").pack(pady=10)
        
        textbox = ctk.CTkTextbox(dlg, width=480, height=280)
        textbox.pack(padx=10, pady=(0, 10))
        
        missing_list_str = "\n".join(missing_games)
        textbox.insert("1.0", missing_list_str)
        textbox.configure(state="disabled")
        
        def on_close():
            dlg.destroy()

        ctk.CTkButton(dlg, text="Cerrar", command=on_close).pack(pady=(0, 10))
        dlg.wait_window()

    def _render_files(self, entries):
        for iid in self.tree_files.get_children():
            self.tree_files.delete(iid)
        self._files_row_by_path.clear()

        # Acceso local para velocidad
        checked = self._checked_paths
        sep = os.sep
        
        # Filtrar solo marcados si el switch está activo
        if hasattr(self, "switch_solo_marcados_var") and self.switch_solo_marcados_var.get():
            entries = [e for e in entries if os.path.normpath(e[5]) in checked]

        for name, game_name, ftype, size, mtime, path in entries:
            # Normalizar el path para comparación
            path_norm = os.path.normpath(path)
            # ¿Está marcado este path exacto?
            exact = path_norm in checked
            # ¿Contiene marcados en su interior? (útil cuando estamos en un padre)
            contains = False
            if not exact and os.path.isdir(path):
                prefix = path_norm.rstrip("\\/") + sep
                # corta rápido en la primera coincidencia
                for p in checked:
                    p_norm = os.path.normpath(p)
                    if p_norm.startswith(prefix):
                        contains = True
                        break

            if exact:
                mark = "☑"          # marcado exacto
            elif contains:
                mark = "◩"          # contiene marcados dentro (estado intermedio)
            else:
                mark = "☐"

            if size is None and os.path.isdir(path):
                size_text = self.traducir("calculando")
            else:
                size_text = fmt_size(size if isinstance(size, (int, float)) else 0)

            iid = self.tree_files.insert(
                "", "end",
                values=(mark, name, game_name, ftype, size_text, fmt_mtime(mtime), path)
            )
            self._files_row_by_path[path] = iid

        self._update_counts()

    def _process_game_list(self, list_content: str):
        """
        Procesa una lista pegada de juegos (separados por comas o saltos de línea),
        marca todas las carpetas encontradas en el explorador y muestra los faltantes.
        Usa la carpeta actual del explorador como base de búsqueda.
        Ejecuta el procesamiento en un hilo separado para no bloquear la UI.
        """
        # Crear diálogo de progreso
        dlg = ctk.CTkToplevel(self)
        dlg.title(self.traducir("procesando_lista"))
        dlg.geometry("500x200")
        dlg.transient(self)
        dlg.grab_set()
        
        frame = ctk.CTkFrame(dlg)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Label de estado
        status_label = ctk.CTkLabel(
            frame,
            text=self.traducir("procesando_lista"),
            font=ctk.CTkFont(size=12)
        )
        status_label.pack(pady=(0, 10))
        
        # Barra de progreso (determinada)
        progress_bar = ctk.CTkProgressBar(frame, width=460, mode="determinate")
        progress_bar.pack(pady=(0, 10))
        progress_bar.set(0)
        
        # Label de detalle
        detail_label = ctk.CTkLabel(
            frame,
            text="Iniciando...",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        detail_label.pack()
        
        # Estado compartido
        state = {"done": False, "error": None, "current": 0, "total": 0, "found": 0, "missing": 0}
        
        def update_progress(current, total, found, missing):
            state["current"] = current
            state["total"] = total
            state["found"] = found
            state["missing"] = missing
            if total > 0:
                progress = current / total
                progress_bar.set(progress)
                detail_label.configure(
                    text=f"Procesando... {current}/{total} juegos | Encontrados: {found} | Faltantes: {missing}"
                )
        
        def process_in_thread():
            try:
                # 0) Asegura que la DB esté cargada y las raíces indexadas
                if not _items_by_key:
                    load_default_jsons()
                    self.after(0, self._update_db_summary)

                if not hasattr(self, "_paths_by_tid"):
                    self._paths_by_tid = {}
                if not hasattr(self, "_paths_by_name"):
                    self._paths_by_name = {}

                # Asegurar que todas las raíces estén indexadas completamente ANTES de buscar
                if hasattr(self, "_scan_roots") and self._scan_roots:
                    # Indexar la carpeta recursivamente si no está indexada (solo hay una carpeta ahora)
                    if not hasattr(self, "_indexed_roots"):
                        self._indexed_roots = set()
                    
                    if self._scan_roots:
                        root = self._scan_roots[0]
                        if os.path.isdir(root) and root not in self._indexed_roots:
                            # Actualizar mensaje del diálogo antes de indexar
                            self.after(0, lambda r=root: (
                                status_label.configure(text=f"Indexando {os.path.basename(r)}..."),
                                detail_label.configure(text="Escaneando carpetas...")
                            ))
                            self._scan_root(root, recursive=True)
                            self._indexed_roots.add(root)
                    
                    # Actualizar mensaje del diálogo después de indexar todas las raíces
                    self.after(0, lambda: (
                        status_label.configure(text=self.traducir("procesando_lista")),
                        detail_label.configure(text="Preparando búsqueda...")
                    ))
                    self.after(0, self._update_db_summary)

                # Obtener la carpeta actual del explorador
                current_folder = getattr(self, "current_folder", None)
                
                # Si hay una carpeta actual, también indexarla (nivel actual, rápido)
                if current_folder and os.path.isdir(current_folder):
                    # Verificar si la carpeta actual está en la raíz escaneada (solo hay una carpeta ahora)
                    is_scanned = False
                    if hasattr(self, "_scan_roots") and self._scan_roots:
                        root = self._scan_roots[0]
                        if current_folder.startswith(root) or current_folder == root:
                            is_scanned = True
                    
                    # Si no está escaneada, escanear solo esta carpeta (solo nivel actual, rápido)
                    if not is_scanned:
                        # Actualizar mensaje del diálogo antes de indexar
                        self.after(0, lambda: (
                            status_label.configure(text="Indexando carpeta actual..."),
                            detail_label.configure(text="Escaneando carpeta...")
                        ))
                        self._scan_root(current_folder, recursive=False)
                        # Actualizar mensaje del diálogo después de indexar
                        self.after(0, lambda: (
                            status_label.configure(text=self.traducir("procesando_lista")),
                            detail_label.configure(text="Preparando búsqueda...")
                        ))
                    self.after(0, self._update_db_summary)

                found_paths: set[str] = set()
                found_games: set[str] = set()  # Rastrear juegos únicos encontrados
                missing_games: list[str] = []

                # 2) Parseo de lista: comas y/o saltos de línea
                raw = list_content.replace("\r", "\n")
                raw = raw.replace("\n", ",")
                game_names = [n.strip() for n in raw.split(",") if n.strip()]
                total_games = len(game_names)

                # Actualizar estado inicial
                self.after(0, lambda: update_progress(0, total_games, 0, 0))

                # OPTIMIZACIÓN: Pre-construir índices invertidos UNA VEZ antes del loop
                # Índice invertido: palabra -> lista de (nombre_normalizado, tid)
                word_to_tids: dict[str, set[tuple[str, str]]] = {}
                if _index_name:
                    for nname, it in _index_name:
                        tid = it["title_id"]
                        words = nname.split()
                        for word in words:
                            if len(word) > 2:  # Solo palabras significativas
                                if word not in word_to_tids:
                                    word_to_tids[word] = set()
                                word_to_tids[word].add((nname, tid))
                
                # Cachear lista de directorios de la carpeta actual (solo una vez)
                current_folder_items = {}
                if current_folder and os.path.isdir(current_folder):
                    try:
                        for item in os.listdir(current_folder):
                            item_path = os.path.join(current_folder, item)
                            if os.path.isdir(item_path):
                                current_folder_items[norm_text(item)] = item_path
                    except Exception:
                        pass

                # 3) Resolver rutas para cada nombre (OPTIMIZADO)
                for i, name in enumerate(game_names):
                    # Actualizar progreso cada 5 juegos para reducir overhead (más rápido)
                    if i % 5 == 0 or i == len(game_names) - 1:
                        current_found = len(found_games)
                        current_missing = len(missing_games)
                        self.after(0, lambda n=i+1, t=total_games, f=current_found, m=current_missing: update_progress(n, t, f, m))
                    
                    norm_n = norm_text(name)
                    name_words = [w for w in norm_n.split() if len(w) > 2]  # Solo palabras significativas
                    paths_found_for_name: set[str] = set()

                    # 3a) Match por nombre en índice de nombres -> TIDs (OPTIMIZADO con índice invertido)
                    if _index_name and word_to_tids:
                        matching_tids = set()
                        # Si hay una sola palabra, buscar directamente
                        if len(name_words) == 1:
                            word = name_words[0]
                            if word in word_to_tids:
                                for nname, tid in word_to_tids[word]:
                                    if norm_n in nname or nname in norm_n:
                                        matching_tids.add(tid)
                        elif name_words:
                            # Múltiples palabras: buscar con umbral flexible (al menos 60% de palabras o mínimo 2)
                            required_words = max(2, int(len(name_words) * 0.6))  # Al menos 60% o mínimo 2 palabras
                            candidate_tids = {}
                            
                            for word in name_words:
                                if word in word_to_tids:
                                    for nname, tid in word_to_tids[word]:
                                        if tid not in candidate_tids:
                                            candidate_tids[tid] = []
                                        candidate_tids[tid].append(nname)
                            
                            # Verificar candidatos que tengan suficientes palabras
                            for tid, names in candidate_tids.items():
                                for nname in names:
                                    matching_words = sum(1 for word in name_words if word in nname)
                                    if matching_words >= required_words:
                                        matching_tids.add(tid)
                                        break
                            
                            # También buscar coincidencias parciales más flexibles SI NO SE ENCONTRÓ NADA
                            if not matching_tids:
                                for nname, it in _index_name:
                                    tid = it["title_id"]
                                    # Coincidencia parcial: el nombre normalizado está contenido o contiene
                                    if norm_n in nname or nname in norm_n:
                                        matching_tids.add(tid)
                                    # O si al menos 2 palabras coinciden (más flexible)
                                    elif len(name_words) >= 2:
                                        matching_count = sum(1 for word in name_words if word in nname)
                                        if matching_count >= 2:
                                            matching_tids.add(tid)
                                    # O si hay al menos 1 palabra significativa (para nombres cortos)
                                    elif len(name_words) == 1 and name_words[0] in nname:
                                        matching_tids.add(tid)
                        
                        for tid in matching_tids:
                            paths_found_for_name.update(self._find_paths_for_tid(tid))

                    # 3b) Match directo en índice por nombre de carpeta (OPTIMIZADO)
                    if self._paths_by_name:
                        # Búsqueda exacta primero (más rápida)
                        if norm_n in self._paths_by_name:
                            paths_found_for_name.update(self._paths_by_name[norm_n])
                        elif name_words:
                            # Búsqueda por palabras clave con umbral flexible (60% o mínimo 2)
                            required_words = max(2, int(len(name_words) * 0.6))  # Al menos 60% o mínimo 2 palabras
                            for key_name, paths in self._paths_by_name.items():
                                # Coincidencia exacta o parcial
                                if norm_n in key_name or key_name in norm_n:
                                    paths_found_for_name.update(paths)
                                # Verificar si suficientes palabras están en el nombre de la carpeta
                                elif len(name_words) > 0:
                                    matching_words = sum(1 for word in name_words if word in key_name)
                                    if matching_words >= required_words:
                                        paths_found_for_name.update(paths)
                                    # También buscar con 1 palabra si es el único caso
                                    elif len(name_words) == 1 and name_words[0] in key_name:
                                        paths_found_for_name.update(paths)
                    
                    # 3c) Búsqueda directa en la carpeta actual (OPTIMIZADO: usa cache)
                    if current_folder_items:
                        # Búsqueda exacta primero
                        if norm_n in current_folder_items:
                            paths_found_for_name.add(current_folder_items[norm_n])
                        elif name_words:
                            # Búsqueda por palabras clave con umbral flexible (60% o mínimo 2)
                            required_words = max(2, int(len(name_words) * 0.6))  # Al menos 60% o mínimo 2 palabras
                            for item_norm, item_path in current_folder_items.items():
                                    # Coincidencia exacta o parcial
                                if norm_n in item_norm or item_norm in norm_n:
                                        paths_found_for_name.add(item_path)
                                # Verificar si suficientes palabras coinciden
                                elif len(name_words) > 0:
                                    matching_words = sum(1 for word in name_words if word in item_norm)
                                    if matching_words >= required_words:
                                            paths_found_for_name.add(item_path)
                                    # También buscar con 1 palabra si es el único caso
                                    elif len(name_words) == 1 and name_words[0] in item_norm:
                                        paths_found_for_name.add(item_path)
                    
                    # 3d) Búsqueda en índices ya construidos (MUY RÁPIDO)
                    # Solo buscar recursivamente si NO encontramos nada en los índices anteriores
                    if not paths_found_for_name and hasattr(self, "_scan_roots") and self._scan_roots:
                        # Asegurar que todas las raíces estén indexadas primero (solo una vez)
                        # Solo hay una carpeta indexada ahora
                        if self._scan_roots:
                            root = self._scan_roots[0]
                            if os.path.isdir(root) and root not in getattr(self, "_indexed_roots", set()):
                                # Indexar esta raíz si no está indexada
                                self._scan_root(root, recursive=True)
                                if not hasattr(self, "_indexed_roots"):
                                    self._indexed_roots = set()
                                self._indexed_roots.add(root)
                        
                        # Si aún no encontramos nada, buscar en los índices de todas las raíces
                        # (ya están indexadas arriba, así que solo buscamos en _paths_by_name)
                        if not paths_found_for_name and self._paths_by_name:
                            # Búsqueda más exhaustiva en el índice de nombres (ya construido)
                            for key_name, paths in self._paths_by_name.items():
                                # Coincidencia exacta o parcial
                                if norm_n in key_name or key_name in norm_n:
                                    paths_found_for_name.update(paths)
                                    # No break - continuar buscando para encontrar todos los matches
                                elif name_words:
                                    # Verificar si suficientes palabras coinciden
                                    required_words = max(2, int(len(name_words) * 0.6))
                                    matching_words = sum(1 for word in name_words if word in key_name)
                                    if matching_words >= required_words:
                                        paths_found_for_name.update(paths)
                                        # No break - continuar buscando
                                    elif len(name_words) == 1 and name_words[0] in key_name:
                                        paths_found_for_name.update(paths)
                                        # No break - continuar buscando

                    if paths_found_for_name:
                        # Agregar TODOS los paths encontrados (puede haber múltiples versiones del mismo juego)
                        # Normalizar todos los paths
                        normalized_paths = {os.path.normpath(p) for p in paths_found_for_name}
                        found_paths.update(normalized_paths)
                        found_games.add(name)  # Rastrear que este juego fue encontrado
                    else:
                        missing_games.append(name)

                # 4) Actualizar UI en el hilo principal
                # Guardar la lista original para comparar después
                state["done"] = True
                self.after(0, lambda: (
                    dlg.destroy(),
                    self._apply_game_list_results(found_paths, missing_games, total_games, len(found_games), game_names)
                ))
                
            except Exception as e:
                state["done"] = True
                state["error"] = str(e)
                self.after(0, lambda: (
                    dlg.destroy(),
                    messagebox.showerror(self.traducir("error"), f"Error al procesar la lista:\n{e}"),
                    self.status_label.configure(text=self.traducir("error"), text_color="red")
                ))
        
        # Ejecutar en hilo separado
        threading.Thread(target=process_in_thread, daemon=True).start()
    
        # Función para verificar progreso (por si acaso el diálogo no se cierra)
        def check_done():
            if not state["done"]:
                dlg.after(100, check_done)
        
        check_done()
    
    def _get_tid_from_path(self, path):
        """Obtiene el Title ID de un path (si existe)"""
        base = os.path.basename(path)
        m = re.search(r'([0-9A-Fa-f]{8})', base)
        if m:
            return m.group(1).upper()
        return None
    
    def _desmarcar_duplicados(self):
        """Desmarca duplicados: si un juego está marcado múltiples veces, deja solo uno
        Detecta duplicados tanto por nombre como por Title ID"""
        if not self._checked_paths:
            return
        
        # Agrupar paths por Title ID primero (más preciso)
        games_by_tid: dict[str, list[str]] = {}
        # También agrupar por nombre normalizado para detectar duplicados por nombre
        games_by_name: dict[str, list[str]] = {}
        # Mapa de path -> TID para cruzar referencias
        path_to_tid: dict[str, str] = {}
        
        for path in list(self._checked_paths):
            if not os.path.exists(path):
                continue
            
            # Obtener Title ID del path
            tid = self._get_tid_from_path(path)
            if tid:
                path_to_tid[path] = tid
                if tid not in games_by_tid:
                    games_by_tid[tid] = []
                games_by_tid[tid].append(path)
            
            # Obtener nombre del juego
            game_name = self._get_game_name_for_path(path)
            if not game_name:
                folder_name = os.path.basename(path)
                game_name = self._clean_folder_name(folder_name)
            
            if game_name:
                # Normalizar nombre para agrupar
                norm_name = self._normalize_game_name_for_comparison(game_name)
                if norm_name not in games_by_name:
                    games_by_name[norm_name] = []
                games_by_name[norm_name].append(path)
        
        # Desmarcar duplicados por Title ID (más preciso)
        paths_to_unmark = set()
        for tid, paths in games_by_tid.items():
            if len(paths) > 1:
                # Dejar solo el primer path, desmarcar los demás
                paths_to_unmark.update(paths[1:])
                game_name = self._get_game_name_for_path(paths[0]) or paths[0]
                print(f"Desmarcando {len(paths) - 1} duplicados por TID '{tid}' ({game_name}) (dejando solo 1)")
        
        # Desmarcar duplicados por nombre (si no están ya desmarcados por TID)
        for norm_name, paths in games_by_name.items():
            if len(paths) > 1:
                # Filtrar paths que ya están marcados para desmarcar
                paths_remaining = [p for p in paths if p not in paths_to_unmark]
                if len(paths_remaining) > 1:
                    # Verificar si alguno tiene TID y si coinciden
                    tids_found = set()
                    for p in paths_remaining:
                        tid = path_to_tid.get(p)
                        if tid:
                            tids_found.add(tid)
                    
                    # Si todos tienen el mismo TID, ya se manejaron arriba
                    if len(tids_found) <= 1:
                        # Si tienen diferentes TIDs o no tienen TID, son duplicados por nombre
                        # Dejar solo el primero, desmarcar los demás
                        paths_to_unmark.update(paths_remaining[1:])
                        print(f"Desmarcando {len(paths_remaining) - 1} duplicados por nombre '{norm_name}' (dejando solo 1)")
        
        if paths_to_unmark:
            self._checked_paths -= paths_to_unmark
            print(f"Desmarcados {len(paths_to_unmark)} paths duplicados")
            # Actualizar la UI
            self._update_counts()
            current_folder = getattr(self, "current_folder", None)
            if current_folder and getattr(self, "_current_entries", None):
                self._render_files(self._current_entries)
    
    def _apply_game_list_results(self, found_paths: set[str], missing_games: list[str], total_games: int, found_games_count: int, original_game_names: list[str] = None):
        """Aplica los resultados del procesamiento de la lista en el hilo principal"""
        try:
            # Guardar la lista original de nombres de juegos para uso futuro
            if original_game_names:
                self.original_game_names = original_game_names.copy()
            else:
                # Si no se proporciona, inicializar como lista vacía
                if not hasattr(self, "original_game_names"):
                    self.original_game_names = []
            
            # 4) Actualiza los checks - normalizar todos los paths
            self._checked_paths.clear()
            # Normalizar todos los paths para asegurar coincidencias exactas
            normalized_paths = {os.path.normpath(p) for p in found_paths}
            self._checked_paths.update(normalized_paths)
            
            # 4.5) Si tenemos la lista original, desmarcar juegos que no están en ella AUTOMÁTICAMENTE
            if original_game_names:
                self._desmarcar_sobrantes(original_game_names)
            
            # 4.6) Desmarcar duplicados (si un juego está marcado múltiples veces, dejar solo uno)
            self._desmarcar_duplicados()
            
            # Filtrar solo los paths que realmente existen y están marcados después de desmarcar sobrantes
            existing_paths = {p for p in self._checked_paths if os.path.exists(p)}
            
            # 4.7) Calcular juegos únicos encontrados y asegurar que missing_games contenga TODOS los juegos de la lista original que NO se encontraron
            found_games_normalized = set()
            unique_games_set = set()  # Para contar juegos únicos
            for path in existing_paths:
                game_name = self._get_game_name_for_path(path)
                if not game_name:
                    folder_name = os.path.basename(path)
                    game_name = self._clean_folder_name(folder_name)
                if game_name:
                    norm_name = self._normalize_game_name_for_comparison(game_name)
                    found_games_normalized.add(norm_name)
                    found_games_normalized.add(norm_text(game_name))
                    # Agregar al set de juegos únicos (usando la normalización principal)
                    unique_games_set.add(norm_name)
            
            # Número de juegos únicos encontrados (después de normalizar)
            unique_games_found = len(unique_games_set)
            
            if original_game_names:
                # Reconstruir missing_games con TODOS los juegos de la lista original que no se encontraron
                missing_games_actual = []
                for orig_name in original_game_names:
                    orig_norm = self._normalize_game_name_for_comparison(orig_name)
                    orig_simple = norm_text(orig_name)
                    # Si no está en los encontrados, agregarlo a faltantes
                    if orig_norm not in found_games_normalized and orig_simple not in found_games_normalized:
                        missing_games_actual.append(orig_name)
                missing_games = missing_games_actual

            # 🔄 refresca lo que esté en pantalla para mostrar los checks marcados
            current_folder = getattr(self, "current_folder", None)
            if current_folder and getattr(self, "_current_entries", None):
                # Refrescar la vista actual para mostrar los checks
                self._render_files(self._current_entries)
            self._update_counts()

            # 5) Calcular tamaño total de los marcados (en hilo separado para no bloquear)
            def calculate_total_size():
                total_size = 0
                for path in existing_paths:
                    if os.path.isdir(path):
                        try:
                            for root, dirs, files in os.walk(path):
                                for f in files:
                                    try:
                                        total_size += os.path.getsize(os.path.join(root, f))
                                    except:
                                        pass
                        except:
                            pass
                # Actualizar mensaje con el tamaño calculado
                current_text = self.status_label.cget("text")
                self.after(0, lambda size=total_size, text=current_text: self.status_label.configure(
                    text=text.replace("Calculando tamaño...", f"Tamaño total: {fmt_size(size)}"),
                    text_color=self.status_label.cget("text_color")
                ))
            
            # Iniciar cálculo de tamaño en hilo separado
            threading.Thread(target=calculate_total_size, daemon=True).start()
            
            # 6) Mostrar solo los juegos faltantes (si hay) y mensaje de estado
            if missing_games:
                self._show_missing_games_dialog(missing_games)
                self.status_label.configure(
                    text=f"Procesados {total_games} juegos. Encontrados: {unique_games_found} juegos únicos ({len(existing_paths)} carpetas). Faltantes: {len(missing_games)}. Calculando tamaño...",
                    text_color="orange"
                )
            else:
                # Si no hay faltantes, mostrar mensaje de éxito
                self.status_label.configure(
                    text=f"✓ Procesados {total_games} juegos. Encontrados: {unique_games_found} juegos únicos ({len(existing_paths)} carpetas). Calculando tamaño...",
                    text_color="green"
                )

            # 6) Navegar a la carpeta que contiene los archivos encontrados
            # Priorizar la carpeta actual si hay archivos encontrados ahí
            if existing_paths:
                # Verificar si alguno de los paths encontrados está en la carpeta actual
                paths_in_current = False
                if current_folder:
                    current_norm = os.path.normpath(current_folder)
                    for path in existing_paths:
                        path_norm = os.path.normpath(path)
                        # Si el path está en la carpeta actual o es la carpeta actual
                        if path_norm == current_norm or path_norm.startswith(current_norm + os.sep):
                            paths_in_current = True
                            break
                
                # Si hay paths en la carpeta actual, solo refrescar la vista
                if paths_in_current and current_folder:
                    # Refrescar la lista para que se muestren los checks marcados
                    self._list_folder(current_folder)
                # Si no hay paths en la carpeta actual Y el usuario NO cambió manualmente, navegar
                elif not self._user_changed_folder:
                    try:
                        from collections import Counter
                        parents = [os.path.dirname(p.rstrip("\\/")) for p in existing_paths]
                        # idealmente abre donde los hijos directos ya son los marcados
                        best_parent, _ = Counter(parents).most_common(1)[0]
                        if best_parent and os.path.isdir(best_parent):
                            self._user_changed_folder = False  # Reset antes de cambiar programáticamente
                            self._enter_folder(best_parent)
                            self._user_changed_folder = False  # Mantener en False después
                    except Exception:
                        # fallback razonable
                        try:
                            common = os.path.commonpath(list(existing_paths))
                            if not os.path.isdir(common):
                                common = os.path.dirname(common)
                            if common:
                                self._user_changed_folder = False
                                self._enter_folder(common)
                                self._user_changed_folder = False
                        except Exception:
                            if getattr(self, "_scan_roots", []):
                                self._user_changed_folder = False
                                self._enter_folder(self._scan_roots[0])
                                self._user_changed_folder = False
                # Si el usuario cambió manualmente y no hay paths en la carpeta actual, solo refrescar
                elif current_folder:
                    self._list_folder(current_folder)
        except Exception as e:
            self.status_label.configure(text=f"Error al aplicar resultados: {e}", text_color="red")


    # Esta es la versión actualizada de _cargar_lista para que use la nueva función de procesamiento
    def _cargar_lista(self):
        file_path = filedialog.askopenfilename(
            title="Selecciona archivo de lista",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                list_content = f.read()
                self._process_game_list(list_content)
        except Exception as e:
            messagebox.showerror(self.traducir("error"), f"Error al leer el archivo:\n{e}")

    def _desmarcar_sobrantes(self, original_game_names: list[str]):
        """Desmarca juegos que no están en la lista original usando normalización robusta"""
        if not original_game_names or not self._checked_paths:
            return
        
        # Normalizar lista original usando la misma función de normalización que se usa para comparar
        original_normalized = set()
        for name in original_game_names:
            norm_name = self._normalize_game_name_for_comparison(name)
            if norm_name:
                original_normalized.add(norm_name)
            # También agregar la versión con norm_text simple para mayor flexibilidad
            simple_norm = norm_text(name)
            if simple_norm:
                original_normalized.add(simple_norm)
        
        # Obtener nombres de los juegos marcados y comparar
        paths_to_unmark = set()
        for path in list(self._checked_paths):
            if not os.path.exists(path):
                # Desmarcar paths que no existen
                paths_to_unmark.add(path)
                continue
            
            # Obtener nombre del juego desde el path
            game_name = self._get_game_name_for_path(path)
            if not game_name:
                # Si no hay nombre de BD, usar nombre de carpeta limpio
                folder_name = os.path.basename(path)
                game_name = self._clean_folder_name(folder_name)
            
            if game_name:
                # Normalizar usando la misma función robusta
                game_name_norm = self._normalize_game_name_for_comparison(game_name)
                game_name_simple = norm_text(game_name)
                
                # Verificar si el juego está en la lista original
                # Usar comparación MUY ESTRICTA: solo coincidencias muy claras
                found = False
                
                # Extraer números del nombre del juego marcado ANTES de comparar
                import re
                game_numbers = set(re.findall(r'\b\d+\b', game_name_norm))
                
                # Primero verificar coincidencia exacta normalizada
                if game_name_norm in original_normalized or game_name_simple in original_normalized:
                    found = True
                else:
                    # Buscar coincidencias en la lista original - SOLO coincidencias muy claras
                    for orig_name in original_game_names:
                        # Normalizar el nombre original de la misma manera
                        orig_norm = self._normalize_game_name_for_comparison(orig_name)
                        orig_simple = norm_text(orig_name)
                        
                        # Coincidencia exacta normalizada (la más estricta)
                        if (game_name_norm == orig_norm or game_name_simple == orig_norm or 
                            game_name_norm == orig_simple or game_name_simple == orig_simple):
                            found = True
                            break
                        
                        # Verificación CRÍTICA: Si hay números diferentes, NO considerar como coincidencia
                        orig_numbers = set(re.findall(r'\b\d+\b', orig_norm))
                        if game_numbers and orig_numbers:
                            # Ambos tienen números, deben coincidir EXACTAMENTE
                            if game_numbers != orig_numbers:
                                # Números diferentes, NO es una coincidencia válida
                                print(f"DEBUG: Números diferentes - Juego: {game_numbers}, Original: {orig_numbers} - '{game_name}' vs '{orig_name}'")
                                continue
                        elif game_numbers and not orig_numbers:
                            # El juego marcado tiene números pero la lista original no
                            # Esto podría ser una variación incorrecta (ej: "Black Ops 1" cuando la lista dice "Black Ops")
                            # Solo considerar como coincidencia si la similitud es EXACTAMENTE 100% (sin los números)
                            game_base = re.sub(r'\b\d+\b', '', game_name_norm).strip()
                            orig_base = re.sub(r'\b\d+\b', '', orig_norm).strip()
                            if game_base == orig_base:
                                # Las bases son idénticas, es una variación con número agregado
                                # NO considerarlo como coincidencia (es un sobrante)
                                print(f"DEBUG: Desmarcando variación numérica - '{game_name}' (tiene números {game_numbers} pero '{orig_name}' no tiene números)")
                                continue
                            # También verificar si las bases son muy similares (>= 90%)
                            from difflib import SequenceMatcher
                            base_similarity = SequenceMatcher(None, game_base, orig_base).ratio()
                            if base_similarity >= 0.90:
                                # Es muy similar pero tiene números diferentes, desmarcar
                                print(f"DEBUG: Desmarcando variación numérica (similitud {base_similarity:.2f}) - '{game_name}' (tiene números {game_numbers} pero '{orig_name}' no tiene números)")
                                continue
                        elif not game_numbers and orig_numbers:
                            # La lista original tiene números pero el juego marcado no
                            # Similar al caso anterior, verificar si las bases son idénticas
                            game_base = re.sub(r'\b\d+\b', '', game_name_norm).strip()
                            orig_base = re.sub(r'\b\d+\b', '', orig_norm).strip()
                            if game_base == orig_base:
                                # Las bases son idénticas, es una variación sin número
                                # NO considerarlo como coincidencia (es un sobrante)
                                print(f"DEBUG: Desmarcando variación numérica - '{game_name}' (no tiene números pero '{orig_name}' tiene números {orig_numbers})")
                                continue
                            # También verificar si las bases son muy similares (>= 90%)
                            from difflib import SequenceMatcher
                            base_similarity = SequenceMatcher(None, game_base, orig_base).ratio()
                            if base_similarity >= 0.90:
                                # Es muy similar pero tiene números diferentes, desmarcar
                                print(f"DEBUG: Desmarcando variación numérica (similitud {base_similarity:.2f}) - '{game_name}' (no tiene números pero '{orig_name}' tiene números {orig_numbers})")
                                continue
                        
                        # Coincidencia parcial MUY ESTRICTA: al menos 95% de similitud (aumentado de 90%)
                        from difflib import SequenceMatcher
                        similarity = SequenceMatcher(None, game_name_norm, orig_norm).ratio()
                        if similarity >= 0.95:  # Muy estricto: 95% de similitud
                            found = True
                            break
                        
                        # Verificar si el nombre contiene palabras clave significativas (MUY ESTRICTO)
                        game_words = set(game_name_norm.split())
                        orig_words = set(orig_norm.split())
                        # Filtrar palabras muy cortas (menos de 3 caracteres) y números
                        game_words = {w for w in game_words if len(w) >= 3 and not w.isdigit()}
                        orig_words = {w for w in orig_words if len(w) >= 3 and not w.isdigit()}
                        
                        if len(game_words) > 0 and len(orig_words) > 0:
                            common_words = game_words & orig_words
                            # MUY ESTRICTO: al menos 4 palabras comunes significativas Y el 85% de las palabras
                            if len(common_words) >= 4 and (len(common_words) / max(len(game_words), len(orig_words))) >= 0.85:
                                found = True
                                break
                        
                        # Verificar coincidencia por palabras clave principales (para nombres largos) - MUY ESTRICTO
                        # Extraer palabras principales (excluyendo artículos y palabras comunes)
                        articles = {'the', 'el', 'la', 'los', 'las', 'of', 'de', 'del', 'and', 'y'}
                        game_main_words = {w for w in game_words if w not in articles}
                        orig_main_words = {w for w in orig_words if w not in articles}
                        if len(game_main_words) > 0 and len(orig_main_words) > 0:
                            main_common = game_main_words & orig_main_words
                            # MUY ESTRICTO: Si TODAS las palabras principales coinciden (100%) Y hay al menos 3 palabras
                            if len(main_common) == len(game_main_words) and len(main_common) == len(orig_main_words) and len(main_common) >= 3:
                                found = True
                                break
                            # O si hay al menos 5 palabras principales y el 95% coincide
                            if len(main_common) >= 5 and len(main_common) / max(len(game_main_words), len(orig_main_words)) >= 0.95:
                                found = True
                                break
                
                if not found:
                    paths_to_unmark.add(path)
                    # Debug: mostrar qué juego se está desmarcando
                    print(f"Desmarcando: '{game_name}' (normalizado: '{game_name_norm}') - no encontrado en lista original")
        
        # Desmarcar los paths que no están en la lista original
        if paths_to_unmark:
            self._checked_paths -= paths_to_unmark
            print(f"Desmarcados {len(paths_to_unmark)} juegos que no están en la lista original (de {len(self._checked_paths) + len(paths_to_unmark)} total)")
            # Actualizar la UI para reflejar los cambios
            self._update_counts()
            # Refrescar la vista actual si hay entradas
            current_folder = getattr(self, "current_folder", None)
            if current_folder and getattr(self, "_current_entries", None):
                self._render_files(self._current_entries)

    def _copy_checked_items_from_browser(self):
        if not self._checked_paths:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado")); return
        dst_root = filedialog.askdirectory(title=self.traducir("elige_destino"))
        if not dst_root: return
        # Solo lo que exista en disco
        items = [p for p in self._checked_paths if os.path.exists(p)]
        if not items:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado")); return
        self._copy_items_with_progress(items, dest_base=dst_root, keep_names=True, include_top_dir=True)

    def _clean_folder_name(self, folder_name: str) -> str:
        """Limpia el nombre de una carpeta eliminando sufijos comunes"""
        import re
        name = folder_name.strip()
        
        # Eliminar sufijos comunes como (GOD)_360gamerRGH, (XEX)_360gamerRGH, etc.
        name = re.sub(r'\([^)]*\)_[^_]*$', '', name)  # (GOD)_360gamerRGH
        name = re.sub(r'\([^)]*\)_360gamerRGH$', '', name)  # (XEX)_360gamerRGH
        name = re.sub(r'\([^)]*\)_AnDreXplay$', '', name)  # (XEX)_AnDreXplay
        name = re.sub(r'\([^)]*\)_AnDreXPlay$', '', name)  # Variante con mayúscula
        name = re.sub(r'\[[^\]]+\]', '', name)  # [Title ID] o [Cars 3 Driven to Win]
        name = re.sub(r'_\d{8}$', '', name)  # _12345678 al final
        name = re.sub(r'^\d{8}\s*', '', name)  # 12345678 al inicio
        name = re.sub(r'\s*-\s*xbox\s+clasico\s*mx$', '', name, flags=re.IGNORECASE)  # - xbox clasico mx
        name = re.sub(r'\s*-\s*xbox\s+clasico$', '', name, flags=re.IGNORECASE)  # - xbox clasico
        
        # Limpiar espacios múltiples
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name

    def _normalize_game_name_for_comparison(self, name: str) -> str:
        """Normaliza un nombre de juego para comparación (elimina duplicados)"""
        import re
        # Normalizar texto básico
        normalized = norm_text(name)
        
        # Eliminar artículos y palabras comunes al inicio
        normalized = re.sub(r'^(the|el|la|los|las)\s+', '', normalized)
        
        # Eliminar palabras comunes que no afectan la identidad del juego
        palabras_comunes = [
            r'\s+the\s+video\s+game\s*$',
            r'\s+hd\s+collection\s*$',
            r'\s+collection\s*$',
            r'\s+edition\s*$',
            r'\s+definitive\s+edition\s*$',
            r'\s+remastered\s*$',
            r'\s+remaster\s*$',
            r'\s+game\s+of\s+the\s+year\s*$',
            r'\s+goty\s*$',
            r'\s+ultimate\s+edition\s*$',
        ]
        for pattern in palabras_comunes:
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
        
        # Normalizar abreviaciones comunes
        normalized = re.sub(r'^gtav$', 'grand theft auto v', normalized)
        normalized = re.sub(r'^gta\s+v$', 'grand theft auto v', normalized)
        normalized = re.sub(r'^gta\s+5$', 'grand theft auto v', normalized)
        normalized = re.sub(r'^gta\s+iv$', 'grand theft auto iv', normalized)
        normalized = re.sub(r'^gta\s+4$', 'grand theft auto iv', normalized)
        normalized = re.sub(r'^gta\s+3$', 'grand theft auto 3', normalized)
        normalized = re.sub(r'^gta\s+san\s+andreas$', 'grand theft auto san andreas', normalized)
        
        # Normalizar variantes comunes de números romanos y números
        normalized = re.sub(r'\s+ii\s+', ' 2 ', normalized)
        normalized = re.sub(r'\s+iii\s+', ' 3 ', normalized)
        normalized = re.sub(r'\s+iv\s+', ' 4 ', normalized)
        normalized = re.sub(r'\s+v\s+', ' 5 ', normalized)
        normalized = re.sub(r'\s+vi\s+', ' 6 ', normalized)
        normalized = re.sub(r'\s+vii\s+', ' 7 ', normalized)
        normalized = re.sub(r'\s+viii\s+', ' 8 ', normalized)
        normalized = re.sub(r'\s+ix\s+', ' 9 ', normalized)
        normalized = re.sub(r'\s+x\s+', ' 10 ', normalized)
        
        # Normalizar "1" vs "one", "2" vs "two", etc. al final
        normalized = re.sub(r'\s+one$', ' 1', normalized)
        normalized = re.sub(r'\s+two$', ' 2', normalized)
        normalized = re.sub(r'\s+three$', ' 3', normalized)
        
        # Eliminar guiones y reemplazar por espacios
        normalized = re.sub(r'[-\u2013\u2014]', ' ', normalized)
        
        # Eliminar "Pixar" al inicio
        normalized = re.sub(r'^pixar\s+', '', normalized)
        
        # Normalizar "DBZ" -> "dragon ball z"
        normalized = re.sub(r'\bdbz\b', 'dragon ball z', normalized)
        normalized = re.sub(r'\bdragon\s+ball\s+z\b', 'dragon ball z', normalized)
        
        # Normalizar "for Kinect"
        normalized = re.sub(r'\s+for\s+kinect\s*$', ' for kinect', normalized, flags=re.IGNORECASE)
        
        # Eliminar guiones bajos
        normalized = re.sub(r'_', ' ', normalized)
        
        # Limpiar espacios múltiples
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized

    def _generar_lista_marcados(self):
        """Genera una lista de nombres de juegos marcados separados por comas"""
        if not self._checked_paths:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado"))
            return
        
        # Diccionario para agrupar nombres similares: normalized_name -> (best_name, is_from_db)
        game_names_map = {}  # normalized -> (best_name, is_from_db)
        
        for path in self._checked_paths:
            if not os.path.exists(path):
                continue
            
            # Intentar obtener el nombre del juego desde la base de datos
            game_name = self._get_game_name_for_path(path)
            is_from_db = bool(game_name)
            
            if not game_name:
                # Si no se encuentra, limpiar el nombre de la carpeta
                folder_name = os.path.basename(path)
                game_name = self._clean_folder_name(folder_name)
            
            if not game_name:
                continue
            
            game_name = game_name.strip()
            normalized = self._normalize_game_name_for_comparison(game_name)
            
            if not normalized:
                continue
            
            # Si ya existe un nombre normalizado similar, elegir el mejor
            if normalized in game_names_map:
                existing_name, existing_is_from_db = game_names_map[normalized]
                # Priorizar nombres de la base de datos sobre nombres de carpetas
                if is_from_db and not existing_is_from_db:
                    game_names_map[normalized] = (game_name, True)
                elif not is_from_db and existing_is_from_db:
                    pass  # Mantener el existente
                else:
                    # Ambos son del mismo tipo, mantener el más corto (más limpio)
                    if len(game_name) < len(existing_name):
                        game_names_map[normalized] = (game_name, is_from_db)
            else:
                game_names_map[normalized] = (game_name, is_from_db)
        
        if not game_names_map:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado"))
            return
        
        # Obtener lista única de nombres (sin duplicados normalizados)
        game_names_sorted = sorted([name for name, _ in game_names_map.values()])
        lista_texto = ", ".join(game_names_sorted)
        
        # Crear diálogo para mostrar la lista
        dlg = ctk.CTkToplevel(self)
        dlg.title(self.traducir("lista_marcados_titulo"))
        dlg.geometry("600x500")
        dlg.transient(self)
        dlg.grab_set()
        
        # Frame principal
        frame = ctk.CTkFrame(dlg)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Contar paths únicos marcados (no solo nombres únicos)
        total_paths_marked = len([p for p in self._checked_paths if os.path.exists(p)])
        total_unique_games = len(game_names_sorted)
        
        # Título con información detallada
        title_text = f"{self.traducir('lista_marcados_desc').format(total=total_unique_games)}"
        if total_paths_marked != total_unique_games:
            title_text += f" ({total_paths_marked} carpetas marcadas)"
        title_label = ctk.CTkLabel(
            frame,
            text=title_text,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Texto con scroll
        text_widget = ctk.CTkTextbox(frame, width=560, height=350)
        text_widget.pack(fill="both", expand=True, pady=(0, 10))
        text_widget.insert("1.0", lista_texto)
        text_widget.configure(state="disabled")  # Solo lectura
        
        # Botones
        buttons_frame = ctk.CTkFrame(frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        def copiar_lista():
            try:
                self.clipboard_clear()
                self.clipboard_append(lista_texto)
                messagebox.showinfo(self.traducir("info"), self.traducir("lista_copiada"))
            except Exception as e:
                messagebox.showerror(self.traducir("error"), f"Error al copiar: {e}")
        
        def comparar_listas():
            """Abre un diálogo para comparar con la lista original"""
            self._mostrar_comparacion_listas(game_names_sorted, game_names_map)
        
        btn_copiar = ctk.CTkButton(
            buttons_frame,
            text=self.traducir("copiar_lista"),
            command=copiar_lista,
            width=120
        )
        btn_copiar.pack(side="left", padx=5)
        
        btn_comparar = ctk.CTkButton(
            buttons_frame,
            text=self.traducir("comparar_listas"),
            command=comparar_listas,
            width=140
        )
        btn_comparar.pack(side="left", padx=5)
        
        btn_cerrar = ctk.CTkButton(
            buttons_frame,
            text=self.traducir("cerrar"),
            command=dlg.destroy,
            width=120
        )
        btn_cerrar.pack(side="right", padx=5)

    def _mostrar_comparacion_listas(self, lista_marcados: list[str], game_names_map: dict):
        """Muestra un diálogo para comparar la lista marcada con una lista original"""
        # Crear diálogo para ingresar la lista original
        dlg_input = ctk.CTkToplevel(self)
        dlg_input.title(self.traducir("comparar_listas_titulo"))
        dlg_input.geometry("700x400")
        dlg_input.transient(self)
        dlg_input.grab_set()
        
        frame_input = ctk.CTkFrame(dlg_input)
        frame_input.pack(fill="both", expand=True, padx=20, pady=20)
        
        label_desc = ctk.CTkLabel(
            frame_input,
            text=self.traducir("comparar_listas_desc"),
            font=ctk.CTkFont(size=12)
        )
        label_desc.pack(pady=(0, 10))
        
        text_input = ctk.CTkTextbox(frame_input, width=660, height=250)
        text_input.pack(fill="both", expand=True, pady=(0, 10))
        
        buttons_frame = ctk.CTkFrame(frame_input)
        buttons_frame.pack(fill="x")
        
        def hacer_comparacion():
            lista_original_texto = text_input.get("1.0", "end-1c").strip()
            if not lista_original_texto:
                messagebox.showwarning(self.traducir("info"), "Por favor ingresa tu lista original")
                return
            
            dlg_input.destroy()
            self._comparar_listas(lista_original_texto, lista_marcados, game_names_map)
        
        btn_comparar = ctk.CTkButton(
            buttons_frame,
            text=self.traducir("comparar"),
            command=hacer_comparacion,
            width=120
        )
        btn_comparar.pack(side="left", padx=5)
        
        btn_cancelar = ctk.CTkButton(
            buttons_frame,
            text=self.traducir("cerrar"),
            command=dlg_input.destroy,
            width=120
        )
        btn_cancelar.pack(side="right", padx=5)

    def _comparar_listas(self, lista_original_texto: str, lista_marcados: list[str], game_names_map: dict):
        """Compara la lista original con la lista de juegos marcados"""
        # Parsear lista original
        lista_original_raw = lista_original_texto.replace("\r", "\n").replace("\n", ",")
        lista_original = [n.strip() for n in lista_original_raw.split(",") if n.strip()]
        
        # Normalizar ambas listas para comparación
        original_normalized = {}
        for name in lista_original:
            normalized = self._normalize_game_name_for_comparison(name)
            if normalized:
                original_normalized[normalized] = name
        
        marcados_normalized = {}
        for name in lista_marcados:
            normalized = self._normalize_game_name_for_comparison(name)
            if normalized:
                marcados_normalized[normalized] = name
        
        # Encontrar coincidencias, faltantes y sobrantes
        coincidencias = []
        faltantes = []
        sobrantes = []
        matched_marcados = set()  # Rastrear qué marcados ya fueron emparejados
        
        # Primero: coincidencias exactas
        for normalized in original_normalized:
            if normalized in marcados_normalized:
                coincidencias.append((original_normalized[normalized], marcados_normalized[normalized]))
                matched_marcados.add(normalized)
        
        # Segundo: buscar coincidencias similares para los faltantes
        def find_similar_name(target_normalized: str, candidates: dict[str, str], threshold: float = 0.6) -> tuple[str, str] | None:
            """Encuentra un nombre similar en los candidatos usando comparación de palabras"""
            from difflib import SequenceMatcher
            
            target_words = set(target_normalized.split())
            if not target_words:
                return None
            
            best_match = None
            best_score = 0
            
            for cand_normalized, cand_original in candidates.items():
                cand_words = set(cand_normalized.split())
                
                # Calcular similitud basada en palabras comunes
                common_words = target_words & cand_words
                if not common_words:
                    continue
                
                # Calcular score: palabras comunes / total de palabras únicas
                total_unique_words = len(target_words | cand_words)
                word_score = len(common_words) / total_unique_words if total_unique_words > 0 else 0
                
                # También calcular similitud de secuencia para el texto completo
                seq_score = SequenceMatcher(None, target_normalized, cand_normalized).ratio()
                
                # Score combinado (priorizar palabras comunes)
                combined_score = (word_score * 0.7) + (seq_score * 0.3)
                
                if combined_score > best_score and combined_score >= threshold:
                    best_score = combined_score
                    best_match = (cand_normalized, cand_original)
            
            return best_match
        
        faltantes_temp = []
        for normalized, name in original_normalized.items():
            if normalized not in marcados_normalized:
                # Buscar un nombre similar en marcados que no haya sido emparejado
                available_marcados = {k: v for k, v in marcados_normalized.items() if k not in matched_marcados}
                similar = find_similar_name(normalized, available_marcados, threshold=0.5)
                if similar:
                    similar_normalized, similar_original = similar
                    coincidencias.append((name, similar_original))
                    matched_marcados.add(similar_normalized)
                else:
                    faltantes_temp.append(name)
        
        faltantes = faltantes_temp
        
        # Sobrantes: están en marcados pero no fueron emparejados
        for normalized, name in marcados_normalized.items():
            if normalized not in matched_marcados:
                sobrantes.append(name)
        
        # Ordenar
        coincidencias.sort(key=lambda x: x[0].lower())
        faltantes.sort(key=str.lower)
        sobrantes.sort(key=str.lower)
        
        # Mostrar resultados en un diálogo con pestañas
        self._mostrar_resultados_comparacion(coincidencias, faltantes, sobrantes)

    def _mostrar_resultados_comparacion(self, coincidencias: list, faltantes: list, sobrantes: list):
        """Muestra los resultados de la comparación en un diálogo con pestañas"""
        dlg = ctk.CTkToplevel(self)
        dlg.title(self.traducir("comparar_listas_titulo"))
        dlg.geometry("800x600")
        dlg.transient(self)
        dlg.grab_set()
        
        frame = ctk.CTkFrame(dlg)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Pestañas
        tabview = ctk.CTkTabview(frame)
        tabview.pack(fill="both", expand=True)
        
        # Pestaña de coincidencias
        tab_coincidencias = tabview.add(self.traducir("coincidencias"))
        label_coincidencias = ctk.CTkLabel(
            tab_coincidencias,
            text=self.traducir("coincidencias_desc").format(total=len(coincidencias)),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        label_coincidencias.pack(pady=(0, 10))
        
        text_coincidencias = ctk.CTkTextbox(tab_coincidencias, width=760, height=450)
        text_coincidencias.pack(fill="both", expand=True)
        if coincidencias:
            texto = "\n".join([f"{orig} → {marc}" if orig != marc else orig for orig, marc in coincidencias])
            text_coincidencias.insert("1.0", texto)
        else:
            text_coincidencias.insert("1.0", self.traducir("sin_coincidencias"))
        text_coincidencias.configure(state="disabled")
        
        # Pestaña de faltantes
        tab_faltantes = tabview.add(self.traducir("faltantes"))
        label_faltantes = ctk.CTkLabel(
            tab_faltantes,
            text=self.traducir("faltantes_desc").format(total=len(faltantes)),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        label_faltantes.pack(pady=(0, 10))
        
        text_faltantes = ctk.CTkTextbox(tab_faltantes, width=760, height=450)
        text_faltantes.pack(fill="both", expand=True)
        if faltantes:
            texto = "\n".join(faltantes)
            text_faltantes.insert("1.0", texto)
        else:
            text_faltantes.insert("1.0", self.traducir("sin_faltantes"))
        text_faltantes.configure(state="disabled")
        
        # Pestaña de sobrantes
        tab_sobrantes = tabview.add(self.traducir("sobrantes"))
        label_sobrantes = ctk.CTkLabel(
            tab_sobrantes,
            text=self.traducir("sobrantes_desc").format(total=len(sobrantes)),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        label_sobrantes.pack(pady=(0, 10))
        
        text_sobrantes = ctk.CTkTextbox(tab_sobrantes, width=760, height=450)
        text_sobrantes.pack(fill="both", expand=True)
        if sobrantes:
            texto = "\n".join(sobrantes)
            text_sobrantes.insert("1.0", texto)
        else:
            text_sobrantes.insert("1.0", self.traducir("sin_sobrantes"))
        text_sobrantes.configure(state="disabled")
        
        # Botón cerrar
        btn_cerrar = ctk.CTkButton(
            frame,
            text=self.traducir("cerrar"),
            command=dlg.destroy,
            width=120
        )
        btn_cerrar.pack(pady=(10, 0))

# -------------------- main --------------------
if __name__ == "__main__":
    app = XboxGameLookupApp()
    app.mainloop()
