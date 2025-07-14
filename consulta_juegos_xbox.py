import customtkinter as ctk
from tkinter import ttk, messagebox, Menu
import requests
import re
import locale
import json
import os
import sys
import subprocess
from pathlib import Path
# import requests_cache # Descomentar para usar caché

# Guardar configuración en carpeta usuario para evitar permisos
CONFIG_FILE = Path.home() / ".consulta_juegos_xbox_config.json"

ctk.set_default_color_theme("blue")

URL_TITLE_IDS = "https://dbox.tools/api/title_ids"
URL_RELEASES = "https://dbox.tools/api/releases"

traducciones = {
    "es": {
        "modo_oscuro": "Modo Oscuro",
        "idioma": "Idioma",
        "title_ids": "Title IDs",
        "releases": "Lanzamientos",
        "ingresa_texto": "Ingresa Title ID o Nombre del juego:",
        "buscar": "Buscar",
        "error": "Error",
        "info": "Información",
        "error_busqueda": "Ocurrió un error durante la búsqueda.",
        "no_results_found": "No se encontraron resultados para la búsqueda.",
        "col_title_id": "Title ID",
        "col_name": "Nombre",
        "col_system": "Consola",
        "col_regions": "Regiones",
        "copiar_celda": "Copiar celda",
        "copiar_fila": "Copiar fila",
        "cargando": "Cargando...",
        "busqueda_completada": "Búsqueda completada."
    },
    "en": {
        "modo_oscuro": "Dark Mode",
        "idioma": "Language",
        "title_ids": "Title IDs",
        "releases": "Releases",
        "ingresa_texto": "Enter Title ID or Game Name:",
        "buscar": "Search",
        "error": "Error",
        "info": "Info",
        "error_busqueda": "An error occurred during the search.",
        "no_results_found": "No results found for the search.",
        "col_title_id": "Title ID",
        "col_name": "Name",
        "col_system": "Console",
        "col_regions": "Regions",
        "copiar_celda": "Copy Cell",
        "copiar_fila": "Copy Row",
        "cargando": "Loading...",
        "busqueda_completada": "Search completed."
    },
    "pt": {
        "modo_oscuro": "Modo Escuro",
        "idioma": "Idioma",
        "title_ids": "Title IDs",
        "releases": "Lançamentos",
        "ingresa_texto": "Digite Title ID ou nome do jogo:",
        "buscar": "Buscar",
        "error": "Erro",
        "info": "Informação",
        "error_busqueda": "Ocorreu um erro durante a busca.",
        "no_results_found": "Não foram encontrados resultados para a pesquisa.",
        "col_title_id": "Title ID",
        "col_name": "Nome",
        "col_system": "Console",
        "col_regions": "Regiões",
        "copiar_celda": "Copiar célula",
        "copiar_fila": "Copiar linha",
        "cargando": "Carregando...",
        "busqueda_completada": "Pesquisa concluída."
    }
}

class XboxGameLookupApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        icon_path = os.path.abspath("icon.ico")
        if not os.path.exists(icon_path):
            print(f"¡No se encontró el icono en {icon_path}!")
        else:
            self.iconbitmap(icon_path)

        self.title("SVXboxGamesFinder - By: @erickmacielsoto - Reviewed by: @jasontorresb")
        self.geometry("980x720")
        # self.resizable(False, False) # Opcional: para evitar que la ventana se pueda redimensionar

        # Descomentar para habilitar el caché de solicitudes
        # requests_cache.install_cache('xbox_api_cache', expire_after=3600)

        self.idioma_actual = self._detectar_idioma_sistema()
        self.modo_oscuro_inicial = self._detectar_modo_oscuro_sistema()

        self._cargar_config() # Cargar config y sobrescribir valores iniciales si existen

        self._aplicar_estilo_treeview("dark" if self.modo_oscuro_inicial else "light")
        ctk.set_appearance_mode("dark" if self.modo_oscuro_inicial else "light")

        self._setup_ui()
        self._update_ui_texts() # Actualización inicial del texto de la UI

    def traducir(self, clave):
        return traducciones[self.idioma_actual].get(clave, f"MISSING_TRANSLATION_{clave}")

    def _guardar_config(self):
        config = {
            "idioma": self.idioma_actual,
            "modo_oscuro": self.switch_var.get()
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
                    loaded_idioma = config.get("idioma")
                    loaded_modo_oscuro = config.get("modo_oscuro")

                    if loaded_idioma in traducciones:
                        self.idioma_actual = loaded_idioma
                    if loaded_modo_oscuro is not None:
                        self.modo_oscuro_inicial = loaded_modo_oscuro
            except Exception as e:
                messagebox.showwarning(self.traducir("info"), f"Error al cargar configuración, usando valores predeterminados: {e}")

    def _detectar_idioma_sistema(self):
        lang, _ = locale.getdefaultlocale()
        if lang:
            if lang.startswith("es"):
                return "es"
            elif lang.startswith("pt"):
                return "pt"
            elif lang.startswith("en"):
                return "en"
        return "es"  # fallback

    def _detectar_modo_oscuro_linux(self):
        try:
            res = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                capture_output=True, text=True)
            if res.returncode == 0:
                modo = res.stdout.strip().strip("'")
                return modo == "prefer-dark"
        except Exception:
            pass
        return False

    def _detectar_modo_oscuro_windows(self):
        try:
            import winreg
        except ImportError:
            return None
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0  # 0 = oscuro, 1 = claro
        except Exception:
            return None

    def _detectar_modo_oscuro_sistema(self):
        if sys.platform.startswith("win"):
            modo_oscuro = self._detectar_modo_oscuro_windows()
            if modo_oscuro is not None:
                return modo_oscuro
        elif sys.platform.startswith("linux"):
            return self._detectar_modo_oscuro_linux()
        return False

    def _aplicar_estilo_treeview(self, modo):
        style = ttk.Style()
        font_name = 'Segoe UI' if sys.platform.startswith('win') else 'Ubuntu'
        if modo == "dark":
            style.theme_use('clam')
            style.configure("Treeview",
                            background="#2b2b2b",
                            foreground="white",
                            fieldbackground="#2b2b2b",
                            font=(font_name, 10))
            style.map("Treeview",
                      background=[('selected', '#0a64a4')],
                      foreground=[('selected', 'white')])
            style.configure("Treeview.Heading",
                            background="#3c3f41",
                            foreground="white",
                            font=(font_name, 11, 'bold'))
        else:
            style.theme_use('default')
            style.configure("Treeview",
                            background="white",
                            foreground="black",
                            fieldbackground="white",
                            font=(font_name, 10))
            style.map("Treeview",
                      background=[('selected', '#3399FF')],
                      foreground=[('selected', 'white')])
            style.configure("Treeview.Heading",
                            background="#f0f0f0",
                            foreground="black",
                            font=(font_name, 11, 'bold'))

    def _toggle_mode(self):
        modo_oscuro = self.switch_var.get()
        ctk.set_appearance_mode("dark" if modo_oscuro else "light")
        self._aplicar_estilo_treeview("dark" if modo_oscuro else "light")
        self._guardar_config()

    def _copiar_fila(self, tree):
        selected = tree.focus()
        if selected:
            values = tree.item(selected, "values")
            texto = "\t".join(str(v) for v in values)
            self.clipboard_clear()
            self.clipboard_append(texto)
            self.update()

    def _copiar_celda(self, tree):
        if hasattr(tree, "_selected_column") and hasattr(tree, "_selected_row"):
            value = tree.set(tree._selected_row, tree._selected_column)
            self.clipboard_clear()
            self.clipboard_append(value)
            self.update()

    def _crear_menu_contextual(self, tree):
        menu = Menu(tree, tearoff=0)
        menu.add_command(label=self.traducir("copiar_celda"), command=lambda: self._copiar_celda(tree))
        menu.add_command(label=self.traducir("copiar_fila"), command=lambda: self._copiar_fila(tree))
        return menu

    def _mostrar_menu_contextual(self, event, tree, menu):
        row = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        if row:
            tree.selection_set(row)
            tree.focus(row)
            tree._selected_row = row
            if column and column.startswith('#'): # Asegurarse de que column no esté vacío y tenga el formato esperado
                col_index = int(column[1:]) - 1
                if 0 <= col_index < len(tree["columns"]):
                    tree._selected_column = tree["columns"][col_index]
            menu.tk_popup(event.x_root, event.y_root)

    def _copiar_ctrl_c(self, event, tree):
        if hasattr(tree, "_selected_column") and hasattr(tree, "_selected_row"):
            self._copiar_celda(tree)
        else:
            self._copiar_fila(tree)

    def _update_ui_texts(self):
        self.label_entrada.configure(text=self.traducir("ingresa_texto"))
        self.boton_buscar.configure(text=self.traducir("buscar"))
        self.switch.configure(text=self.traducir("modo_oscuro"))
        self.idioma_menu_label.configure(text=f"🌐 {self.traducir('idioma')}:")

        # Actualizar encabezados de Treeview
        self.tree_title_ids.heading("title_id", text=self.traducir("col_title_id"))
        self.tree_title_ids.heading("name", text=self.traducir("col_name"))
        self.tree_title_ids.heading("system", text=self.traducir("col_system"))
        
        self.tree_releases.heading("name", text=self.traducir("col_name"))
        self.tree_releases.heading("regions", text=self.traducir("col_regions"))
        self.tree_releases.heading("system", text=self.traducir("col_system"))

        # Recrear los menús contextuales para que sus etiquetas se actualicen
        # Asegurarse de que los treeviews ya existan antes de intentar crear menús para ellos
        if hasattr(self, 'tree_title_ids'):
            self.menu_title = self._crear_menu_contextual(self.tree_title_ids)
            # Re-vincular el menú contextual ya que se ha recreado
            self.tree_title_ids.bind("<Button-3>", lambda e: self._mostrar_menu_contextual(e, self.tree_title_ids, self.menu_title))

        if hasattr(self, 'tree_releases'):
            self.menu_release = self._crear_menu_contextual(self.tree_releases)
            # Re-vincular el menú contextual
            self.tree_releases.bind("<Button-3>", lambda e: self._mostrar_menu_contextual(e, self.tree_releases, self.menu_release))

        # Actualizar el texto del label de estado si no es un mensaje transitorio
        current_status_text = self.status_label.cget("text")
        if current_status_text not in [self.traducir("cargando"), self.traducir("busqueda_completada"), self.traducir("no_results_found"), self.traducir("error_busqueda")]:
             self.status_label.configure(text="") # Limpiar si no es un estado transitorio

    def _cambiar_idioma(self, val):
        self.idioma_actual = {'Español': 'es', 'English': 'en', 'Português': 'pt'}[val]
        self.selector_idioma.set(val)
        self._guardar_config()
        self._update_ui_texts() # Llamar a la función para actualizar todos los textos

    def _buscar_todo(self, event=None):
        query = self.entry.get().strip()
        if not query:
            messagebox.showerror(self.traducir("error"), self.traducir("ingresa_texto"))
            return

        # Limpiar resultados anteriores
        for item in self.tree_title_ids.get_children():
            self.tree_title_ids.delete(item)
        for item in self.tree_releases.get_children():
            self.tree_releases.delete(item)

        # Deshabilitar controles y mostrar mensaje de carga
        self.boton_buscar.configure(state="disabled")
        self.entry.configure(state="disabled")
        self.status_label.configure(text=self.traducir("cargando"), text_color="orange")
        self.update_idletasks() # Forzar actualización de la UI para que se vea el mensaje

        try:
            # Title IDs
            title_id_items = []
            if re.fullmatch(r"[A-Fa-f0-9]{8}", query):
                res = requests.get(f"{URL_TITLE_IDS}/{query}")
                res.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
                item = res.json()
                # Verifica si el item tiene datos, la API para un solo ID retorna {} si no encuentra
                if item: 
                    title_id_items.append({
                        "title_id": item.get("title_id", "N/A"),
                        "name": item.get("name", "N/A"),
                        "system": ", ".join(item.get("systems", [])) if isinstance(item.get("systems"), list) else item.get("systems", "N/A"),
                    })
            else:
                res = requests.get(URL_TITLE_IDS, params={"name": query, "limit": 20})
                res.raise_for_status()
                for item in res.json().get("items", []):
                    title_id_items.append({
                        "title_id": item.get("title_id", "N/A"),
                        "name": item.get("name", "N/A"),
                        "system": ", ".join(item.get("systems", [])) if isinstance(item.get("systems"), list) else item.get("systems", "N/A"),
                    })

            for item in title_id_items:
                self.tree_title_ids.insert("", "end", values=(item["title_id"], item["name"], item["system"]))

            # Releases
            res = requests.get(URL_RELEASES, params={"name": query, "limit": 30})
            res.raise_for_status()
            for item in res.json().get("items", []):
                self.tree_releases.insert("", "end", values=(
                    item.get("name", "N/A"),
                    ", ".join(item.get("regions", [])),
                    item.get("fallback_system", "N/A")
                ))
            
            # Si no se encontraron resultados en ninguna tabla
            if not title_id_items and not self.tree_releases.get_children():
                self.status_label.configure(text=self.traducir("no_results_found"), text_color="orange")
            else:
                self.status_label.configure(text=self.traducir("busqueda_completada"), text_color="green")

        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 404:
                # 404 para búsquedas por nombre generalmente significa que no hay coincidencias
                self.status_label.configure(text=self.traducir("no_results_found"), text_color="orange")
            else:
                messagebox.showerror(self.traducir("error"), f"{self.traducir('error_busqueda')}\nHTTP Error: {http_err.response.status_code} - {http_err.response.reason}")
                self.status_label.configure(text=self.traducir("error_busqueda"), text_color="red")
        except requests.RequestException as e:
            messagebox.showerror(self.traducir("error"), f"{self.traducir('error_busqueda')}\n{e}")
            self.status_label.configure(text=self.traducir("error_busqueda"), text_color="red")
        finally:
            # Re-habilitar controles
            self.boton_buscar.configure(state="normal")
            self.entry.configure(state="normal")


    def _setup_ui(self):
        # Frame superior para configuración
        frame_top = ctk.CTkFrame(self)
        frame_top.pack(fill="x", padx=10, pady=5)

        self.switch_var = ctk.BooleanVar(value=self.modo_oscuro_inicial)
        self.switch = ctk.CTkSwitch(frame_top, text=self.traducir("modo_oscuro"), variable=self.switch_var, command=self._toggle_mode)
        self.switch.pack(side="left", padx=10)

        self.selector_idioma = ctk.CTkOptionMenu(frame_top, values=["Español", "English", "Português"],
                                                command=self._cambiar_idioma)
        self.selector_idioma.pack(side="right") 

        self.idioma_menu_label = ctk.CTkLabel(frame_top, text=f"🌐 {self.traducir('idioma')}:")
        self.idioma_menu_label.pack(side="right", padx=(5, 0))

        self.selector_idioma.set({"es": "Español", "en": "English", "pt": "Português"}.get(self.idioma_actual, "Español"))

        self.label_entrada = ctk.CTkLabel(self, text=self.traducir("ingresa_texto"))
        self.label_entrada.pack(pady=10)

        self.entry = ctk.CTkEntry(self, placeholder_text="Ej: 4D530AA4 o Forza Horizon", width=600)
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", self._buscar_todo)

        self.boton_buscar = ctk.CTkButton(self, text=self.traducir("buscar"), command=self._buscar_todo)
        self.boton_buscar.pack(pady=10)

        # Etiqueta de estado para mensajes de carga/error
        self.status_label = ctk.CTkLabel(self, text="", fg_color="transparent")
        self.status_label.pack(pady=5)

        # Frame y Treeview para Title IDs
        self.frame_title = ctk.CTkFrame(self)
        self.frame_title.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.label_title = ctk.CTkLabel(self.frame_title, text=self.traducir("title_ids"))
        self.label_title.pack(anchor="w")

        columns_title = ("title_id", "name", "system")
        self.tree_title_ids = ttk.Treeview(self.frame_title, columns=columns_title, show="headings", height=8)
        for col in columns_title:
            self.tree_title_ids.heading(col, text=self.traducir("col_" + col))
            # Ajustar anchos y permitir estiramiento
            if col == "name":
                self.tree_title_ids.column(col, width=200, stretch=True)
            else:
                self.tree_title_ids.column(col, width=120, stretch=True) 
        self.tree_title_ids.pack(fill="both", expand=True)

        # Los menús se crearán/recrearán en _update_ui_texts
        self.tree_title_ids.bind("<Control-c>", lambda e: self._copiar_ctrl_c(e, self.tree_title_ids))

        # Frame y Treeview para Releases
        self.frame_release = ctk.CTkFrame(self)
        self.frame_release.pack(fill="both", expand=True, padx=10, pady=(0,20))
        self.label_releases = ctk.CTkLabel(self.frame_release, text=self.traducir("releases"))
        self.label_releases.pack(anchor="w")

        columns_release = ("name", "regions", "system")
        self.tree_releases = ttk.Treeview(self.frame_release, columns=columns_release, show="headings", height=10)
        for col in columns_release:
            self.tree_releases.heading(col, text=self.traducir("col_" + col))
            # Ajustar anchos y permitir estiramiento
            if col == "name":
                self.tree_releases.column(col, width=300, stretch=True)
            else:
                self.tree_releases.column(col, width=150, stretch=True)
        self.tree_releases.pack(fill="both", expand=True)

        # Los menús se crearán/recrearán en _update_ui_texts
        self.tree_releases.bind("<Control-c>", lambda e: self._copiar_ctrl_c(e, self.tree_releases))

if __name__ == "__main__":
    app = XboxGameLookupApp()
    app.mainloop()