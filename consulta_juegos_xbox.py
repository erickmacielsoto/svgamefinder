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
from PIL import Image, ImageTk

# -------------------- Módulos locales --------------------
from config import CONFIG_FILE, get_app_root
from translations import traducciones
from utils import norm_text, fmt_size, fmt_mtime
from ui_components import CTkTooltip
from game_data import (
    clear_db, load_json_file, load_default_jsons, summarize_by_system,
    get_loaded_files_count, get_items_count, search_by_tid, search_by_name,
    get_index_tid, get_index_name, get_items_by_key
)

ctk.set_default_color_theme("blue")

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
        "limpiar_lista": "Limpiar lista",
        "pegar_lista": "Pegar lista",
        "cargar_lista": "Cargar lista",
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
        "mostrar_nombres": "Mostrar nombres",
        # Tooltips
        "limpiar_lista_tooltip": "Elimina todos los juegos de la lista cargada",
        "pegar_lista_tooltip": "Pega una lista de juegos desde el portapapeles",
        "cargar_lista_tooltip": "Carga una lista de juegos desde un archivo",
        "limpiar_db_tooltip": "Limpia todos los archivos JSON cargados",
        "cargar_json_tooltip": "Carga un archivo JSON con datos de juegos",
        "agregar_carpeta_tooltip": "Agrega una carpeta para indexar juegos",
        "atras_tooltip": "Navega hacia atrás en el historial",
        "adelante_tooltip": "Navega hacia adelante en el historial",
        "subir_tooltip": "Sube un nivel en la jerarquía de carpetas",
        "abrir_explorer_tooltip": "Abre la carpeta actual en el Explorador de Windows",
        "cambiar_carpeta_tooltip": "Cambia la carpeta actual del explorador",
        "seleccionar_todo_tooltip": "Selecciona todos los archivos visibles",
        "marcar_visibles_tooltip": "Marca todos los archivos visibles",
        "desmarcar_visibles_tooltip": "Desmarca todos los archivos visibles",
        "copiar_seleccion_tooltip": "Copia los archivos seleccionados",
        "copiar_marcados_tooltip": "Copia los archivos marcados",
        "limpiar_seleccion_tooltip": "Limpia la selección y los marcados",
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
        "mostrar_nombres": "Show names",
        # Tooltips
        "limpiar_lista_tooltip": "Clears all games from the loaded list",
        "pegar_lista_tooltip": "Pastes a list of games from clipboard",
        "cargar_lista_tooltip": "Loads a list of games from a file",
        "limpiar_db_tooltip": "Clears all loaded JSON files",
        "cargar_json_tooltip": "Loads a JSON file with game data",
        "agregar_carpeta_tooltip": "Adds a folder to index games",
        "atras_tooltip": "Navigate back in history",
        "adelante_tooltip": "Navigate forward in history",
        "subir_tooltip": "Go up one level in folder hierarchy",
        "abrir_explorer_tooltip": "Opens current folder in Windows Explorer",
        "cambiar_carpeta_tooltip": "Changes the current explorer folder",
        "seleccionar_todo_tooltip": "Selects all visible files",
        "marcar_visibles_tooltip": "Checks all visible files",
        "desmarcar_visibles_tooltip": "Unchecks all visible files",
        "copiar_seleccion_tooltip": "Copies selected files",
        "copiar_marcados_tooltip": "Copies checked files",
        "limpiar_seleccion_tooltip": "Clears selection and checked items",
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
        "mostrar_nombres": "Mostrar nomes",
        # Tooltips
        "limpiar_lista_tooltip": "Remove todos os jogos da lista carregada",
        "pegar_lista_tooltip": "Cola uma lista de jogos da área de transferência",
        "cargar_lista_tooltip": "Carrega uma lista de jogos de um arquivo",
        "limpiar_db_tooltip": "Limpa todos os arquivos JSON carregados",
        "cargar_json_tooltip": "Carrega um arquivo JSON com dados de jogos",
        "agregar_carpeta_tooltip": "Adiciona uma pasta para indexar jogos",
        "atras_tooltip": "Navega para trás no histórico",
        "adelante_tooltip": "Navega para frente no histórico",
        "subir_tooltip": "Sobe um nível na hierarquia de pastas",
        "abrir_explorer_tooltip": "Abre a pasta atual no Explorador do Windows",
        "cambiar_carpeta_tooltip": "Altera a pasta atual do explorador",
        "seleccionar_todo_tooltip": "Seleciona todos os arquivos visíveis",
        "marcar_visibles_tooltip": "Marca todos os arquivos visíveis",
        "desmarcar_visibles_tooltip": "Desmarca todos os arquivos visíveis",
        "copiar_seleccion_tooltip": "Copia os arquivos selecionados",
        "copiar_marcados_tooltip": "Copia os arquivos marcados",
        "limpiar_seleccion_tooltip": "Limpa a seleção e os marcados",
    }
}

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
        self.copy_method = "explorer"  # "auto" | "explorer" | "internal"
        self.mostrar_nombres_botones = True  # Por defecto mostrar nombres
        self.cliente_id = ""  # Identificador del cliente
        self._cargar_config()
        self._actualizar_titulo_ventana()  # Actualizar título con el identificador del cliente
        self._aplicar_estilo_treeview("dark" if self.modo_oscuro_inicial else "light")
        ctk.set_appearance_mode("dark" if self.modo_oscuro_inicial else "light")
        
        # Cargar iconos (si existen)
        self._load_icons()

        # Inicializar variables antes de setup_ui para evitar errores
        self._checked_paths = set()
        self._last_checked_paths_for_size = set()
        self._marked_size_thread = None
        self._marked_size_stop = threading.Event()
        
        # UI
        self._setup_ui()
        self._update_ui_texts()
        # Aplicar iconos a los botones después de crear la UI
        self._apply_icons_to_buttons()
        # Aplicar preferencia de mostrar/ocultar nombres después de aplicar iconos
        if hasattr(self, 'show_names_var'):
            self._toggle_button_names()
        
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

        # Navegación + tamaños + checks (inicializar después de crear la UI)
        self._nav_history = []
        self._nav_index = -1
        self._folder_size_cache = {}
        self._size_thread = None
        self._size_thread_stop = threading.Event()
        self._files_row_by_path = {}
        self._current_entries = []
        self._filter_job = None
        # _checked_paths, _last_checked_paths_for_size, _marked_size_thread, _marked_size_stop ya inicializados arriba
        self._user_changed_folder = False  # Rastrea si el usuario cambió manualmente la carpeta

    def _load_icons(self):
        """Carga los iconos desde la carpeta 'icons' si existen"""
        self.icons = {}
        icons_dir = Path(get_app_root()) / "icons"
        
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
            'cargar_json': 'download.png',  # También busca 'dowload.png' por si hay un typo
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
        global traducciones
        # Asegurarse de que el idioma existe, si no usar español por defecto
        idioma = self.idioma_actual if self.idioma_actual in traducciones else 'es'
        resultado = traducciones[idioma].get(clave)
        if resultado is None:
            # Intentar con español como fallback
            resultado = traducciones.get('es', {}).get(clave)
        if resultado is None:
            # Si no existe, recargar el módulo una vez y volver a intentar
            if not hasattr(self, '_translations_reloaded'):
                try:
                    import importlib
                    import translations as translations_module
                    importlib.reload(translations_module)
                    from translations import traducciones as traducciones_nuevas
                    traducciones = traducciones_nuevas
                    self._translations_reloaded = True
                    # Intentar de nuevo después de recargar
                    resultado = traducciones[idioma].get(clave)
                    if resultado is None:
                        resultado = traducciones.get('es', {}).get(clave)
                except Exception:
                    pass
            # Si aún no existe, devolver un texto más legible
            if resultado is None:
                return clave.replace('_', ' ').title()
        return resultado

    def _guardar_config(self):
        config = {
            "idioma": self.idioma_actual,
            "modo_oscuro": self.switch_var.get(),
            "mostrar_nombres_botones": self.show_names_var.get() if hasattr(self, 'show_names_var') else True,
            "scan_roots": getattr(self, "_scan_roots", []),
            "copy_method": self.copy_method,
            "cliente_id": getattr(self, "cliente_id", ""),
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
                if config.get("mostrar_nombres_botones") is not None: 
                    self.mostrar_nombres_botones = config["mostrar_nombres_botones"]
                self._scan_roots = config.get("scan_roots", [])
                if config.get("copy_method") in ("auto","explorer","internal"):
                    self.copy_method = config["copy_method"]
                self.cliente_id = config.get("cliente_id", "")
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

    def _actualizar_titulo_ventana(self):
        """Actualiza el título de la ventana incluyendo el identificador del cliente"""
        titulo_base = "SVXboxGamesFinder (Local) - By: @erickmacielsoto - Reviewed by: @jasontorresb"
        if self.cliente_id and self.cliente_id.strip():
            self.title(f"[{self.cliente_id}] {titulo_base}")
        else:
            self.title(titulo_base)
    
    def _cambiar_cliente(self):
        """Abre un diálogo para cambiar el identificador del cliente"""
        dlg = ctk.CTkToplevel(self)
        # Obtener traducciones de forma segura - usar el idioma actual de la aplicación
        idioma_actual = self.idioma_actual if hasattr(self, 'idioma_actual') and self.idioma_actual in traducciones else 'es'
        
        # Obtener textos traducidos
        titulo = traducciones[idioma_actual].get("cambiar_cliente", "Cambiar Cliente")
        texto_label = traducciones[idioma_actual].get("ingresa_cliente", "Ingresa el identificador del cliente:")
        texto_ok = traducciones[idioma_actual].get("ok", "OK")
        texto_cancelar = traducciones[idioma_actual].get("cancelar", "Cancelar")
        texto_guardado = traducciones[idioma_actual].get("cliente_guardado", "Cliente guardado")
        
        dlg.title(titulo)
        dlg.geometry("400x150")
        dlg.grab_set()
        dlg.transient(self)
        
        # Centrar la ventana
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth() // 2) - (400 // 2)
        y = (dlg.winfo_screenheight() // 2) - (150 // 2)
        dlg.geometry(f"400x150+{x}+{y}")
        
        # Label
        label = ctk.CTkLabel(dlg, text=texto_label, font=ctk.CTkFont(size=12))
        label.pack(pady=(20, 10))
        
        # Entry
        entry_var = ctk.StringVar(value=self.cliente_id)
        entry = ctk.CTkEntry(dlg, textvariable=entry_var, width=300, font=ctk.CTkFont(size=12))
        entry.pack(pady=10)
        entry.focus()
        entry.select_range(0, "end")
        
        # Botones
        btn_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        def guardar():
            nuevo_cliente = entry_var.get().strip()
            self.cliente_id = nuevo_cliente
            self._actualizar_titulo_ventana()
            self._guardar_config()
            dlg.destroy()
            if nuevo_cliente:
                self.status_label.configure(
                    text=f"{texto_guardado}: {nuevo_cliente}", 
                    text_color="green"
                )
                self.after(3000, lambda: self.status_label.configure(text="", text_color="gray"))
        
        btn_guardar = ctk.CTkButton(btn_frame, text=texto_ok, command=guardar, width=100)
        btn_guardar.pack(side="left", padx=5)
        
        btn_cancelar = ctk.CTkButton(btn_frame, text=texto_cancelar, 
                                    command=dlg.destroy, width=100, fg_color="gray")
        btn_cancelar.pack(side="left", padx=5)
        
        # Bind Enter y Escape
        entry.bind("<Return>", lambda e: guardar())
        dlg.bind("<Escape>", lambda e: dlg.destroy())
        
        # Permitir Enter para guardar
        entry.bind("<Return>", lambda e: guardar())
        dlg.bind("<Escape>", lambda e: dlg.destroy())
    
    def _toggle_mode(self):
        ctk.set_appearance_mode("dark" if self.switch_var.get() else "light")
        self._aplicar_estilo_treeview("dark" if self.switch_var.get() else "light")
        self._guardar_config()
    
    def _toggle_button_names(self):
        """Oculta o muestra los nombres de los botones"""
        show_names = self.show_names_var.get()
        self.mostrar_nombres_botones = show_names
        
        # Obtener el idioma actual de forma segura
        idioma_actual = getattr(self, 'idioma_actual', 'es')
        if idioma_actual not in traducciones:
            idioma_actual = 'es'
        
        # Mapeo de botones a sus textos traducidos (usar traducciones directamente)
        # NOTA: Los botones con iconos de imagen NO deben tener emojis en el texto
        button_texts = {
            # Botones superiores (sin emojis porque tienen iconos de imagen)
            'btn_limpiar_lista': traducciones[idioma_actual].get('limpiar_lista', 'Limpiar lista'),
            'btn_paste_list': traducciones[idioma_actual].get('pegar_lista', 'Pegar lista'),
            'btn_cargar_lista': traducciones[idioma_actual].get('cargar_lista', 'Cargar lista'),
            'btn_limpiar': traducciones[idioma_actual].get('limpiar_db', 'Limpiar .json'),
            'btn_cargar': traducciones[idioma_actual].get('cargar_json', 'Cargar .json'),
            'btn_add_root': traducciones[idioma_actual].get('agregar_carpeta', 'Agregar carpeta'),
            # Botones explorador (sin emojis porque tienen iconos de imagen)
            'btn_back': traducciones[idioma_actual].get('atras', 'Atrás'),
            'btn_forward': traducciones[idioma_actual].get('adelante', 'Adelante'),
            'btn_up': traducciones[idioma_actual].get('subir', 'Subir nivel'),
            'btn_open_explorer': traducciones[idioma_actual].get('abrir_explorer', 'Abrir en Explorer'),
            'btn_change_folder': traducciones[idioma_actual].get('cambiar_carpeta', 'Cambiar…'),
            'btn_select_all': traducciones[idioma_actual].get('seleccionar_todo', 'Seleccionar todo'),
            'btn_mark_all': traducciones[idioma_actual].get('marcar_visibles', 'Marcar visibles'),
            'btn_unmark_all': traducciones[idioma_actual].get('desmarcar_visibles', 'Desmarcar visibles'),
            'btn_copy_rows': traducciones[idioma_actual].get('copiar_seleccion', 'Copiar selección'),
            'btn_copy_marked': traducciones[idioma_actual].get('copiar_marcados', 'Copiar marcados'),
            'btn_limpiar_seleccion': traducciones[idioma_actual].get('limpiar_seleccion', 'Limpiar selección'),
            'btn_filter': traducciones[idioma_actual].get('aplicar_filtro', 'Buscar'),
            'btn_filter_clear': traducciones[idioma_actual].get('limpiar_filtro', 'Limpiar'),
            'boton_buscar': traducciones[idioma_actual].get('buscar', 'Buscar'),
        }
        
        for button_attr, text_key in button_texts.items():
            if hasattr(self, button_attr):
                button = getattr(self, button_attr)
                try:
                    # Obtener el icono desde el diccionario de iconos cargados
                    current_image = None
                    icon_key_map = {
                        'btn_limpiar_lista': 'limpiar_lista',
                        'btn_paste_list': 'pegar_lista',
                        'btn_cargar_lista': 'cargar_lista',
                        'btn_limpiar': 'limpiar_json',
                        'btn_cargar': 'cargar_json',
                        'btn_add_root': 'agregar_carpeta',
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
                    icon_key = icon_key_map.get(button_attr)
                    if icon_key and hasattr(self, 'icons') and icon_key in self.icons:
                        current_image = self.icons[icon_key]
                    else:
                        # Intentar obtener el icono actual del botón como fallback
                        try:
                            img_value = button.cget("image")
                            if img_value:
                                current_image = img_value
                        except:
                            pass
                    
                    if show_names:
                        # Mostrar nombre: icono + texto
                        if current_image:
                            button.configure(text=text_key, image=current_image, compound="left")
                        else:
                            button.configure(text=text_key, image="")
                    else:
                        # Ocultar nombre: solo icono
                        if current_image:
                            button.configure(text="", image=current_image)
                        else:
                            # Si no hay icono, mantener el texto (no podemos ocultarlo sin icono)
                            button.configure(text=text_key)
                except Exception as e:
                    print(f"Error actualizando botón {button_attr}: {e}")
        
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
        
        # Switch para mostrar/ocultar nombres de botones
        self.show_names_var = ctk.BooleanVar(value=self.mostrar_nombres_botones)
        self.switch_names = ctk.CTkSwitch(left, text=self.traducir("mostrar_nombres"),
                                         variable=self.show_names_var, command=self._toggle_button_names)
        self.switch_names.pack(side="left", padx=(10, 10))
        
        self.idioma_menu_label = ctk.CTkLabel(left, text=f"🌐 {self.traducir('idioma')}:")
        self.idioma_menu_label.pack(side="left", padx=(10, 5))
        self.selector_idioma = ctk.CTkOptionMenu(left, values=["Español", "English", "Português"],
                                                 command=self._cambiar_idioma)
        self.selector_idioma.pack(side="left")
        self.selector_idioma.set({"es":"Español","en":"English","pt":"Português"}.get(self.idioma_actual,"Español"))
        
        # Botón para cambiar identificador de cliente
        cliente_text = traducciones.get(self.idioma_actual, traducciones['es']).get('cambiar_cliente', 'Cambiar Cliente')
        self.btn_cliente = ctk.CTkButton(left, text=f"👤 {cliente_text}", 
                                       command=self._cambiar_cliente, width=120)
        self.btn_cliente.pack(side="left", padx=(10, 10))
        CTkTooltip(self.btn_cliente, cliente_text)

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
        
        # Espaciado uniforme para todos los botones
        BTN_PADX = (4, 4)
        BTN_PADY = 2
        
        # Obtener traducciones de forma segura
        idioma_ini = getattr(self, 'idioma_actual', 'es')
        if idioma_ini not in traducciones:
            idioma_ini = 'es'
        
        self.btn_limpiar_lista = ctk.CTkButton(right, text=traducciones[idioma_ini].get("limpiar_lista", "Limpiar lista"), command=self._limpiar_lista_cargada, width=110)
        self.btn_limpiar_lista.grid(row=0, column=2, padx=BTN_PADX, pady=BTN_PADY, sticky="w")
        CTkTooltip(self.btn_limpiar_lista, traducciones[idioma_ini].get("limpiar_lista", "Limpiar lista"))
        self.btn_paste_list = ctk.CTkButton(right, text=traducciones[idioma_ini].get("pegar_lista", "Pegar lista"), command=self._pegar_lista_dialog, width=110)
        self.btn_paste_list.grid(row=0, column=3, padx=BTN_PADX, pady=BTN_PADY, sticky="w")
        CTkTooltip(self.btn_paste_list, traducciones[idioma_ini].get("pegar_lista", "Pegar lista"))
        self.btn_cargar_lista = ctk.CTkButton(right, text=traducciones[idioma_ini].get("cargar_lista", "Cargar lista"), command=self._cargar_lista, width=110)
        self.btn_cargar_lista.grid(row=0, column=4, padx=BTN_PADX, pady=BTN_PADY, sticky="w")
        CTkTooltip(self.btn_cargar_lista, traducciones[idioma_ini].get("cargar_lista", "Cargar lista"))
        
        # Fila 2: Botones de JSON y carpeta (alineados con la fila 1, empezando en columna 2)
        self.btn_limpiar = ctk.CTkButton(right, text=f"🧹 {traducciones[idioma_ini].get('limpiar_db', 'Limpiar .json')}", command=self._limpiar_db, width=110)
        self.btn_limpiar.grid(row=1, column=2, padx=BTN_PADX, pady=BTN_PADY, sticky="w")
        CTkTooltip(self.btn_limpiar, traducciones[idioma_ini].get("limpiar_db", "Limpiar .json"))
        self.btn_cargar = ctk.CTkButton(right, text=f"📥 {traducciones[idioma_ini].get('cargar_json', 'Cargar .json')}", command=self._cargar_json, width=110)
        self.btn_cargar.grid(row=1, column=3, padx=BTN_PADX, pady=BTN_PADY, sticky="w")
        CTkTooltip(self.btn_cargar, traducciones[idioma_ini].get("cargar_json", "Cargar .json"))
        self.btn_add_root = ctk.CTkButton(right, text=f"📂 {traducciones[idioma_ini].get('agregar_carpeta', 'Agregar carpeta')}", command=self._add_scan_root, width=110)
        self.btn_add_root.grid(row=1, column=4, padx=BTN_PADX, pady=BTN_PADY, sticky="w")
        CTkTooltip(self.btn_add_root, traducciones[idioma_ini].get("agregar_carpeta", "Agregar carpeta"))
        self.btn_ver_carpetas = ctk.CTkButton(right, text=f"📋 {traducciones[idioma_ini].get('ver_carpetas', 'Ver carpetas')}", command=self._show_scan_roots_dialog, width=110)
        self.btn_ver_carpetas.grid(row=1, column=5, padx=BTN_PADX, pady=BTN_PADY, sticky="w")
        CTkTooltip(self.btn_ver_carpetas, traducciones[idioma_ini].get("ver_carpetas_tooltip", "Ver carpetas agregadas"))
        
        # Guardar anchos originales de los botones superiores
        self._top_button_widths = {
            'copy_method_menu': 120,
            'btn_limpiar_lista': 110,
            'btn_paste_list': 110,
            'btn_cargar_lista': 110,
            'btn_limpiar': 110,
            'btn_cargar': 110,
            'btn_add_root': 110,
            'btn_ver_carpetas': 110,
            'btn_cliente': 120,
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
        self.boton_buscar = ctk.CTkButton(entry_frame, text=self.traducir('buscar'), command=self._buscar_todo)
        self.boton_buscar.pack(side="right")
        CTkTooltip(self.boton_buscar, self.traducir("buscar"))

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
        self.marked_size_label = ctk.CTkLabel(header_info, text=f"  |  {self.traducir('tamano_marcados')}: -")
        self.marked_size_label.pack(side="left", padx=(8, 0))
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
        
        # Espaciado uniforme para todos los botones del explorador
        EXPLORER_BTN_PADX = (4, 4)
        EXPLORER_BTN_PADY = 2
        
        # Fila 1: Navegación básica (4 botones) - Sin emojis porque tienen iconos de imagen
        self.btn_back = ctk.CTkButton(buttons_container, text=self.traducir('atras'), width=90, command=self._nav_back)
        self.btn_back.grid(row=0, column=0, padx=EXPLORER_BTN_PADX, pady=EXPLORER_BTN_PADY)
        CTkTooltip(self.btn_back, self.traducir("atras"))  # Mostrar el nombre del botón en el tooltip
        self.btn_forward = ctk.CTkButton(buttons_container, text=self.traducir('adelante'), width=90, command=self._nav_forward)
        self.btn_forward.grid(row=0, column=1, padx=EXPLORER_BTN_PADX, pady=EXPLORER_BTN_PADY)
        CTkTooltip(self.btn_forward, self.traducir("adelante"))
        self.btn_up = ctk.CTkButton(buttons_container, text=self.traducir('subir'), width=100, command=self._go_up)
        self.btn_up.grid(row=0, column=2, padx=EXPLORER_BTN_PADX, pady=EXPLORER_BTN_PADY)
        CTkTooltip(self.btn_up, self.traducir("subir"))
        self.btn_open_explorer = ctk.CTkButton(buttons_container, text=self.traducir('abrir_explorer'), width=120, command=self._open_current_in_explorer)
        self.btn_open_explorer.grid(row=0, column=3, padx=EXPLORER_BTN_PADX, pady=EXPLORER_BTN_PADY)
        CTkTooltip(self.btn_open_explorer, self.traducir("abrir_explorer"))
        
        # Fila 2: Navegación y acciones (4 botones) - Sin emojis porque tienen iconos de imagen
        self.btn_change_folder = ctk.CTkButton(buttons_container, text=self.traducir('cambiar_carpeta'), width=120, command=self._change_browser_folder)
        self.btn_change_folder.grid(row=1, column=0, padx=EXPLORER_BTN_PADX, pady=EXPLORER_BTN_PADY)
        CTkTooltip(self.btn_change_folder, self.traducir("cambiar_carpeta"))
        self.btn_select_all = ctk.CTkButton(buttons_container, text=self.traducir('seleccionar_todo'), width=120, command=self._select_all_files)
        self.btn_select_all.grid(row=1, column=1, padx=EXPLORER_BTN_PADX, pady=EXPLORER_BTN_PADY)
        CTkTooltip(self.btn_select_all, self.traducir("seleccionar_todo"))
        self.btn_mark_all = ctk.CTkButton(buttons_container, text=self.traducir('marcar_visibles'), width=120, command=self._mark_visible_rows)
        self.btn_mark_all.grid(row=1, column=2, padx=EXPLORER_BTN_PADX, pady=EXPLORER_BTN_PADY)
        CTkTooltip(self.btn_mark_all, self.traducir("marcar_visibles"))
        self.btn_unmark_all = ctk.CTkButton(buttons_container, text=self.traducir('desmarcar_visibles'), width=120, command=self._unmark_visible_rows)
        self.btn_unmark_all.grid(row=1, column=3, padx=EXPLORER_BTN_PADX, pady=EXPLORER_BTN_PADY)
        CTkTooltip(self.btn_unmark_all, self.traducir("desmarcar_visibles"))
        
        # Fila 3: Acciones de copia (3 botones) - Sin emojis porque tienen iconos de imagen
        self.btn_copy_rows = ctk.CTkButton(buttons_container, text=self.traducir('copiar_seleccion'), width=120, command=self._copy_selected_rows_browser)
        self.btn_copy_rows.grid(row=2, column=0, padx=EXPLORER_BTN_PADX, pady=EXPLORER_BTN_PADY)
        CTkTooltip(self.btn_copy_rows, self.traducir("copiar_seleccion"))
        self.btn_copy_marked = ctk.CTkButton(buttons_container, text=self.traducir('copiar_marcados'), width=120, command=self._copy_checked_items_from_browser)
        self.btn_copy_marked.grid(row=2, column=1, padx=EXPLORER_BTN_PADX, pady=EXPLORER_BTN_PADY)
        CTkTooltip(self.btn_copy_marked, self.traducir("copiar_marcados"))
        self.btn_limpiar_seleccion = ctk.CTkButton(buttons_container, text=self.traducir('limpiar_seleccion'), width=120, command=self._limpiar_lista_cargada)
        self.btn_limpiar_seleccion.grid(row=2, column=2, padx=EXPLORER_BTN_PADX, pady=EXPLORER_BTN_PADY)
        CTkTooltip(self.btn_limpiar_seleccion, self.traducir("limpiar_seleccion"))
        
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
        self.btn_filter = ctk.CTkButton(filter_bar, text=self.traducir('aplicar_filtro'), width=90, command=self._apply_files_filter)
        self.btn_filter.pack(side="left", padx=(0,6))
        CTkTooltip(self.btn_filter, self.traducir("aplicar_filtro"))
        self.btn_filter_clear = ctk.CTkButton(filter_bar, text=self.traducir('limpiar_filtro'), width=90, command=self._clear_files_filter)
        self.btn_filter_clear.pack(side="left")
        CTkTooltip(self.btn_filter_clear, self.traducir("limpiar_filtro"))

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
        self.boton_buscar.configure(text=self.traducir('buscar'))
        self.switch.configure(text=self.traducir("modo_oscuro"))
        if hasattr(self, 'switch_names'):
            self.switch_names.configure(text=self.traducir("mostrar_nombres"))
        self.idioma_menu_label.configure(text=f"🌐 {self.traducir('idioma')}:")
        if hasattr(self, 'btn_cliente'):
            # Usar traducciones directamente para evitar problemas
            idioma_actual = getattr(self, 'idioma_actual', 'es')
            cliente_text = traducciones.get(idioma_actual, traducciones['es']).get('cambiar_cliente', 'Cambiar Cliente')
            # Actualizar el texto del botón
            self.btn_cliente.configure(text=f"👤 {cliente_text}")
            # Actualizar tooltip del botón cliente
            if not hasattr(self, '_btn_cliente_tooltip'):
                # Crear tooltip por primera vez
                self._btn_cliente_tooltip = CTkTooltip(self.btn_cliente, cliente_text)
            else:
                # Actualizar el texto del tooltip existente (el tooltip usa self.text cuando se muestra)
                self._btn_cliente_tooltip.text = cliente_text
        # etiquetas del método de copia (mostrar texto amistoso en tooltip rápido)
        method = self.copy_method_var.get()
        self.copy_method_menu.configure(values=["auto","explorer","internal"])
        # Actualizar textos de otros elementos (no botones con iconos)
        self.label_title.configure(text=self.traducir("title_ids"))
        self.path_label.configure(text=f"{self.traducir('ruta')} -")
        self.files_filter_entry.configure(placeholder_text=self.traducir("filtro_placeholder"))
        
        # Los textos de los botones se actualizarán en _toggle_button_names()
        # que respeta la preferencia de mostrar/ocultar nombres
        self.tree_files.heading("mark", text=self.traducir("col_sel"))
        self.tree_files.heading("name", text=self.traducir("nombre"))
        self.tree_files.heading("type", text=self.traducir("tipo"))
        self.tree_files.heading("size", text=self.traducir("tamano"))
        self.tree_files.heading("modified", text=self.traducir("modificado"))
        
        # Aplicar la preferencia de mostrar/ocultar nombres después de actualizar textos
        if hasattr(self, 'show_names_var'):
            self._toggle_button_names()
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
                'btn_limpiar', 'btn_cargar', 'btn_add_root', 'btn_cliente'
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
        self.selector_idioma.set(val); self._guardar_config(); self._update_ui_texts(); self._apply_icons_to_buttons(); 
        if hasattr(self, 'show_names_var'):
            self._toggle_button_names()
        self._actualizar_titulo_ventana()  # Actualizar título al cambiar idioma
        self._update_db_summary()

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
        files = get_loaded_files_count()
        rows  = get_items_count()
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
                tid = query.upper()
                results = sorted(search_by_tid(tid), key=lambda it: (it["system"], it["name"].lower()))
            else:
                results = search_by_name(query)
                results = sorted(results, key=lambda it: (it["name"].lower(), it["system"]))[:500]
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
        
        # Escanear en segundo plano para no bloquear la UI
        self.status_label.configure(text=self.traducir("escaneando_carpeta"), text_color="orange")
        threading.Thread(target=lambda: self._scan_root_async(path), daemon=True).start()

    def _scan_root_async(self, root):
        """Escanea una carpeta en segundo plano y actualiza la UI cuando termina."""
        try:
            self._scan_root(root, recursive=True)
            self.after(0, lambda: (
                self._update_db_summary(),
                self.status_label.configure(text=self.traducir("carpeta_indexada"), text_color="green")
            ))
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(
                text=f"Error al escanear: {e}", text_color="red"
            ))

    def _show_scan_roots_dialog(self):
        """Muestra un diálogo con las carpetas agregadas y permite eliminarlas."""
        if not hasattr(self, "_scan_roots") or not self._scan_roots:
            messagebox.showinfo(self.traducir("info"), self.traducir("ninguna_carpeta_agregada"))
            return
        
        dlg = ctk.CTkToplevel(self)
        dlg.title(self.traducir("carpetas_agregadas"))
        dlg.geometry("700x400")
        dlg.grab_set()
        
        ctk.CTkLabel(dlg, text=self.traducir("carpetas_agregadas_desc"), 
                    font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        
        # Frame con scrollbar para la lista
        frame_list = ctk.CTkFrame(dlg)
        frame_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        listbox = ctk.CTkTextbox(frame_list, width=680, height=250)
        listbox.pack(fill="both", expand=True, padx=5, pady=5)
        listbox.configure(state="normal")
        
        for i, path in enumerate(self._scan_roots, 1):
            listbox.insert("end", f"{i}. {path}\n")
        listbox.configure(state="disabled")
        
        btn_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_frame.pack(pady=(5, 10))
        
        def eliminar_seleccionada():
            # Obtener el índice seleccionado (simplificado: eliminar la última)
            # En una versión mejorada, se podría hacer selección múltiple
            if self._scan_roots:
                eliminada = self._scan_roots.pop()
                self._guardar_config()
                # Limpiar índices relacionados con esa carpeta
                if hasattr(self, "_paths_by_tid"):
                    tids_a_eliminar = []
                    for tid, paths in list(self._paths_by_tid.items()):
                        # Crear nuevo set sin la carpeta eliminada
                        paths_filtrados = {p for p in paths if p != eliminada and not p.startswith(eliminada + os.sep)}
                        if not paths_filtrados:
                            tids_a_eliminar.append(tid)
                        else:
                            self._paths_by_tid[tid] = paths_filtrados
                    for tid in tids_a_eliminar:
                        del self._paths_by_tid[tid]
                
                # Limpiar también _paths_by_name
                if hasattr(self, "_paths_by_name"):
                    for norm_name, paths in list(self._paths_by_name.items()):
                        paths_filtrados = {p for p in paths if p != eliminada and not p.startswith(eliminada + os.sep)}
                        if not paths_filtrados:
                            del self._paths_by_name[norm_name]
                        else:
                            self._paths_by_name[norm_name] = paths_filtrados
                dlg.destroy()
                self._update_db_summary()
                messagebox.showinfo(self.traducir("info"), self.traducir("carpeta_eliminada"))
        
        ctk.CTkButton(btn_frame, text=self.traducir("eliminar_ultima"), 
                     command=eliminar_seleccionada, width=150).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text=self.traducir("cancelar"), 
                     command=dlg.destroy, width=120).pack(side="left", padx=5)
        
        dlg.wait_window()

    def _scan_root(self, root, recursive=True):
        """
        Escanea una carpeta raíz e indexa los juegos encontrados.
        OPTIMIZADO: Hace una sola pasada en lugar de dos.
        Si recursive=False, solo escanea el nivel actual (no recursivo).
        """
        if not hasattr(self, "_paths_by_tid"):
            self._paths_by_tid = {}
        if not hasattr(self, "_paths_by_name"):
            self._paths_by_name = {}

        if recursive:
            # OPTIMIZACIÓN: Una sola pasada combinando indexación por TID y nombre
            items_by_tid = get_items_by_key()
            tid_to_names = {}  # Cache: TID -> nombres normalizados
            
            # Pre-cargar nombres normalizados de todos los juegos
            for it in items_by_tid.values():
                tid = it["title_id"]
                norm_name = norm_text(it["name"])
                if tid not in tid_to_names:
                    tid_to_names[tid] = []
                tid_to_names[tid].append(norm_name)
            
            # Una sola pasada: escanear y indexar por TID y nombre simultáneamente
            for dirpath, _, dirnames in os.walk(root):
                base = os.path.basename(dirpath)
                base_norm = norm_text(base)
                
                # Buscar Title ID en el nombre de la carpeta
                m = re.search(r'([0-9A-Fa-f]{8})', base)
                if m:
                    tid = m.group(1).upper()
                    self._paths_by_tid.setdefault(tid, set()).add(dirpath)
                    # Si conocemos el nombre del juego para este TID, indexarlo también
                    if tid in tid_to_names:
                        for norm_name in tid_to_names[tid]:
                            self._paths_by_name.setdefault(norm_name, set()).add(dirpath)
                
                # Buscar en subdirectorios que sean exactamente un TID
                for d in dirnames:
                    if re.fullmatch(r'[0-9A-Fa-f]{8}', d):
                        tid = d.upper()
                        full_path = os.path.join(dirpath, d)
                        self._paths_by_tid.setdefault(tid, set()).add(full_path)
                        # Indexar por nombre si conocemos el nombre del juego
                        if tid in tid_to_names:
                            for norm_name in tid_to_names[tid]:
                                self._paths_by_name.setdefault(norm_name, set()).add(full_path)
                
                # Búsqueda adicional por nombre (solo si no encontramos TID)
                # Esto ayuda cuando el nombre de la carpeta coincide con el nombre del juego
                if not m:  # Solo si no encontramos TID en el nombre
                    for tid, names in tid_to_names.items():
                        for norm_name in names:
                            if norm_name == base_norm or (len(norm_name) > 3 and norm_name in base_norm):
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
            index_tid = get_index_tid()
            if tid in index_tid:
                # Tomar el primer resultado (puede haber múltiples por consola)
                game_item = index_tid[tid][0]
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
        # marcados visibles (en la vista actual)
        marked_visible = 0
        for row in self.tree_files.get_children():
            vals = self.tree_files.item(row, "values")
            if not vals: continue
            path = vals[-1]
            path_norm = os.path.normpath(path)
            if path_norm in self._checked_paths:
                marked_visible += 1
        
        # Total de marcados (en todas las carpetas)
        total_marked = len(self._checked_paths)
        
        # Mostrar ambos: visibles y total
        if total_marked > marked_visible:
            self.counts_label.configure(
                text=f"  |  {self.traducir('seleccionados')}: {sel_count}  |  {self.traducir('marcados')}: {marked_visible}/{total_marked}"
            )
        else:
            self.counts_label.configure(
                text=f"  |  {self.traducir('seleccionados')}: {sel_count}  |  {self.traducir('marcados')}: {marked_visible}"
            )
        self._update_marked_size_async()

    def _set_marked_size_label(self, total_bytes=None, calculating=False):
        """Actualiza el label de tamaño total marcado (con soporte para 'calculando')."""
        if not hasattr(self, "marked_size_label"):
            return
        if calculating:
            size_txt = self.traducir("calculando")
        elif total_bytes is None:
            size_txt = "-"
        else:
            size_txt = fmt_size(total_bytes)
        self.marked_size_label.configure(
            text=f"  |  {self.traducir('tamano_marcados')}: {size_txt}"
        )

    def _update_marked_size_async(self):
        """Calcula en segundo plano el tamaño total de todo lo marcado."""
        if not hasattr(self, "marked_size_label"):
            return
        if not hasattr(self, "_checked_paths"):
            return

        paths = {p for p in self._checked_paths if os.path.exists(p)}

        # Si no hay paths marcados, resetear y salir
        if not paths:
            self._last_checked_paths_for_size = set()
            self._set_marked_size_label(total_bytes=0)
            try:
                if self._marked_size_stop:
                    self._marked_size_stop.set()
            except Exception:
                pass
            return

        # Evitar cálculos repetidos si no cambió el conjunto
        if paths == getattr(self, "_last_checked_paths_for_size", set()):
            return
        self._last_checked_paths_for_size = set(paths)

        # Cancelar cálculo previo si sigue corriendo
        try:
            if self._marked_size_stop:
                self._marked_size_stop.set()
        except Exception:
            pass

        stop_event = threading.Event()
        self._marked_size_stop = stop_event
        self._set_marked_size_label(calculating=True)

        def dir_size(p: str) -> int | None:
            total = 0
            for root, _dirs, files in os.walk(p):
                if stop_event.is_set():
                    return None
                for fname in files:
                    fp = os.path.join(root, fname)
                    try:
                        total += os.path.getsize(fp)
                    except Exception:
                        pass
            return total

        def worker():
            total = 0
            folder_cache = getattr(self, "_folder_size_cache", {})
            for p in paths:
                if stop_event.is_set():
                    return
                if os.path.isdir(p):
                    size = folder_cache.get(p)
                    if size is None:
                        size = dir_size(p)
                        if size is None:  # Cancelado
                            return
                        folder_cache[p] = size
                    total += size or 0
                else:
                    try:
                        total += os.path.getsize(p)
                    except Exception:
                        pass
            if stop_event.is_set():
                return
            self.after(0, lambda: self._set_marked_size_label(total_bytes=total))

        self._marked_size_thread = threading.Thread(target=worker, daemon=True)
        self._marked_size_thread.start()

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
            index_tid = get_index_tid()
            if tid and tid in index_tid:
                game_name = index_tid[tid][0].get("name", "")
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
        dlg.title(self.traducir("pegar_lista_dialog_titulo"))
        dlg.geometry("600x400")
        dlg.grab_set()

        ctk.CTkLabel(dlg, text=self.traducir("pegar_lista_dialog_desc")).pack(pady=10)
        
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
        ctk.CTkButton(btn_frame, text=self.traducir("aceptar"), command=on_paste_and_go).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text=self.traducir("cancelar"), command=on_cancel).pack(side="left", padx=5)

        dlg.wait_window()

    def _show_missing_games_dialog(self, missing_games: list[str]):
        """
        Muestra una ventana con la lista de juegos que no se encontraron, con conteo.
        """
        dlg = ctk.CTkToplevel(self)
        dlg.title(f"{self.traducir('juegos_faltantes_titulo')} ({len(missing_games)})")
        dlg.geometry("500x400")
        dlg.grab_set()

        ctk.CTkLabel(dlg, text=f"{self.traducir('juegos_faltantes_desc')} {len(missing_games)}:").pack(pady=10)
        
        textbox = ctk.CTkTextbox(dlg, width=480, height=280)
        textbox.pack(padx=10, pady=(0, 10))
        
        missing_list_str = "\n".join(missing_games)
        textbox.insert("1.0", missing_list_str)
        textbox.configure(state="disabled")
        
        def on_close():
            dlg.destroy()

        ctk.CTkButton(dlg, text=self.traducir("cerrar"), command=on_close).pack(pady=(0, 10))
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
        # Crear diálogo de progreso
        dlg = ctk.CTkToplevel(self)
        dlg.title(self.traducir("procesando_lista"))
        dlg.geometry("600x180")
        dlg.grab_set()
        dlg.transient(self)
        
        title_lbl = ctk.CTkLabel(dlg, text=self.traducir("procesando_lista"), font=ctk.CTkFont(size=14, weight="bold"))
        title_lbl.pack(pady=(12, 6))
        
        status_lbl = ctk.CTkLabel(dlg, text="", wraplength=560, justify="left")
        status_lbl.pack(padx=16, pady=(0, 6))
        
        pbar = ctk.CTkProgressBar(dlg)
        pbar.pack(fill="x", padx=16, pady=8)
        pbar.set(0)
        
        detail_lbl = ctk.CTkLabel(dlg, text="0%")
        detail_lbl.pack(pady=(0, 6))
        
        # Estado compartido para el progreso
        progress_state = {
            "current": 0,
            "total": 0,
            "current_game": "",
            "done": False,
            "error": None
        }
        
        def update_progress():
            if progress_state["done"]:
                dlg.destroy()
                return
            if progress_state["error"]:
                dlg.destroy()
                messagebox.showerror(self.traducir("error"), f"{self.traducir('error_busqueda')}\n{progress_state['error']}")
                return
            
            if progress_state["total"] > 0:
                frac = min(1.0, progress_state["current"] / progress_state["total"])
                pbar.set(frac)
                percent = int(frac * 100)
                current_text = progress_state.get("current_game", "")
                status_lbl.configure(text=f"{self.traducir('procesando')} {current_text}")
                detail_lbl.configure(text=f"{percent}% ({progress_state['current']}/{progress_state['total']})")
            dlg.after(100, update_progress)
        
        update_progress()
        
        def process_in_thread():
            try:
                # 0) Asegura que la DB esté cargada y las raíces indexadas
                progress_state["current_game"] = self.traducir("cargando")
                self.after(0, update_progress)
                
                if not get_items_by_key():
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
                            text=self.traducir("indexando_carpeta_actual"), text_color="orange"
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

                # OPTIMIZACIÓN: Pre-construir índices invertidos para búsquedas rápidas
                # Índice invertido: palabra -> lista de (nombre_normalizado, tid)
                word_to_tids: dict[str, set[tuple[str, str]]] = {}
                index_name = get_index_name()
                if index_name:
                    for nname, it in index_name:
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

                # Actualizar estado inicial
                progress_state["total"] = total_games
                progress_state["current"] = 0
                
                # 3) Resolver rutas para cada nombre (OPTIMIZADO)
                for i, name in enumerate(game_names):
                    # Actualizar progreso
                    progress_state["current"] = i + 1
                    progress_state["current_game"] = name[:50] + ("..." if len(name) > 50 else "")
                    self.after(0, update_progress)
                    
                    norm_n = norm_text(name)
                    name_words = [w for w in norm_n.split() if len(w) > 2]  # Solo palabras significativas
                    paths_found_for_name: set[str] = set()

                    # 3a) Match por nombre en índice de nombres -> TIDs (OPTIMIZADO con índice invertido)
                    if index_name and word_to_tids:
                        matching_tids = set()
                        # Si hay una sola palabra, buscar directamente
                        if len(name_words) == 1:
                            word = name_words[0]
                            if word in word_to_tids:
                                for nname, tid in word_to_tids[word]:
                                    if norm_n in nname or nname in norm_n:
                                        matching_tids.add(tid)
                        elif name_words:
                            # Múltiples palabras: buscar intersección de TIDs que contengan todas las palabras
                            candidate_tids = None
                            for word in name_words:
                                if word in word_to_tids:
                                    word_tids = {tid for _, tid in word_to_tids[word]}
                                    if candidate_tids is None:
                                        candidate_tids = word_tids
                                    else:
                                        candidate_tids &= word_tids  # Intersección
                            
                            if candidate_tids:
                                # Verificar que todas las palabras estén en el nombre del juego
                                for nname, it in index_name:
                                    tid = it["title_id"]
                                    if tid in candidate_tids:
                                        if all(word in nname for word in name_words):
                                            matching_tids.add(tid)
                        
                        for tid in matching_tids:
                            paths_found_for_name.update(self._find_paths_for_tid(tid))

                    # 3b) Match directo en índice por nombre de carpeta (OPTIMIZADO)
                    if self._paths_by_name:
                        # Búsqueda exacta primero (más rápida)
                        if norm_n in self._paths_by_name:
                            paths_found_for_name.update(self._paths_by_name[norm_n])
                        elif name_words:
                            # Búsqueda por palabras clave (solo si hay palabras)
                            for key_name, paths in self._paths_by_name.items():
                                # Verificar si todas las palabras están en el nombre de la carpeta
                                if all(word in key_name for word in name_words):
                                    paths_found_for_name.update(paths)
                    
                    # 3c) Búsqueda directa en la carpeta actual (OPTIMIZADO: usa cache)
                    if current_folder_items:
                        # Búsqueda exacta primero
                        if norm_n in current_folder_items:
                            paths_found_for_name.add(current_folder_items[norm_n])
                        elif name_words:
                            # Búsqueda por palabras clave
                            for item_norm, item_path in current_folder_items.items():
                                if all(word in item_norm for word in name_words):
                                    paths_found_for_name.add(item_path)

                    if paths_found_for_name:
                        # Agregar TODOS los paths encontrados (no solo el primero)
                        # Esto permite marcar múltiples ubicaciones del mismo juego
                        for path in paths_found_for_name:
                            path_norm = os.path.normpath(path)
                            found_paths.add(path_norm)
                        found_games.add(name)  # Rastrear que este juego fue encontrado
                    else:
                        missing_games.append(name)

                # 4) Actualizar UI en el hilo principal
                progress_state["done"] = True
                self.after(0, lambda: (
                    dlg.destroy(),
                    self._apply_game_list_results(found_paths, missing_games, total_games, len(found_games))
                ))
                
            except Exception as e:
                progress_state["done"] = True
                progress_state["error"] = str(e)
                self.after(0, lambda: (
                    dlg.destroy(),
                    messagebox.showerror(self.traducir("error"), f"Error al procesar la lista:\n{e}"),
                    self.status_label.configure(text=self.traducir("error"), text_color="red")
                ))
        
        # Ejecutar en hilo separado
        threading.Thread(target=process_in_thread, daemon=True).start()
    
    def _apply_game_list_results(self, found_paths: set[str], missing_games: list[str], total_games: int, found_games_count: int):
        """Aplica los resultados del procesamiento de la lista en el hilo principal"""
        try:
            # 4) Actualiza los checks - normalizar todos los paths y filtrar los que existen
            self._checked_paths.clear()
            
            # Diagnosticar diferencias
            paths_before_normalize = len(found_paths)
            normalized_paths = {os.path.normpath(p) for p in found_paths}
            paths_after_normalize = len(normalized_paths)
            existing_paths = {p for p in normalized_paths if os.path.exists(p)}
            actually_marked = len(existing_paths)
            
            # Si hay diferencias, mostrar información de diagnóstico
            paths_inexistentes = normalized_paths - existing_paths
            if paths_inexistentes and len(paths_inexistentes) <= 10:
                # Solo mostrar si hay pocos, para no saturar
                print(f"Paths que no existen ({len(paths_inexistentes)}):")
                for p in list(paths_inexistentes)[:10]:
                    print(f"  - {p}")
            
            self._checked_paths.update(existing_paths)

            # 🔄 refresca lo que esté en pantalla para mostrar los checks marcados
            current_folder = getattr(self, "current_folder", None)
            if current_folder and getattr(self, "_current_entries", None):
                # Refrescar la vista actual para mostrar los checks
                self._render_files(self._current_entries)
            self._update_counts()

            # 5) Navegar a la carpeta que contiene los archivos encontrados
            # Priorizar la carpeta actual si hay archivos encontrados ahí
            if existing_paths:
                # Contar cuántos paths marcados están en la carpeta actual
                paths_in_current_count = 0
                if current_folder:
                    current_norm = os.path.normpath(current_folder)
                    for path in existing_paths:
                        path_norm = os.path.normpath(path)
                        # Si el path está en la carpeta actual o es la carpeta actual
                        if path_norm == current_norm or path_norm.startswith(current_norm + os.sep):
                            paths_in_current_count += 1
                
                # Si hay muchos paths en la carpeta actual (más del 50%), solo refrescar la vista
                if paths_in_current_count > len(existing_paths) * 0.5 and current_folder:
                    # Refrescar la lista para que se muestren los checks marcados
                    self._list_folder(current_folder)
                # Si no hay suficientes paths en la carpeta actual Y el usuario NO cambió manualmente, navegar
                elif not self._user_changed_folder:
                    try:
                        from collections import Counter
                        # Obtener el directorio padre de cada path marcado
                        parents = [os.path.dirname(p.rstrip("\\/")) for p in existing_paths if os.path.exists(p)]
                        if parents:
                            # Encontrar el directorio padre más común (donde están más carpetas marcadas)
                            parent_counts = Counter(parents)
                            
                            # Buscar la mejor carpeta: la que contiene más elementos marcados
                            # Primero intentar con un umbral del 30%, pero si no hay, usar la que tenga más elementos
                            best_parent = None
                            best_count = 0
                            
                            # Buscar carpeta que tenga al menos el 30% de los elementos
                            for parent, count in parent_counts.most_common():
                                if count >= len(existing_paths) * 0.3 and os.path.isdir(parent):
                                    best_parent = parent
                                    best_count = count
                                    break
                            
                            # Si no hay una carpeta con el 30%, usar la que tenga más elementos
                            if not best_parent:
                                for parent, count in parent_counts.most_common():
                                    if os.path.isdir(parent):
                                        best_parent = parent
                                        best_count = count
                                        break
                            
                            # Si encontramos una buena carpeta, navegar ahí
                            if best_parent and best_count > 0:
                                self._user_changed_folder = False
                                self._enter_folder(best_parent)
                                self._user_changed_folder = False
                            else:
                                # Si no hay un directorio dominante, usar el path común
                                try:
                                    common = os.path.commonpath(list(existing_paths))
                                    if not os.path.isdir(common):
                                        common = os.path.dirname(common)
                                    if common and os.path.isdir(common):
                                        self._user_changed_folder = False
                                        self._enter_folder(common)
                                        self._user_changed_folder = False
                                    else:
                                        # Fallback: usar el primer scan_root que contenga algún path marcado
                                        scan_roots = getattr(self, "_scan_roots", [])
                                        for root in scan_roots:
                                            root_norm = os.path.normpath(root)
                                            # Verificar si algún path marcado está dentro de esta raíz
                                            if any(os.path.normpath(p).startswith(root_norm + os.sep) or os.path.normpath(p) == root_norm for p in existing_paths):
                                                self._user_changed_folder = False
                                                self._enter_folder(root)
                                                self._user_changed_folder = False
                                                break
                                except Exception:
                                    # Fallback: usar el primer scan_root
                                    if getattr(self, "_scan_roots", []):
                                        self._user_changed_folder = False
                                        self._enter_folder(self._scan_roots[0])
                                        self._user_changed_folder = False
                    except Exception as e:
                        print(f"Error navegando a carpeta: {e}")
                        # Fallback: refrescar la vista actual
                        if current_folder:
                            self._list_folder(current_folder)
                # Si el usuario cambió manualmente y no hay paths en la carpeta actual, solo refrescar
                elif current_folder:
                    self._list_folder(current_folder)

            # 6) Estado + faltantes
            # Información detallada sobre las diferencias
            info_adicional = ""
            if paths_before_normalize != paths_after_normalize:
                info_adicional += f" (duplicados eliminados: {paths_before_normalize - paths_after_normalize})"
            if paths_after_normalize != actually_marked:
                info_adicional += f" (no existen: {paths_after_normalize - actually_marked})"
            
            mensaje = self.traducir("procesados_juegos").format(
                total=total_games,
                encontrados=found_games_count,
                carpetas=len(found_paths),
                marcados=actually_marked
            ) + info_adicional
            
            self.status_label.configure(
                text=mensaje,
                text_color="green" if actually_marked > 0 else "orange"
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
