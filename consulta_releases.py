import customtkinter as ctk
from tkinter import messagebox
import requests
import re

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

URL_TITLE_ID = "https://dbox.tools/api/title_ids"
URL_GAMES = "https://dbox.tools/api/games"
URL_RELEASES = "https://dbox.tools/api/releases"

def buscar_todo(event=None):
    query = entry.get().strip()
    if not query:
        messagebox.showerror("Error", "Ingresa un Title ID o nombre de juego.")
        return

    text_result.configure(state="normal")
    text_result.delete("1.0", "end")

    if re.fullmatch(r"[A-Fa-f0-9]{8}", query):
        # Es Title ID
        text_result.insert("end", f"🔍 Buscando por Title ID: {query}\n")
        res = requests.get(f"{URL_TITLE_ID}/{query}")
        if res.status_code == 200:
            item = res.json()
            text_result.insert("end", format_title_id(item))
        else:
            text_result.insert("end", f"No se encontró Title ID: {query}\n")
    else:
        # Es texto
        text_result.insert("end", f"🔍 Buscando por Nombre: {query}\n")
        res = requests.get(f"{URL_GAMES}?search={query}")
        if res.status_code == 200:
            data = res.json()
            if data.get("items"):
                for i, item in enumerate(data["items"], 1):
                    text_result.insert("end", f"\n# Game {i}\n{format_game(item)}\n")
            else:
                text_result.insert("end", "No se encontraron juegos.\n")

        text_result.insert("end", "\n" + "="*50 + "\n")
        text_result.insert("end", f"🔍 Buscando Releases: {query}\n")
        res2 = requests.get(URL_RELEASES, params={"name": query, "limit": 20})
        if res2.status_code == 200:
            data = res2.json()
            if data.get("items"):
                for i, item in enumerate(data["items"], 1):
                    text_result.insert("end", f"\n# Release {i}\n{format_release(item)}\n")
            else:
                text_result.insert("end", "No se encontraron releases.\n")

    text_result.configure(state="disabled")

def format_title_id(item):
    s = f"🎮 Nombre: {item.get('name')}\n"
    s += f"🔑 Title ID: {item.get('title_id')}\n"
    s += f"💿 Sistemas: {item.get('systems')}\n"
    s += f"🆔 Bing ID: {item.get('bing_id')}\n"
    return s

def format_game(item):
    s = f"🎮 Nombre: {item.get('name')}\n"
    s += f"🔑 ID: {item.get('id')}\n"
    s += f"💿 Sistema: {item.get('system')}\n"
    s += f"📆 Lanzamiento: {item.get('release_date')}\n"
    return s

def format_release(item):
    s = f"🎮 Nombre: {item.get('name')}\n"
    s += f"🌎 Regiones: {item.get('regions')}\n"
    s += f"📦 Barcode: {item.get('barcode')}\n"
    s += f"💿 Sistema: {item.get('fallback_system')}\n"
    s += f"💿 Discos: {item.get('discs')}\n"
    return s

# GUI principal
app = ctk.CTk()
app.title("Consulta Juegos - Xbox 360 - By: elerickmj")
app.geometry("900x700")

label = ctk.CTkLabel(app, text="Ingresa Title ID o Nombre del juego:")
label.pack(pady=10)

entry = ctk.CTkEntry(app, placeholder_text="Ej: 4E4D0846 o Red Dead Redemption", width=500)
entry.pack(pady=5)
entry.bind("<Return>", buscar_todo)  # Búsqueda con ENTER

btn_buscar = ctk.CTkButton(app, text="🔍 Buscar Automático", command=buscar_todo)
btn_buscar.pack(pady=10)

text_result = ctk.CTkTextbox(app, width=850, height=500, wrap="word")
text_result.pack(pady=20)
text_result.configure(state="disabled")

app.mainloop()
