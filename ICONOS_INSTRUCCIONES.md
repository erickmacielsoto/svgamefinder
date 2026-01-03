# Instrucciones para Agregar Iconos

## Formato de los Iconos

Los iconos deben cumplir con los siguientes requisitos:

1. **Formato**: PNG (recomendado) o ICO
2. **Tamaño**: 20x20 píxeles (se redimensionarán automáticamente si son más grandes)
3. **Fondo**: Transparente (PNG con canal alpha)
4. **Resolución**: Mínimo 20x20, recomendado 32x32 o 64x64 para mejor calidad

## Ubicación de los Archivos

Crea una carpeta llamada `icons` en la raíz del proyecto (al mismo nivel que `consulta_juegos_xbox.py`).

```
svgamefinder/
├── consulta_juegos_xbox.py
├── icons/              ← Crea esta carpeta
│   ├── trash.png
│   ├── clipboard.png
│   ├── folder.png
│   └── ...
```

## Nombres de Archivos Requeridos

Los iconos deben tener exactamente estos nombres:

### Botones Superiores:
- `trash.png` - Limpiar lista
- `clipboard.png` - Pegar lista
- `folder.png` - Cargar lista
- `clean.png` - Limpiar .json
- `download.png` - Cargar .json
- `add_folder.png` - Agregar carpeta

### Botones del Explorador:
- `back.png` - Atrás
- `forward.png` - Adelante
- `up.png` - Subir nivel
- `open.png` - Abrir en Explorer
- `refresh.png` - Cambiar carpeta
- `select_all.png` - Seleccionar todo
- `check.png` - Marcar visibles
- `uncheck.png` - Desmarcar visibles
- `copy.png` - Copiar selección
- `copy_marked.png` - Copiar marcados
- `clear.png` - Limpiar selección
- `search.png` - Buscar
- `clear_filter.png` - Limpiar filtro

## Descarga desde Flaticon

1. Ve a [Flaticon.com](https://www.flaticon.com)
2. Busca el icono que necesitas (ej: "trash", "clipboard", "folder")
3. Descarga el icono en formato PNG
4. Asegúrate de que tenga fondo transparente
5. Renombra el archivo según la lista de arriba
6. Colócalo en la carpeta `icons/`

## Notas Importantes

- Si un icono no existe, el botón seguirá mostrando el emoji/texto actual
- Los iconos se redimensionan automáticamente a 20x20 píxeles
- Los iconos funcionan tanto en modo claro como oscuro
- La aplicación creará la carpeta `icons` automáticamente si no existe

## Ejemplo de Uso

Una vez que agregues los iconos, la aplicación los cargará automáticamente al iniciar. Los botones mostrarán los iconos en lugar de los emojis/texto actual.

