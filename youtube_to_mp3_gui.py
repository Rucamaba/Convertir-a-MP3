# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import yt_dlp
import os
import sys
import traceback
from threading import Thread

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        root.title("YouTube a MP3")
        
        # Configurar el tamaño y posición de la ventana
        window_width = 500
        window_height = 200
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Marco principal
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Etiqueta URL
        tk.Label(main_frame, text="URL del video:").pack()
        
        # Campo de entrada URL
        self.url_entry = tk.Entry(main_frame, width=50)
        self.url_entry.pack(pady=10)
        
        # Barra de progreso (etiqueta por ahora)
        self.progress_label = tk.Label(main_frame, text="")
        self.progress_label.pack(pady=10)
        
        # Botón de descarga
        self.download_button = tk.Button(main_frame, text="Convertir a MP3", command=self.start_download)
        self.download_button.pack(pady=10)
        
        # Etiqueta de estado
        self.status_label = tk.Label(main_frame, text="")
        self.status_label.pack(pady=10)

    def update_progress(self, message):
        self.progress_label.config(text=message)
        self.root.update()

    def my_hook(self, d):
        if d["status"] == "downloading":
            self.update_progress(f"Descargando... {d['_percent_str']}")
        elif d["status"] == "finished":
            self.update_progress("Descarga completada, comenzando conversión a MP3...")

    def convert_to_mp3(self, url):
        try:
            output_dir = r"C:\Users\ruben\Music\YouTube Downloads"
            os.makedirs(output_dir, exist_ok=True)
            
            self.update_progress("Iniciando descarga...")
            
            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "256",
                }],
                "ffmpeg_location": r"C:\Convertir a MP3\ffmpeg\ffmpeg-7.1-essentials_build\bin",
                "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
                "progress_hooks": [self.my_hook],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.update_progress("")
            self.status_label.config(text=f"¡Conversión completada!\nArchivo guardado en: {output_dir}")
            messagebox.showinfo("Éxito", "Conversión completada exitosamente")
            self.download_button.config(state=tk.NORMAL)
            
        except Exception as e:
            self.update_progress("")
            self.status_label.config(text="Error durante la descarga")
            messagebox.showerror("Error", f"Error durante la descarga:\n{str(e)}")
            self.download_button.config(state=tk.NORMAL)

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Error", "Por favor, ingresa una URL de YouTube")
            return
        
        self.download_button.config(state=tk.DISABLED)
        self.status_label.config(text="")
        Thread(target=self.convert_to_mp3, args=(url,), daemon=True).start()

def main():
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
