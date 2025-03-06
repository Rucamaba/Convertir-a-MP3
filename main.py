from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.utils import platform
from kivy.clock import Clock, mainthread
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
import yt_dlp
import os
from threading import Thread
import traceback

if platform == "android":
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    
class YouTubeToMP3App(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.theme_cls.primary_palette = "Blue"
    
    def build(self):
        if platform == "android":
            request_permissions([
                Permission.INTERNET,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            ])
        return Builder.load_file('youtube_to_mp3_android.kv')

    def get_output_dir(self):
        if platform == "android":
            # Use Android Music directory
            base_path = primary_external_storage_path()
            return os.path.join(base_path, "Music", "YouTube Downloads")
        else:
            # Use default desktop path for testing
            return os.path.expanduser("~/Music/YouTube Downloads")

    @mainthread
    def update_progress(self, message):
        self.root.ids.progress_label.text = message

    @mainthread
    def update_status(self, message):
        self.root.ids.status_label.text = message

    @mainthread
    def show_dialog(self, title, text):
        if not self.dialog:
            self.dialog = MDDialog(
                title=title,
                text=text,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
        self.dialog.text = text
        self.dialog.title = title
        self.dialog.open()

    def my_hook(self, d):
        if d["status"] == "downloading":
            self.update_progress(f"Descargando... {d['_percent_str']}")
        elif d["status"] == "finished":
            self.update_progress("Descarga completada, comenzando conversión a MP3...")

    def convert_to_mp3(self, url):
        try:
            output_dir = self.get_output_dir()
            os.makedirs(output_dir, exist_ok=True)
            
            self.update_progress("Iniciando descarga...")
            
            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }],
                "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
                "progress_hooks": [self.my_hook],
                "ignoreerrors": True,
                "extract_flat": "in_playlist"
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                except Exception as e:
                    raise Exception(f"Error al obtener información: {str(e)}")

                if "entries" in info:  # Es una playlist
                    total_videos = len(info["entries"])
                    self.update_status(f"Encontrada playlist con {total_videos} videos")
                    processed = 0
                    
                    for entry in info["entries"]:
                        if not entry:
                            continue
                        
                        processed += 1
                        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                        video_title = entry.get("title", "Unknown")
                        mp3_path = os.path.join(output_dir, f"{video_title}.mp3")
                        
                        if os.path.exists(mp3_path):
                            self.update_progress(f"\nSaltando '{video_title}' - Ya existe ({processed}/{total_videos})")
                            continue
                        
                        self.update_progress(f"Descargando '{video_title}' ({processed}/{total_videos})")
                        try:
                            ydl.download([video_url])
                        except Exception as e:
                            self.update_progress(f"Error en '{video_title}': {str(e)}")
                            continue
                            
                else:  # Video individual
                    video_title = info.get("title", "Unknown")
                    mp3_path = os.path.join(output_dir, f"{video_title}.mp3")
                    
                    if os.path.exists(mp3_path):
                        self.update_progress(f"Saltando '{video_title}' - Ya existe")
                    else:
                        self.update_progress(f"Descargando '{video_title}'")
                        ydl.download([url])
            
            self.update_progress("")
            success_message = f"¡Conversión completada!\nArchivo guardado en: {output_dir}"
            self.update_status(success_message)
            self.show_dialog("Éxito", "Conversión completada exitosamente")
            self.root.ids.convert_button.disabled = False
            
        except Exception as e:
            self.update_progress("")
            self.update_status("Error durante la descarga")
            self.show_dialog("Error", f"Error durante la descarga:\n{str(e)}")
            self.root.ids.convert_button.disabled = False

    def start_download(self):
        url = self.root.ids.url_input.text.strip()
        if not url:
            self.show_dialog("Error", "Por favor, ingresa una URL de YouTube")
            return
        
        self.root.ids.convert_button.disabled = True
        self.update_status("")
        Thread(target=self.convert_to_mp3, args=(url,), daemon=True).start()

if __name__ == '__main__':
    YouTubeToMP3App().run()