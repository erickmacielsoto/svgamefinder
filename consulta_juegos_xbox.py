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
        "abrir_carpeta": "Abrir carpeta",
        "ver_archivos": "Ver archivos…",
        "copiar_a": "Copiar a…",
        "carpeta_indexada": "Carpeta indexada.",
        "copiando": "Copiando...",
        "copia_completada": "Copia completada.",
        "error_copiar": "Error al copiar",
        "no_carpeta_tid": "No se encontró carpeta para ese Title ID.\nAgrega una 'carpeta origen' y reintenta.",
        "elige_carpeta_juego": "Selecciona la carpeta del juego",
        "elige_destino": "Selecciona la carpeta de destino",
        "ok": "OK",
        "cancelar": "Cancelar",
        "copia_cancelada": "Copia cancelada.",
        # Explorador
        "explorador": "Explorador de archivos",
        "ruta": "Ruta:",
        "abrir_explorer": "Abrir en Explorer",
        "subir": "Subir nivel",
        "cambiar_carpeta": "Cambiar…",
        "copiar_seleccion": "Copiar selección",
        "copiar_marcados": "Copiar marcados",
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
        # Archivo actual
        "archivo": "Archivo",
        # Método de copia
        "metodo_copia": "Método de copia",
        "auto_explorer": "Auto (Explorer si hay)",
        "explorer_forzar": "Explorer (forzar)",
        "interno": "Interno (propio)",
    },
    "en": {
        "modo_oscuro": "Dark Mode",
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
        "abrir_carpeta": "Open folder",
        "ver_archivos": "Browse files…",
        "copiar_a": "Copy to…",
        "carpeta_indexada": "Folder indexed.",
        "copiando": "Copying...",
        "copia_completada": "Copy completed.",
        "error_copiar": "Copy error",
        "no_carpeta_tid": "No folder found for that Title ID.\nAdd a 'source folder' and try again.",
        "elige_carpeta_juego": "Choose the game folder",
        "elige_destino": "Choose destination folder",
        "ok": "OK",
        "cancelar": "Cancel",
        "copia_cancelada": "Copy canceled.",
        "explorador": "File explorer",
        "ruta": "Path:",
        "abrir_explorer": "Open in Explorer",
        "subir": "Up",
        "cambiar_carpeta": "Change…",
        "copiar_seleccion": "Copy selection",
        "copiar_marcados": "Copy checked",
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
        "archivo": "File",
        "metodo_copia": "Copy method",
        "auto_explorer": "Auto (Explorer if available)",
        "explorer_forzar": "Explorer (force)",
        "interno": "Internal (built-in)",
    },
    "pt": {
        "modo_oscuro": "Modo Escuro",
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
        "abrir_carpeta": "Abrir pasta",
        "ver_archivos": "Ver arquivos…",
        "copiar_a": "Copiar para…",
        "carpeta_indexada": "Pasta indexada.",
        "copiando": "Copiando...",
        "copia_completada": "Cópia concluída.",
        "error_copiar": "Erro ao copiar",
        "no_carpeta_tid": "Nenhuma pasta encontrada para esse Title ID.\nAdicione uma 'pasta de origem' e tente novamente.",
        "elige_carpeta_juego": "Escolha a pasta do jogo",
        "elige_destino": "Escolha a pasta de destino",
        "ok": "OK",
        "cancelar": "Cancelar",
        "copia_cancelada": "Cópia cancelada.",
        "explorador": "Explorador de arquivos",
        "ruta": "Caminho:",
        "abrir_explorer": "Abrir no Explorer",
        "subir": "Subir",
        "cambiar_carpeta": "Alterar…",
        "copiar_seleccion": "Copiar seleção",
        "copiar_marcados": "Copiar marcados",
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
        "archivo": "Arquivo",
        "metodo_copia": "Método de cópia",
        "auto_explorer": "Auto (Explorer se houver)",
        "explorer_forzar": "Explorer (forçar)",
        "interno": "Interno",
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

        self.title("SVXboxGamesFinder (Local) - By: @erickmacielsoto - Reviewed by: @jasontorresb")
        self.geometry("1200x880")

        # Preferencias
        self.idioma_actual = self._detectar_idioma_sistema()
        self.modo_oscuro_inicial = self._detectar_modo_oscuro_sistema()
        self.copy_method = "explorer"  # "auto" | "explorer" | "internal"
        self._cargar_config()
        self._aplicar_estilo_treeview("dark" if self.modo_oscuro_inicial else "light")
        ctk.set_appearance_mode("dark" if self.modo_oscuro_inicial else "light")

        # UI
        self._setup_ui()
        self._update_ui_texts()
        
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
                if hasattr(self, "_scan_roots"):
                    def scan_roots_background():
                        try:
                            for r in list(self._scan_roots):
                                if os.path.isdir(r): 
                                    self._scan_root(r)
                                else:
                                    try: self._scan_roots.remove(r)
                                    except ValueError: pass
                        except Exception as e:
                            print(f"Error escaneando raíces: {e}")
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
        self._checked_paths = set()
        self._user_changed_folder = False  # Rastrea si el usuario cambió manualmente la carpeta

        self._update_nav_buttons()

    # ---------- traducción y preferencias ----------
    def traducir(self, clave): return traducciones[self.idioma_actual].get(clave, f"MISSING_TRANSLATION_{clave}")

    def _guardar_config(self):
        config = {
            "idioma": self.idioma_actual,
            "modo_oscuro": self.switch_var.get(),
            "scan_roots": getattr(self, "_scan_roots", []),
            "copy_method": self.copy_method,
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
                self._scan_roots = config.get("scan_roots", [])
                if config.get("copy_method") in ("auto","explorer","internal"):
                    self.copy_method = config["copy_method"]
            except Exception as e:
                messagebox.showwarning(self.traducir("info"), f"Error al cargar configuración, usando valores predeterminados: {e}")

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
        self.idioma_menu_label = ctk.CTkLabel(left, text=f"🌐 {self.traducir('idioma')}:")
        self.idioma_menu_label.pack(side="left", padx=(10, 5))
        self.selector_idioma = ctk.CTkOptionMenu(left, values=["Español", "English", "Português"],
                                                 command=self._cambiar_idioma)
        self.selector_idioma.pack(side="left")
        self.selector_idioma.set({"es":"Español","en":"English","pt":"Português"}.get(self.idioma_actual,"Español"))

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
        
        # Fila 1: Navegación básica (4 botones)
        self.btn_back = ctk.CTkButton(buttons_container, text=f"⬅️ {self.traducir('atras')}", width=90, command=self._nav_back)
        self.btn_back.grid(row=0, column=0, padx=(6,4), pady=2)
        self.btn_forward = ctk.CTkButton(buttons_container, text=f"➡️ {self.traducir('adelante')}", width=90, command=self._nav_forward)
        self.btn_forward.grid(row=0, column=1, padx=(6,4), pady=2)
        self.btn_up = ctk.CTkButton(buttons_container, text=f"⬆️ {self.traducir('subir')}", width=100, command=self._go_up)
        self.btn_up.grid(row=0, column=2, padx=(6,4), pady=2)
        self.btn_open_explorer = ctk.CTkButton(buttons_container, text=f"📂 {self.traducir('abrir_explorer')}", width=120, command=self._open_current_in_explorer)
        self.btn_open_explorer.grid(row=0, column=3, padx=(6,4), pady=2)
        
        # Fila 2: Navegación y acciones (4 botones)
        self.btn_change_folder = ctk.CTkButton(buttons_container, text=f"🔄 {self.traducir('cambiar_carpeta')}", width=120, command=self._change_browser_folder)
        self.btn_change_folder.grid(row=1, column=0, padx=(6,4), pady=2)
        self.btn_select_all = ctk.CTkButton(buttons_container, text=f"✅ {self.traducir('seleccionar_todo')}", width=120, command=self._select_all_files)
        self.btn_select_all.grid(row=1, column=1, padx=(6,4), pady=2)
        self.btn_mark_all = ctk.CTkButton(buttons_container, text=f"☑️ {self.traducir('marcar_visibles')}", width=120, command=self._mark_visible_rows)
        self.btn_mark_all.grid(row=1, column=2, padx=(6,4), pady=2)
        self.btn_unmark_all = ctk.CTkButton(buttons_container, text=f"☐ {self.traducir('desmarcar_visibles')}", width=120, command=self._unmark_visible_rows)
        self.btn_unmark_all.grid(row=1, column=3, padx=(6,4), pady=2)
        
        # Fila 3: Acciones de copia (3 botones)
        self.btn_copy_rows = ctk.CTkButton(buttons_container, text=f"📋 {self.traducir('copiar_seleccion')}", width=120, command=self._copy_selected_rows_browser)
        self.btn_copy_rows.grid(row=2, column=0, padx=(6,4), pady=2)
        self.btn_copy_marked = ctk.CTkButton(buttons_container, text=f"📦 {self.traducir('copiar_marcados')}", width=120, command=self._copy_checked_items_from_browser)
        self.btn_copy_marked.grid(row=2, column=1, padx=(6,4), pady=2)
        self.btn_limpiar_seleccion = ctk.CTkButton(buttons_container, text=f"🗑️ {self.traducir('limpiar_seleccion')}", width=120, command=self._limpiar_lista_cargada)
        self.btn_limpiar_seleccion.grid(row=2, column=2, padx=(6,4), pady=2)
        
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

        # Filtro
        filter_bar = ctk.CTkFrame(self.frame_explorer, fg_color="transparent"); filter_bar.pack(fill="x", padx=6, pady=(0,6))
        self.files_filter_var = ctk.StringVar(value="")
        self.files_filter_entry = ctk.CTkEntry(filter_bar, textvariable=self.files_filter_var,
                                               placeholder_text=self.traducir("filtro_placeholder"), width=520)
        self.files_filter_entry.pack(side="left", padx=(0,6))
        self.files_filter_entry.bind("<Return>", lambda e: self._apply_files_filter())
        self.files_filter_entry.bind("<KeyRelease>", lambda e: self._apply_files_filter(debounce=True))
        self.btn_filter = ctk.CTkButton(filter_bar, text=f"🔍 {self.traducir('aplicar_filtro')}", width=90, command=self._apply_files_filter)
        self.btn_filter.pack(side="left", padx=(0,6))
        self.btn_filter_clear = ctk.CTkButton(filter_bar, text=f"🧹 {self.traducir('limpiar_filtro')}", width=90, command=self._clear_files_filter)
        self.btn_filter_clear.pack(side="left")

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
        if not hasattr(self, "_scan_roots"): self._scan_roots = []
        if path not in self._scan_roots:
            self._scan_roots.append(path); self._guardar_config()
        self._scan_root(path); self._update_db_summary()
        self.status_label.configure(text=self.traducir("carpeta_indexada"), text_color="green")

    def _scan_root(self, root, recursive=True):
        """
        Escanea una carpeta raíz e indexa los juegos encontrados.
        Si recursive=False, solo escanea el nivel actual (no recursivo).
        """
        if not hasattr(self, "_paths_by_tid"):
            self._paths_by_tid = {}
        if not hasattr(self, "_paths_by_name"):
            self._paths_by_name = {}

        if recursive:
            # Escaneo recursivo completo (para carpetas raíz agregadas manualmente)
            # Primera pasada: indexar por Title ID
            for dirpath, _, dirnames in os.walk(root):
                base = os.path.basename(dirpath)
                m = re.search(r'([0-9A-Fa-f]{8})', base)
                if m:
                    tid = m.group(1).upper()
                    self._paths_by_tid.setdefault(tid, set()).add(dirpath)
                
                for d in dirnames:
                    if re.fullmatch(r'[0-9A-Fa-f]{8}', d):
                        tid = d.upper()
                        self._paths_by_tid.setdefault(tid, set()).add(os.path.join(dirpath, d))

            # Segunda pasada: indexar por nombre de juego para una mejor búsqueda
            for it in _items_by_key.values():
                tid = it["title_id"]
                norm_name = norm_text(it["name"])
                
                # Buscar en las carpetas indexadas por TID para añadir también el nombre
                if tid in self._paths_by_tid:
                    for path in self._paths_by_tid[tid]:
                        self._paths_by_name.setdefault(norm_name, set()).add(path)
                
                # Buscar en el árbol de directorios para una coincidencia con el nombre
                for dirpath, _, _ in os.walk(root):
                    norm_dir_name = norm_text(os.path.basename(dirpath))
                    if norm_name == norm_dir_name or norm_name in norm_dir_name:
                        self._paths_by_name.setdefault(norm_name, set()).add(dirpath)
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

            entries.sort(key=lambda x: (x[2] != "Carpeta", x[0].lower()))
            self._current_entries = entries
            self._render_files(entries)
            self._clear_files_filter()
            self._start_dirsize_worker(entries, folder, self._size_thread_stop)
            self._update_counts()

        except Exception as e:
            messagebox.showerror(self.traducir("error"), str(e))


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
        self.counts_label.configure(
            text=f"  |  {self.traducir('seleccionados')}: {sel_count}  |  {self.traducir('marcados')}: {marked_visible}"
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
        if folder:
            self._enter_folder(folder, user_initiated=True)

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
                    row_id = self._files_row_by_path.get(path)
                    if row_id: self.tree_files.set(row_id, "size", fmt_size(total))
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

        self._copy_items_with_progress(confirmed_items, dest_base=dst_root, keep_names=True, include_top_dir=True)

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
                    state["copied"] += size
                    state["files_done"] += 1
                    elapsed = max(time.time() - start_time, 0.001)
                    state["speed"] = state["copied"] / elapsed
                    if total_bytes > 0 and state["speed"] > 0:
                        rem = max(total_bytes - state["copied"], 0)
                        state["eta"] = rem / state["speed"]
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
            dlg.destroy()
            if content:
                self._process_game_list(content)

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
        # 1) UI: estado "procesando"
        self.status_label.configure(text="Procesando lista...", text_color="orange")
        self.update_idletasks()
        
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

                # Obtener la carpeta actual del explorador
                current_folder = getattr(self, "current_folder", None)
                
                # Si hay una carpeta actual, indexarla si no está ya indexada
                if current_folder and os.path.isdir(current_folder):
                    # Verificar si la carpeta actual está en las raíces escaneadas
                    is_scanned = False
                    if hasattr(self, "_scan_roots"):
                        for root in self._scan_roots:
                            if current_folder.startswith(root) or current_folder == root:
                                is_scanned = True
                                break
                    
                    # Si no está escaneada, escanear solo esta carpeta (solo nivel actual, rápido)
                    if not is_scanned:
                        # Escanear solo el nivel actual, no recursivamente (mucho más rápido)
                        self.after(0, lambda: self.status_label.configure(
                            text="Indexando carpeta actual...", text_color="orange"
                        ))
                        self._scan_root(current_folder, recursive=False)
                        self.after(0, self._update_db_summary)
                elif not self._paths_by_tid and not self._paths_by_name:
                    # Si no hay carpeta actual y no hay índices, escanear las raíces guardadas
                    for r in getattr(self, "_scan_roots", []) or []:
                        if os.path.isdir(r):
                            self._scan_root(r)
                    self.after(0, self._update_db_summary)

                found_paths: set[str] = set()
                found_games: set[str] = set()  # Rastrear juegos únicos encontrados
                missing_games: list[str] = []

                # 2) Parseo de lista: comas y/o saltos de línea
                raw = list_content.replace("\r", "\n")
                raw = raw.replace("\n", ",")
                game_names = [n.strip() for n in raw.split(",") if n.strip()]
                total_games = len(game_names)

                # 3) Resolver rutas para cada nombre
                for i, name in enumerate(game_names):
                    # Actualizar progreso cada 10 juegos
                    if i % 10 == 0:
                        self.after(0, lambda n=i, t=total_games: self.status_label.configure(
                            text=f"Procesando lista... {n}/{t}", text_color="orange"
                        ))
                    
                    norm_n = norm_text(name)
                    name_words = norm_n.split()  # Definir una vez al inicio
                    paths_found_for_name: set[str] = set()

                    # 3a) Match por nombre en índice de nombres -> TIDs
                    if _index_name:
                        # Búsqueda más flexible: buscar si el nombre normalizado está contenido en el nombre del juego
                        # o si alguna palabra clave del nombre está en el nombre del juego
                        matching_tids = set()
                        for nname, it in _index_name:
                            # Coincidencia exacta o parcial
                            if norm_n in nname or nname in norm_n:
                                matching_tids.add(it["title_id"])
                            # Si el nombre tiene múltiples palabras, buscar si todas están presentes
                            elif len(name_words) > 1:
                                if all(word in nname for word in name_words if len(word) > 2):
                                    matching_tids.add(it["title_id"])
                        
                        for tid in matching_tids:
                            paths_found_for_name.update(self._find_paths_for_tid(tid))

                    # 3b) Match directo en índice por nombre de carpeta (construido al escanear raíces)
                    if self._paths_by_name:
                        # exacto
                        if norm_n in self._paths_by_name:
                            paths_found_for_name.update(self._paths_by_name[norm_n])
                        else:
                            # contiene (suave) — útil para listas con pequeñas variaciones
                            for key_name, paths in self._paths_by_name.items():
                                # Coincidencia exacta o parcial
                                if norm_n in key_name or key_name in norm_n:
                                    paths_found_for_name.update(paths)
                                # Si el nombre tiene múltiples palabras, buscar si todas están presentes
                                elif len(name_words) > 1:
                                    if all(word in key_name for word in name_words if len(word) > 2):
                                        paths_found_for_name.update(paths)
                    
                    # 3c) Búsqueda directa en la carpeta actual del explorador
                    if current_folder and os.path.isdir(current_folder):
                        # Buscar subdirectorios que coincidan con el nombre del juego
                        try:
                            for item in os.listdir(current_folder):
                                item_path = os.path.join(current_folder, item)
                                if os.path.isdir(item_path):
                                    item_norm = norm_text(item)
                                    # Coincidencia exacta o parcial
                                    if norm_n == item_norm or norm_n in item_norm or item_norm in norm_n:
                                        paths_found_for_name.add(item_path)
                                    # Búsqueda por palabras clave
                                    elif len(name_words) > 1:
                                        item_words = item_norm.split()
                                        if all(word in item_norm for word in name_words if len(word) > 2):
                                            paths_found_for_name.add(item_path)
                        except Exception:
                            pass

                    if paths_found_for_name:
                        # Solo tomar el primer path encontrado para cada juego (evitar duplicados)
                        first_path = sorted(list(paths_found_for_name))[0]
                        # Normalizar el path para asegurar coincidencias exactas
                        first_path = os.path.normpath(first_path)
                        found_paths.add(first_path)
                        found_games.add(name)  # Rastrear que este juego fue encontrado
                    else:
                        missing_games.append(name)

                # 4) Actualizar UI en el hilo principal
                self.after(0, lambda: self._apply_game_list_results(found_paths, missing_games, total_games, len(found_games)))
                
            except Exception as e:
                self.after(0, lambda: (
                    messagebox.showerror(self.traducir("error"), f"Error al procesar la lista:\n{e}"),
                    self.status_label.configure(text=self.traducir("error"), text_color="red")
                ))
        
        # Ejecutar en hilo separado
        threading.Thread(target=process_in_thread, daemon=True).start()
    
    def _apply_game_list_results(self, found_paths: set[str], missing_games: list[str], total_games: int, found_games_count: int):
        """Aplica los resultados del procesamiento de la lista en el hilo principal"""
        try:
            # 4) Actualiza los checks - normalizar todos los paths
            self._checked_paths.clear()
            # Normalizar todos los paths para asegurar coincidencias exactas
            normalized_paths = {os.path.normpath(p) for p in found_paths}
            self._checked_paths.update(normalized_paths)

            # 🔄 refresca lo que esté en pantalla para mostrar los checks marcados
            current_folder = getattr(self, "current_folder", None)
            if current_folder and getattr(self, "_current_entries", None):
                # Refrescar la vista actual para mostrar los checks
                self._render_files(self._current_entries)
            self._update_counts()

            # 5) Navegar a la carpeta que contiene los archivos encontrados
            # Priorizar la carpeta actual si hay archivos encontrados ahí
            if found_paths:
                # Verificar si alguno de los paths encontrados está en la carpeta actual
                paths_in_current = False
                if current_folder:
                    current_norm = os.path.normpath(current_folder)
                    for path in found_paths:
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
                        parents = [os.path.dirname(p.rstrip("\\/")) for p in found_paths]
                        # idealmente abre donde los hijos directos ya son los marcados
                        best_parent, _ = Counter(parents).most_common(1)[0]
                        if best_parent and os.path.isdir(best_parent):
                            self._user_changed_folder = False  # Reset antes de cambiar programáticamente
                            self._enter_folder(best_parent)
                            self._user_changed_folder = False  # Mantener en False después
                    except Exception:
                        # fallback razonable
                        try:
                            common = os.path.commonpath(list(found_paths))
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

            # 6) Estado + faltantes
            self.status_label.configure(
                text=f"Procesados {total_games} juegos. Se encontraron {found_games_count} juegos ({len(found_paths)} carpetas).",
                text_color="green" if found_paths else "orange"
            )
            self._update_counts()
            if missing_games:
                self.after(50, lambda: self._show_missing_games_dialog(missing_games))
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

# -------------------- main --------------------
if __name__ == "__main__":
    app = XboxGameLookupApp()
    app.mainloop()
