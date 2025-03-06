# Conversor de YouTube a MP3

Este programa te permite descargar videos de YouTube y convertirlos automáticamente a formato MP3 de alta calidad (320kbps).

## Características

- ✨ Interfaz gráfica fácil de usar
- 📋 Soporta videos individuales y playlists completas
- ✅ Selector de canciones para playlists
- 🎵 Conversión automática a MP3 de alta calidad (320kbps)
- 📁 Descarga organizada en tu carpeta de Música
- 🔄 Detección automática de archivos existentes (evita descargas duplicadas)

## Cómo usar

1. Haz doble clic en `iniciar_conversor.bat` para abrir el programa
2. Pega la URL del video o playlist de YouTube
3. Click en "Analizar URL"

### Para videos individuales
- El programa comenzará la descarga automátamente
- Verás el progreso en la ventana
- Al terminar, encontrarás el archivo MP3 en tu carpeta de Música

### Para playlists
- Se abrirá una ventana con la lista de todas las canciones encontradas
- Cada canción tendrá una casilla de verificación
- Puedes usar los botones "Seleccionar Todo" o "Deseleccionar Todo"
- Selecciona las canciones que quieres descargar
- Click en "Descargar Seleccionadas"
- El programa descargará solo las canciones seleccionadas

## Ubicación de las descargas

Todas las canciones se guardan en:
```
%USERPROFILE%\Music\YouTube Downloads
```
Por ejemplo:
- En Windows 10/11: `C:\Users\<tu-usuario>\Music\YouTube Downloads`

Los archivos se guardan automáticamente con el título del video como nombre del archivo.

## Solución de problemas

Si encuentras algún error:
- Asegúrate de tener una conexión a internet estable
- Verifica que la URL sea correcta y que el video esté disponible
- Si es una playlist, asegúrate de que sea pública y accesible
- Los archivos que ya existan se saltarán automáticamente para evitar duplicados
- Si el programa no abre, asegúrate de hacer doble clic en `iniciar_conversor.bat`

## Requisitos

- Windows
- Conexión a internet
- No requiere instalación adicional - todo lo necesario está incluido