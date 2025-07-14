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
        "releases": "Releases",
        "ingresa_texto": "Ingresa Title ID o Nombre del juego:",
        "buscar": "Buscar",
        "error": "Error",
        "error_busqueda": "Ocurrió un error durante la búsqueda.",
        "col_title_id": "Title ID",
        "col_name": "Nombre",
        "col_system": "Consola",
        "col_regions": "Regiones",
        "copiar_celda": "Copiar celda",
        "copiar_fila": "Copiar fila"
    },
    "en": {
        "modo_oscuro": "Dark Mode",
        "idioma": "Language",
        "title_ids": "Title IDs",
        "releases": "Releases",
        "ingresa_texto": "Enter Title ID or Game Name:",
        "buscar": "Search",
        "error": "Error",
        "error_busqueda": "An error occurred during the search.",
        "col_title_id": "Title ID",
        "col_name": "Name",
        "col_system": "Console",
        "col_regions": "Regions",
        "copiar_celda": "Copy Cell",
        "copiar_fila": "Copy Row"
    },
    "pt": {
        "modo_oscuro": "Modo Escuro",
        "idioma": "Idioma",
        "title_ids": "Title IDs",
        "releases": "Lançamentos",
        "ingresa_texto": "Digite Title ID ou nome do jogo:",
        "buscar": "Buscar",
        "error": "Erro",
        "error_busqueda": "Ocorreu um erro durante a busca.",
        "col_title_id": "Title ID",
        "col_name": "Nome",
        "col_system": "Console",
        "col_regions": "Regiões",
        "copiar_celda": "Copiar célula",
        "copiar_fila": "Copiar linha"
    }
}

def traducir(clave):
    return traducciones[idioma_actual][clave]

def guardar_config():
    config = {
        "idioma": idioma_actual,
        "modo_oscuro": switch_var.get()
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f)

def cargar_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("idioma"), config.get("modo_oscuro")
        except Exception:
            return None, None
    return None, None

def detectar_idioma_sistema():
    lang, _ = locale.getdefaultlocale()
    if lang:
        if lang.startswith("es"):
            return "es"
        elif lang.startswith("pt"):
            return "pt"
        elif lang.startswith("en"):
            return "en"
    return "es"  # fallback

def detectar_modo_oscuro_linux():
    try:
        # Solo para GNOME, si está disponible
        res = subprocess.run(
            ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
            capture_output=True, text=True)
        if res.returncode == 0:
            modo = res.stdout.strip().strip("'")
            return modo == "prefer-dark"
    except Exception:
        pass
    return False

def detectar_modo_oscuro_windows():
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

def detectar_modo_oscuro_sistema():
    if sys.platform.startswith("win"):
        modo_oscuro = detectar_modo_oscuro_windows()
        if modo_oscuro is not None:
            return modo_oscuro
    elif sys.platform.startswith("linux"):
        return detectar_modo_oscuro_linux()
    return False

def aplicar_estilo_treeview(modo):
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

def toggle_mode():
    modo_oscuro = switch_var.get()
    ctk.set_appearance_mode("dark" if modo_oscuro else "light")
    aplicar_estilo_treeview("dark" if modo_oscuro else "light")
    guardar_config()

def copiar_fila(tree):
    selected = tree.focus()
    if selected:
        values = tree.item(selected, "values")
        texto = "\t".join(str(v) for v in values)
        app.clipboard_clear()
        app.clipboard_append(texto)
        app.update()

def copiar_celda(tree):
    if hasattr(tree, "_selected_column") and hasattr(tree, "_selected_row"):
        value = tree.set(tree._selected_row, tree._selected_column)
        app.clipboard_clear()
        app.clipboard_append(value)
        app.update()

def crear_menu_contextual(tree):
    menu = Menu(tree, tearoff=0)
    menu.add_command(label=traducir("copiar_celda"), command=lambda: copiar_celda(tree))
    menu.add_command(label=traducir("copiar_fila"), command=lambda: copiar_fila(tree))
    return menu

def mostrar_menu_contextual(event, tree, menu):
    row = tree.identify_row(event.y)
    column = tree.identify_column(event.x)
    if row:
        tree.selection_set(row)
        tree.focus(row)
        tree._selected_row = row
        col_index = int(column[1:]) - 1
        if 0 <= col_index < len(tree["columns"]):
            tree._selected_column = tree["columns"][col_index]
        menu.tk_popup(event.x_root, event.y_root)

def copiar_ctrl_c(event, tree):
    if hasattr(tree, "_selected_column") and hasattr(tree, "_selected_row"):
        copiar_celda(tree)
    else:
        copiar_fila(tree)

def buscar_todo(event=None):
    query = entry.get().strip()
    if not query:
        messagebox.showerror(traducir("error"), traducir("ingresa_texto"))
        return

    for item in tree_title_ids.get_children():
        tree_title_ids.delete(item)
    for item in tree_releases.get_children():
        tree_releases.delete(item)

    try:
        # Title IDs
        title_id_items = []
        if re.fullmatch(r"[A-Fa-f0-9]{8}", query):
            res = requests.get(f"{URL_TITLE_IDS}/{query}")
            res.raise_for_status()
            item = res.json()
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
            tree_title_ids.insert("", "end", values=(item["title_id"], item["name"], item["system"]))

        # Releases
        res = requests.get(URL_RELEASES, params={"name": query, "limit": 30})
        res.raise_for_status()
        for item in res.json().get("items", []):
            tree_releases.insert("", "end", values=(
                item.get("name", "N/A"),
                ", ".join(item.get("regions", [])),
                item.get("fallback_system", "N/A")
            ))

    except requests.RequestException as e:
        messagebox.showerror(traducir("error"), f"{traducir('error_busqueda')}\n{e}")

# --- Inicio de app ---

idioma_cfg, modo_cfg = cargar_config()

idioma_sistema = detectar_idioma_sistema()
modo_sistema = detectar_modo_oscuro_sistema()

idioma_actual = idioma_cfg if idioma_cfg in traducciones else idioma_sistema
modo_oscuro_inicial = modo_cfg if modo_cfg is not None else modo_sistema

app = ctk.CTk()
app.title("Consulta Juegos Xbox - By: elerickmj")
app.geometry("980x720")

aplicar_estilo_treeview("dark" if modo_oscuro_inicial else "light")
ctk.set_appearance_mode("dark" if modo_oscuro_inicial else "light")

frame_top = ctk.CTkFrame(app)
frame_top.pack(fill="x", padx=10, pady=5)

switch_var = ctk.BooleanVar(value=modo_oscuro_inicial)
switch = ctk.CTkSwitch(frame_top, text=traducir("modo_oscuro"), variable=switch_var, command=toggle_mode)
switch.pack(side="left", padx=10)

idioma_menu_label = ctk.CTkLabel(frame_top, text=f"🌐 {traducir('idioma')}:")
idioma_menu_label.pack(side="right", padx=(5, 0))

selector_idioma = ctk.CTkOptionMenu(frame_top, values=["Español", "English", "Português"],
                                    command=lambda val: cambiar_idioma({'Español': 'es', 'English': 'en', 'Português': 'pt'}[val]))
selector_idioma.pack(side="right")
selector_idioma.set({"es": "Español", "en": "English", "pt": "Português"}.get(idioma_actual, "Español"))

label_entrada = ctk.CTkLabel(app, text=traducir("ingresa_texto"))
label_entrada.pack(pady=10)

entry = ctk.CTkEntry(app, placeholder_text="Ej: 4D530AA4 o Forza Horizon", width=600)
entry.pack(pady=5)
entry.bind("<Return>", buscar_todo)

boton_buscar = ctk.CTkButton(app, text=traducir("buscar"), command=buscar_todo)
boton_buscar.pack(pady=10)

frame_title = ctk.CTkFrame(app)
frame_title.pack(fill="both", expand=True, padx=10, pady=(0,10))
label_title = ctk.CTkLabel(frame_title, text=traducir("title_ids"))
label_title.pack(anchor="w")

columns_title = ("title_id", "name", "system")
tree_title_ids = ttk.Treeview(frame_title, columns=columns_title, show="headings", height=8)
for col in columns_title:
    tree_title_ids.heading(col, text=traducir("col_" + col))
    tree_title_ids.column(col, width=200 if col == "name" else 120)
tree_title_ids.pack(fill="both", expand=True)

menu_title = crear_menu_contextual(tree_title_ids)
tree_title_ids.bind("<Button-3>", lambda e: mostrar_menu_contextual(e, tree_title_ids, menu_title))
tree_title_ids.bind("<Control-c>", lambda e: copiar_ctrl_c(e, tree_title_ids))

frame_release = ctk.CTkFrame(app)
frame_release.pack(fill="both", expand=True, padx=10, pady=(0,20))
label_releases = ctk.CTkLabel(frame_release, text=traducir("releases"))
label_releases.pack(anchor="w")

columns_release = ("name", "regions", "system")
tree_releases = ttk.Treeview(frame_release, columns=columns_release, show="headings", height=10)
for col in columns_release:
    tree_releases.heading(col, text=traducir("col_" + col))
    tree_releases.column(col, width=300 if col == "name" else 150)
tree_releases.pack(fill="both", expand=True)

menu_release = crear_menu_contextual(tree_releases)
tree_releases.bind("<Button-3>", lambda e: mostrar_menu_contextual(e, tree_releases, menu_release))
tree_releases.bind("<Control-c>", lambda e: copiar_ctrl_c(e, tree_releases))

app.mainloop()
