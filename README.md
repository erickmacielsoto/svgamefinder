🎮 Consulta Juegos Xbox - By: elerickmj
Aplicación de escritorio multiplataforma (Windows, Linux) creada con Python y customtkinter que permite buscar información sobre juegos de Xbox mediante Title ID o nombre del juego. Consulta datos desde la API pública de dbox.tools.

🌟 Características
🔍 Búsqueda Flexible: Permite buscar automáticamente por Title ID (8 caracteres hexadecimales) o por nombre del juego.

📋 Información Detallada: Muestra datos relevantes como el nombre del juego, Title ID, sistema (Xbox 360, Original, etc.), regiones de lanzamiento y más.

🌙 Tema Personalizable: Interfaz moderna con soporte para tema claro u oscuro, con detección automática del tema del sistema operativo.

🌐 Soporte Multi-idioma: Interfaz traducida al español, inglés y portugués, con detección automática del idioma del sistema.

✨ Experiencia de Usuario Mejorada: Indicadores visuales de carga durante las búsquedas y menús contextuales para copiar fácilmente celdas o filas completas.

⚙️ Construcción Robusta: Desarrollado con customtkinter, una versión moderna y estética de tkinter, asegurando una interfaz de usuario atractiva y funcional.

🚀 Cómo Empezar
Requisitos
Python 3.x

En sistemas Linux (Debian/Ubuntu), asegúrate de tener python3-tk instalado para el correcto funcionamiento de tkinter:

Bash

sudo apt update
sudo apt install python3-tk
Instalación y Ejecución
Clona el repositorio:

Bash

git clone https://github.com/erickmacielsoto/consulta-juegos-xbox.git
cd consulta-juegos-xbox
Crea y activa un entorno virtual (recomendado):

Bash

python3 -m venv venv
source venv/bin/activate  # En Linux/macOS
# .\venv\Scripts\activate  # En Windows (CMD)
# .\venv\Scripts\Activate.ps1 # En Windows (PowerShell)
Instala las dependencias:
Con tu entorno virtual activado, instala las bibliotecas necesarias:

Bash

pip install -r requirements.txt
Ejecuta la aplicación:

Bash

python consulta_juegos_xbox.py

📦 Crear un Ejecutable (Standalone)
Puedes empaquetar la aplicación en un solo archivo ejecutable para Windows o Linux, lo que permite ejecutarla sin necesidad de tener Python instalado o de usar la terminal.

Instala PyInstaller (dentro de tu entorno virtual activado):

Bash

pip install pyinstaller
Genera el ejecutable:
Asegúrate de estar en el directorio raíz del proyecto (consulta-juegos-xbox).

Para Windows (.exe):
pyinstaller --noconfirm --onefile --windowed --name "ConsultaXboxJuegos" --icon=icon.ico consulta_juegos_xbox.py

Para Linux (ejecutable):
pyinstaller --noconfirm --onefile --windowed --name "ConsultaXboxJuegos" consulta_juegos_xbox.py
(En Linux, la opción --icon para el ejecutable directo a veces no es tan efectiva o requiere pasos adicionales de integración con el escritorio. El icono se usará si lo empaquetas en un instalador o paquete .deb/.rpm).

El archivo ejecutable final se generará en la carpeta dist/.

📡 API Utilizada
Esta aplicación consume la API pública de dbox.tools para obtener los datos de los juegos:

GET /api/title_ids/{title_id} — Buscar por Title ID específico.

GET /api/title_ids?name={nombre}&limit={limite} — Buscar Title IDs por nombre.

GET /api/releases?name={nombre}&limit={limite} — Buscar lanzamientos por nombre.

📁 Estructura de Archivos
consulta-juegos-xbox/
│
├── consulta_juegos_xbox.py   # Código principal de la aplicación
├── requirements.txt          # Dependencias del proyecto
├── README.md                 # Este archivo
├── LICENSE                   # Licencia MIT
└── icon.ico                  # Ícono opcional para el ejecutable (para Windows)

📜 Licencia
Este proyecto está bajo la licencia MIT.
Puedes usar, modificar y compartir el código libremente, incluso en proyectos comerciales. Consulta el archivo LICENSE para más detalles.

🤝 Contribuciones
¡Las contribuciones son bienvenidas! Si encuentras un error o tienes una idea para una mejora, no dudes en abrir un issue o enviar un pull request.

👨‍💻 Autor
Erick Maciel

GitHub: @erickmacielsoto
TikTok: @elerickmj

Probado por
Jason Torres
GitHub: @jasontorresb