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
DEFAULT_JSON_GLOBS = ["bd/*.json"]  # json(s) locales que se cargan automáticamente

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
    here = os.getcwd()
    bd_path = Path(here) / "bd"
    if not bd_path.is_dir():
        print("No se encontró la carpeta 'bd'. Los JSON no se cargarán automáticamente.")
        return

    for pat in DEFAULT_JSON_GLOBS:
        for fname in sorted(bd_path.glob(pat)):
            absf = os.path.abspath(str(fname))
            if absf in _loaded_files: continue
            try: load_json_file(absf)
            except Exception: pass

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
        
        # Datos (Ahora se cargan después de la interfaz)
        load_default_jsons()
        if hasattr(self, "_scan_roots"):
            for r in list(self._scan_roots):
                if os.path.isdir(r): self._scan_root(r)
                else:
                    try: self._scan_roots.remove(r)
                    except ValueError: pass

        self._update_db_summary()

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

        right = ctk.CTkFrame(frame_top, fg_color="transparent"); right.pack(side="right")
        # Selector de método de copia
        ctk.CTkLabel(right, text=f"🚚 {self.traducir('metodo_copia')}:").pack(side="left", padx=(0,6))
        self.copy_method_var = ctk.StringVar(value=self.copy_method)
        self.copy_method_menu = ctk.CTkOptionMenu(
            right,
            values=[ "auto", "explorer", "internal" ],
            variable=self.copy_method_var,
            command=self._on_change_copy_method,
            width=140
        )
        self.copy_method_menu.pack(side="left", padx=(0,12))

        self.btn_limpiar = ctk.CTkButton(right, text=self.traducir("limpiar_db"), command=self._limpiar_db)
        self.btn_limpiar.pack(side="right", padx=(6, 10))
        self.btn_cargar = ctk.CTkButton(right, text=self.traducir("cargar_json"), command=self._cargar_json)
        self.btn_cargar.pack(side="right", padx=(6, 6))
        self.btn_add_root = ctk.CTkButton(right, text=self.traducir("agregar_carpeta"), command=self._add_scan_root)
        self.btn_add_root.pack(side="right")

        self.label_entrada = ctk.CTkLabel(self, text=self.traducir("ingresa_texto")); self.label_entrada.pack(pady=(10, 0))
        self.entry = ctk.CTkEntry(self, placeholder_text="Ej: 4D530AA4 o Forza Horizon", width=780)
        self.entry.pack(pady=5); self.entry.bind("<Return>", self._buscar_todo)
        self.boton_buscar = ctk.CTkButton(self, text=self.traducir("buscar"), command=self._buscar_todo); self.boton_buscar.pack(pady=8)

        self.status_label = ctk.CTkLabel(self, text="", fg_color="transparent"); self.status_label.pack(pady=(0, 6))
        self.db_summary = ctk.CTkLabel(self, text="", fg_color="transparent"); self.db_summary.pack(pady=(0, 10))

        # Tabla Title IDs
        self.frame_title = ctk.CTkFrame(self); self.frame_title.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.label_title = ctk.CTkLabel(self.frame_title, text=self.traducir("title_ids")); self.label_title.pack(anchor="w")

        wrap_titles = ctk.CTkFrame(self.frame_title, fg_color="transparent"); wrap_titles.pack(fill="both", expand=True)
        columns_title = ("title_id","name","system")
        self.tree_title_ids = ttk.Treeview(wrap_titles, columns=columns_title, show="headings", height=12, selectmode="browse")
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
        ctk.CTkLabel(header, text=self.traducir("explorador")).pack(side="left", padx=(2, 8))
        self.path_label = ctk.CTkLabel(header, text=f"{self.traducir('ruta')} -"); self.path_label.pack(side="left")
        # ← Contador de seleccionados | marcados
        self.counts_label = ctk.CTkLabel(header, text="  |  0/0"); self.counts_label.pack(side="left", padx=(8, 0))

        hdr_right = ctk.CTkFrame(header, fg_color="transparent"); hdr_right.pack(side="right")
        # Botones de navegación
        self.btn_back = ctk.CTkButton(hdr_right, text=self.traducir("atras"), width=90, command=self._nav_back); self.btn_back.pack(side="right", padx=(6,4))
        self.btn_forward = ctk.CTkButton(hdr_right, text=self.traducir("adelante"), width=90, command=self._nav_forward); self.btn_forward.pack(side="right", padx=(6,4))
        self.btn_up = ctk.CTkButton(hdr_right, text=self.traducir("subir"), width=100, command=self._go_up); self.btn_up.pack(side="right", padx=(6,4))
        self.btn_open_explorer = ctk.CTkButton(hdr_right, text=self.traducir("abrir_explorer"), width=140, command=self._open_current_in_explorer); self.btn_open_explorer.pack(side="right", padx=(6,4))
        self.btn_change_folder = ctk.CTkButton(hdr_right, text=self.traducir("cambiar_carpeta"), width=120, command=self._change_browser_folder); self.btn_change_folder.pack(side="right", padx=(6,4))
        # Copiar selección y marcados
        self.btn_copy_rows = ctk.CTkButton(hdr_right, text=self.traducir("copiar_seleccion"), width=140, command=self._copy_selected_rows_browser)
        self.btn_copy_rows.pack(side="right", padx=(6,4))
        self.btn_mark_all = ctk.CTkButton(hdr_right, text=self.traducir("marcar_visibles"), width=130, command=self._mark_visible_rows)
        self.btn_mark_all.pack(side="right", padx=(6,4))
        self.btn_unmark_all = ctk.CTkButton(hdr_right, text=self.traducir("desmarcar_visibles"), width=150, command=self._unmark_visible_rows)
        self.btn_unmark_all.pack(side="right", padx=(6,4))
        self.btn_copy_marked = ctk.CTkButton(hdr_right, text=self.traducir("copiar_marcados"), width=140, command=self._copy_checked_items_from_browser)
        self.btn_copy_marked.pack(side="right", padx=(6,4))

        # Filtro
        filter_bar = ctk.CTkFrame(self.frame_explorer, fg_color="transparent"); filter_bar.pack(fill="x", padx=6, pady=(0,6))
        self.files_filter_var = ctk.StringVar(value="")
        self.files_filter_entry = ctk.CTkEntry(filter_bar, textvariable=self.files_filter_var,
                                               placeholder_text=self.traducir("filtro_placeholder"), width=520)
        self.files_filter_entry.pack(side="left", padx=(0,6))
        self.files_filter_entry.bind("<Return>", lambda e: self._apply_files_filter())
        self.files_filter_entry.bind("<KeyRelease>", lambda e: self._apply_files_filter(debounce=True))
        self.btn_filter = ctk.CTkButton(filter_bar, text=self.traducir("aplicar_filtro"), width=90, command=self._apply_files_filter)
        self.btn_filter.pack(side="left", padx=(0,6))
        self.btn_filter_clear = ctk.CTkButton(filter_bar, text=self.traducir("limpiar_filtro"), width=90, command=self._clear_files_filter)
        self.btn_filter_clear.pack(side="left")
        self.btn_cargar_lista = ctk.CTkButton(right, text="Cargar lista", command=self._cargar_lista)
        self.btn_cargar_lista.pack(side="right", padx=(6, 6))
        self.btn_paste_list = ctk.CTkButton(right, text="Pegar lista", command=self._pegar_lista_dialog)
        self.btn_paste_list.pack(side="right", padx=(6, 6))

        # Tabla de archivos (con columna de check)
        wrap_files = ctk.CTkFrame(self.frame_explorer, fg_color="transparent"); wrap_files.pack(fill="both", expand=True)
        columns_files = ("mark","name","type","size","modified","path")
        self.tree_files = ttk.Treeview(wrap_files, columns=columns_files, show="headings", height=12, selectmode="extended")
        self.tree_files["displaycolumns"] = ("mark","name","type","size","modified")

        self.tree_files.heading("mark", text=self.traducir("col_sel"))
        self.tree_files.heading("name", text=self.traducir("nombre"))
        self.tree_files.heading("type", text=self.traducir("tipo"))
        self.tree_files.heading("size", text=self.traducir("tamano"))
        self.tree_files.heading("modified", text=self.traducir("modificado"))
        self.tree_files.heading("path", text="Path")

        self.tree_files.column("mark", width=60, stretch=False, anchor="center")
        self.tree_files.column("name", width=560, stretch=True)
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
        self.boton_buscar.configure(text=self.traducir("buscar"))
        self.switch.configure(text=self.traducir("modo_oscuro"))
        self.idioma_menu_label.configure(text=f"🌐 {self.traducir('idioma')}:")
        # etiquetas del método de copia (mostrar texto amistoso en tooltip rápido)
        method = self.copy_method_var.get()
        self.copy_method_menu.configure(values=["auto","explorer","internal"])
        self.btn_cargar.configure(text=self.traducir("cargar_json"))
        self.btn_limpiar.configure(text=self.traducir("limpiar_db"))
        self.btn_add_root.configure(text=self.traducir("agregar_carpeta"))
        self.label_title.configure(text=self.traducir("title_ids"))
        self.btn_back.configure(text=self.traducir("atras"))
        self.btn_forward.configure(text=self.traducir("adelante"))
        self.btn_up.configure(text=self.traducir("subir"))
        self.btn_open_explorer.configure(text=self.traducir("abrir_explorer"))
        self.btn_change_folder.configure(text=self.traducir("cambiar_carpeta"))
        self.btn_copy_rows.configure(text=self.traducir("copiar_seleccion"))
        self.btn_copy_marked.configure(text=self.traducir("copiar_marcados"))
        self.btn_mark_all.configure(text=self.traducir("marcar_visibles"))
        self.btn_unmark_all.configure(text=self.traducir("desmarcar_visibles"))
        self.path_label.configure(text=f"{self.traducir('ruta')} -")
        self.files_filter_entry.configure(placeholder_text=self.traducir("filtro_placeholder"))
        self.btn_filter.configure(text=self.traducir("aplicar_filtro"))
        self.btn_filter_clear.configure(text=self.traducir("limpiar_filtro"))
        self.tree_files.heading("mark", text=self.traducir("col_sel"))
        self.tree_files.heading("name", text=self.traducir("nombre"))
        self.tree_files.heading("type", text=self.traducir("tipo"))
        self.tree_files.heading("size", text=self.traducir("tamano"))
        self.tree_files.heading("modified", text=self.traducir("modificado"))
        # refrescar contador
        self._update_counts()

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

    def _update_db_summary(self):
        files = len(_loaded_files)
        rows  = len(_items_by_key)
        by_sys = summarize_by_system()
        tid_paths = sum(len(v) for v in getattr(self, "_paths_by_tid", {}).values()) if hasattr(self, "_paths_by_tid") else 0
        roots = len(getattr(self, "_scan_roots", []) or [])
        extra = f" | Carpetas origen: {roots} | Coincidencias TID↔ruta: {tid_paths}"
        self.db_summary.configure(text=self.traducir("resumen_db").format(files=files, rows=rows, by_system=by_sys) + extra)

    # ---------- búsqueda local ----------
    def _buscar_todo(self, event=None):
        query = self.entry.get().strip()
        if not query:
            messagebox.showerror(self.traducir("error"), self.traducir("ingresa_texto")); return

        for item in self.tree_title_ids.get_children(): self.tree_title_ids.delete(item)
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
                self.status_label.configure(text=self.traducir("no_results_found"), text_color="orange"); return
            for it in results:
                self.tree_title_ids.insert("", "end", values=(it["title_id"], it["name"], it["system"]))
            self.status_label.configure(text=self.traducir("busqueda_completada"), text_color="green")
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

    def _scan_root(self, root):
        if not hasattr(self, "_paths_by_tid"):
            self._paths_by_tid = {}
        if not hasattr(self, "_paths_by_name"):
            self._paths_by_name = {}

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

    def _enter_folder(self, folder):
        folder = os.path.normpath(folder)
        if not self._nav_history or self._nav_history[self._nav_index] != folder:
            self._nav_history = self._nav_history[: self._nav_index + 1]
            self._nav_history.append(folder); self._nav_index += 1
        self._list_folder(folder); self._update_nav_buttons()

    def _nav_back(self):
        if self._nav_index > 0:
            self._nav_index -= 1
            self._list_folder(self._nav_history[self._nav_index]); self._update_nav_buttons()

    def _nav_forward(self):
        if self._nav_index < len(self._nav_history) - 1:
            self._nav_index += 1
            self._list_folder(self._nav_history[self._nav_index]); self._update_nav_buttons()

    # ---------- Explorador ----------
    def _browse_selected_game(self):
        tid = self._get_selected_tid()
        if not tid: return
        paths = self._find_paths_for_tid(tid)
        if not paths:
            messagebox.showinfo(self.traducir("info"), self.traducir("no_carpeta_tid")); return
        src = self._choose_path_dialog(paths, title=self.traducir("ver_archivos"))
        if not src: return
        self._enter_folder(src)

    def _list_folder(self, folder):
        try: self._size_thread_stop.set()
        except Exception: pass
        self._size_thread_stop = threading.Event()

        self.current_folder = folder
        self.path_label.configure(text=f"{self.traducir('ruta')} {folder}")

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
                    entries.append((e.name, ftype, size, mtime, e.path))

            entries.sort(key=lambda x: (x[1] != "Carpeta", x[0].lower()))
            self._current_entries = entries
            self._render_files(entries)
            self._clear_files_filter()
            self._start_dirsize_worker(entries, folder, self._size_thread_stop)
            self._update_counts()

        except Exception as e:
            messagebox.showerror(self.traducir("error"), str(e))

    def _render_files(self, entries):
        for iid in self.tree_files.get_children(): self.tree_files.delete(iid)
        self._files_row_by_path.clear()

        for name, ftype, size, mtime, path in entries:
            mark = "☑" if path in self._checked_paths else "☐"
            if size is None and os.path.isdir(path):
                size_text = self.traducir("calculando")
            else:
                size_text = fmt_size(size if isinstance(size, (int, float)) else 0)
            iid = self.tree_files.insert("", "end",
                values=(mark, name, ftype, size_text, fmt_mtime(mtime), path))
            self._files_row_by_path[path] = iid
        self._update_counts()

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
        for name, ftype, size, mtime, path in entries:
            if (q in name.lower()) or (q in ftype.lower()) or (q in path.lower()):
                filtered.append((name, ftype, size, mtime, path))
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
        current_mark, name, ftype, size_text, mod, path = vals
        # toggle
        if path in self._checked_paths:
            self._checked_paths.remove(path); new_mark = "☐"
        else:
            self._checked_paths.add(path); new_mark = "☑"
        self.tree_files.set(row, "mark", new_mark)
        self._update_counts()
        return "break"  # evita seleccionar fila al hacer clic en el check

    def _mark_visible_rows(self):
        for row in self.tree_files.get_children():
            vals = self.tree_files.item(row, "values")
            if not vals: continue
            path = vals[-1]
            self._checked_paths.add(path)
            self.tree_files.set(row, "mark", "☑")
        self._update_counts()

    def _unmark_visible_rows(self):
        for row in self.tree_files.get_children():
            vals = self.tree_files.item(row, "values")
            if not vals: continue
            path = vals[-1]
            if path in self._checked_paths: self._checked_paths.remove(path)
            self.tree_files.set(row, "mark", "☐")
        self._update_counts()

    def _open_or_enter(self):
        sel = self.tree_files.focus()
        if not sel: return
        vals = self.tree_files.item(sel, "values")
        if not vals: return
        _mark, _name, ftype, _sz, _mt, path = vals
        try:
            if os.path.isdir(path): self._enter_folder(path)
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
        if parent and parent != folder: self._enter_folder(parent)

    def _open_current_in_explorer(self):
        folder = getattr(self, "current_folder", None)
        if not folder: return
        try: os.startfile(folder)
        except Exception as e: messagebox.showerror(self.traducir("error"), str(e))

    def _change_browser_folder(self):
        folder = filedialog.askdirectory(title=self.traducir("cambiar_carpeta"))
        if folder: self._enter_folder(folder)

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
            for _name, _ftype, size, _mt, path in entries:
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
        """Copia las filas seleccionadas (resaltadas) del explorador."""
        sels = self.tree_files.selection()
        if not sels:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado"))
            return
        paths = []
        for sid in sels:
            vals = self.tree_files.item(sid, "values")
            if vals:
                paths.append(vals[-1])  # columna 'path'
        dst_root = filedialog.askdirectory(title=self.traducir("elige_destino"))
        if not dst_root:
            return
        self._copy_items_with_progress(paths, dest_base=dst_root, keep_names=True, include_top_dir=True)

    def _copy_checked_items_from_browser(self):
        if not self._checked_paths:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado")); return
        dst_root = filedialog.askdirectory(title=self.traducir("elige_destino"))
        if not dst_root: return
        items = list(self._checked_paths)
        self._copy_items_with_progress(items, dest_base=dst_root, keep_names=True, include_top_dir=True)

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
        to_str   = os.path.abspath(dest_base) + "\0"

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
        No requiere pywin32. Muestra el diálogo nativo de Windows.
        """
        import os, sys
        if not sources:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguno_marcado"))
            return
        if not sys.platform.startswith("win"):
            messagebox.showerror(self.traducir("error"), "Esta copia solo está disponible en Windows.")
            return

        # Normaliza rutas y asegura carpeta destino
        os.makedirs(dest_base, exist_ok=True)
        srcs = []
        for s in sources:
            s = os.path.abspath(s)
            if os.path.isdir(s) and not include_top_dir:
                srcs.append(os.path.join(s, "*"))   # copiar solo contenido
            else:
                srcs.append(s)                       # copiar carpeta/archivo tal cual

        # Llama a SHFileOperation
        return self._copy_with_explorer_ctypes(srcs, dest_base)


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
        to_str   = os.path.abspath(dest_dir) + "\0"

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

    def _process_game_list(self, list_content: str):
        """
        Procesa una lista de juegos, los marca y muestra el resumen.
        """
        self.status_label.configure(text="Procesando lista...", text_color="orange")
        self.update_idletasks()

        found_paths = set()
        total_games = 0
        missing_games = []
        
        try:
            game_names = [name.strip() for name in list_content.replace('\n', ',').split(',') if name.strip()]
            total_games = len(game_names)
            
            for name in game_names:
                norm_n = norm_text(name)
                matching_ids = {it["title_id"] for nname, it in _index_name if norm_n in nname}
                
                paths_found_for_name = set()
                for tid in matching_ids:
                    paths = self._find_paths_for_tid(tid)
                    paths_found_for_name.update(paths)
                
                if norm_n in getattr(self, "_paths_by_name", {}):
                    paths_found_for_name.update(self._paths_by_name[norm_n])

                if paths_found_for_name:
                    found_paths.update(paths_found_for_name)
                else:
                    missing_games.append(name)

        except Exception as e:
            messagebox.showerror(self.traducir("error"), f"Error al procesar la lista:\n{e}")
            self.status_label.configure(text=self.traducir("error"), text_color="red")
            return

        # 1. Limpia las marcas previas y añade las nuevas
        self._checked_paths.clear()
        for p in found_paths:
            self._checked_paths.add(p)
        
        self._render_files(getattr(self, "_current_entries", []) or [])

        # 2. Navega al primer directorio raíz para mostrar los resultados
        # Esto es crucial para que se refresque la vista
        if getattr(self, "_scan_roots", []):
            self._enter_folder(self._scan_roots[0])
        elif found_paths:
             self._enter_folder(os.path.dirname(os.path.dirname(next(iter(found_paths)))))

        # 3. Muestra el mensaje de estado
        self.status_label.configure(
            text=f"Procesados {total_games} juegos. Se encontraron {len(found_paths)} carpetas.", 
            text_color="green"
        )
        self._update_counts()

        # 4. Muestra la ventana de juegos faltantes si los hay
        if missing_games:
            self.after(50, lambda: self._show_missing_games_dialog(missing_games))


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

# -------------------- main --------------------
if __name__ == "__main__":
    app = XboxGameLookupApp()
    app.mainloop()
