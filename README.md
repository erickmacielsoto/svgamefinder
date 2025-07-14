🎮 Consulta Juegos Xbox 360 - By: elerickmj

Aplicación de escritorio para Windows creada con Python y `customtkinter` que permite buscar información sobre juegos de Xbox 360 mediante Title ID o nombre del juego. Consulta datos desde la API pública de [dbox.tools](https://dbox.tools).

📌 Características

- 🔍 Búsqueda automática por **Title ID** (8 caracteres hexadecimales) o por **nombre del juego**.
- 📋 Muestra información detallada:
  - Nombre del juego
  - Title ID
  - Plataforma / Sistema
  - Fecha de lanzamiento
  - Regiones y cantidad de discos disponibles
- 🌙 Interfaz moderna con soporte para tema claro u oscuro.
- ⚙️ Construido con `customtkinter`, una versión moderna de `tkinter`.


🚀 Cómo ejecutar la aplicación

1. Clona el repositorio
bash
git clone https://github.com/tu-usuario/consulta-juegos-xbox360.git
cd consulta-juegos-xbox360

2. Instala las dependencias
Usa un entorno virtual si lo prefieres, y luego ejecuta:
bash
Copiar
Editar
pip install -r requirements.txt

3. Ejecuta la app
bash
Copiar
Editar
python app.py

🖥️ Crear ejecutable para Windows (.exe)
Opcional: si quieres generar un archivo ejecutable con PyInstaller:
bash
Copiar
Editar
pip install pyinstaller
pyinstaller --noconsole --onefile --icon=icon.ico app.py
Reemplaza icon.ico por tu propio ícono si tienes uno.
El archivo final se generará en la carpeta dist/.

📡 API utilizada
Esta aplicación usa la API pública de dbox.tools:

GET /api/title_ids/{title_id} — Buscar por Title ID

GET /api/games?search=nombre — Buscar juegos por nombre

GET /api/releases?name=nombre&limit=20 — Buscar lanzamientos

📁 Estructura de archivos
bash
Copiar
Editar
consulta-juegos-xbox360/
│
├── app.py                # Código principal de la aplicación
├── requirements.txt      # Dependencias del proyecto
├── README.md             # Este archivo
├── LICENSE               # Licencia MIT
└── icon.ico              # Ícono opcional para el ejecutable

🧾 Licencia
Este proyecto está bajo la licencia MIT.
Puedes usar, modificar y compartir el código libremente, incluso en proyectos comerciales.
Consulta el archivo LICENSE para más detalles.

👨‍💻 Autor
Erick Maciel
TikTok: @elerickmj
