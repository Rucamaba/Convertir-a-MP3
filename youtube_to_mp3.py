# -*- coding: utf-8 -*-
import yt_dlp
import os
import sys
from pathlib import Path
import traceback

def my_hook(d):
    if d["status"] == "downloading":
        print(f"\rDescargando... {d['_percent_str']} completado", end="", flush=True)
    elif d["status"] == "finished":
        print("\nDescarga completada, comenzando conversión a MP3...")

def convert_to_mp3(url, output_dir=None):
    try:
        # Set fixed output directory
        output_dir = r"C:\Users\ruben\Music\YouTube Downloads"
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Directorio de salida: {output_dir}")
        print("Iniciando descarga...")
        
        # Configure yt-dlp options with 256kbps quality
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "256",  # Changed to 256kbps
            }],
            "ffmpeg_location": r"C:\Convertir a MP3\ffmpeg\ffmpeg-7.1-essentials_build\bin",
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [my_hook],
            "verbose": True
        }

        print("Configuración completada, iniciando descarga...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Descargando video...")
            ydl.download([url])
            
        print(f"\nConversión completada. El archivo MP3 se guardó en: {output_dir}")
        return True
        
    except Exception as e:
        print(f"\nError durante la descarga: {str(e)}")
        print("\nDetalles del error:")
        traceback.print_exc()
        return False

def main():
    try:
        if len(sys.argv) < 2:
            print("Uso: python youtube_to_mp3.py <URL_del_video>")
            return 1
        
        url = sys.argv[1]
        success = convert_to_mp3(url)
        return 0 if success else 1
        
    except Exception as e:
        print(f"\nError en main: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
