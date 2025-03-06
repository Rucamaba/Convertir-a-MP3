import tkinter as tk
from tkinter import messagebox, ttk
import yt_dlp
import os
from threading import Thread

class PlaylistSelector:
    def __init__(self, parent, new_videos, existing_count, on_confirm):
        self.window = tk.Toplevel(parent)
        self.window.title("Seleccionar Canciones")
        self.window.geometry("600x400")
        
        # Centro la ventana
        window_width = 600
        window_height = 400
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.videos = new_videos
        self.on_confirm = on_confirm
        self.selected = {}

        # Marco principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Etiqueta de instrucciones
        status_text = f"Encontradas {len(new_videos)} canciones nuevas"
        if existing_count > 0:
            status_text += f" ({existing_count} ya existentes y serán ignoradas)"
        ttk.Label(main_frame, text=status_text).pack(pady=5)

        # Botones de selección
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        ttk.Button(buttons_frame, text="Seleccionar Todo", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Deseleccionar Todo", command=self.deselect_all).pack(side=tk.LEFT)

        # Frame para la lista con scroll
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Canvas para el scroll
        self.canvas = tk.Canvas(list_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configurar scrollbar
        scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=scrollbar.set)

        # Frame para los checkboxes
        self.checks_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.checks_frame, anchor=tk.NW)

        # Crear checkboxes solo para videos nuevos
        for i, video in enumerate(new_videos):
            var = tk.BooleanVar(value=True)
            self.selected[i] = var
            ttk.Checkbutton(self.checks_frame, text=video['title'], variable=var).pack(anchor=tk.W, pady=2)

        # Actualizar tamaño del scroll
        self.checks_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Botón de confirmación
        ttk.Button(main_frame, text="Descargar Seleccionadas", command=self.confirm).pack(pady=10)

        # Traer ventana al frente
        self.window.lift()
        self.window.focus_force()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas.find_all()[0], width=event.width)

    def select_all(self):
        for var in self.selected.values():
            var.set(True)

    def deselect_all(self):
        for var in self.selected.values():
            var.set(False)

    def confirm(self):
        selected_videos = [
            self.videos[i] for i, var in self.selected.items()
            if var.get()
        ]
        self.window.destroy()
        self.on_confirm(selected_videos)

class SimpleConverterGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("YouTube a MP3")
        self.window.geometry("400x200")
        
        # Centro la ventana
        window_width = 400
        window_height = 200
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Marco principal
        self.frame = ttk.Frame(self.window, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Etiqueta de instrucción
        ttk.Label(self.frame, text="Pega la URL del video o playlist de YouTube:").pack(pady=5)
        
        # Campo de entrada
        self.url_entry = ttk.Entry(self.frame, width=50)
        self.url_entry.pack(pady=10)
        
        # Etiqueta de estado
        self.status_label = ttk.Label(self.frame, text="")
        self.status_label.pack(pady=10)
        
        # Botón de descarga
        self.download_button = ttk.Button(self.frame, text="Analizar URL", command=self.start_analysis)
        self.download_button.pack(pady=10)

        # Carpeta de descargas
        self.output_dir = os.path.join(os.path.expanduser("~"), "Music", "YouTube Downloads")
        os.makedirs(self.output_dir, exist_ok=True)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.window.update()

    def get_safe_filename(self, title):
        """Genera un nombre de archivo seguro y retorna la ruta completa"""
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return os.path.join(self.output_dir, f"{safe_title}.mp3")

    def check_if_exists(self, title):
        """Verifica si una canción ya existe"""
        return os.path.exists(self.get_safe_filename(title))

    def download_videos(self, videos):
        try:
            # Obtenemos la ruta de ffmpeg
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ffmpeg_path = os.path.join(current_dir, "ffmpeg", "ffmpeg-7.1-essentials_build", "bin")

            total = len(videos)
            downloaded = 0

            for i, video in enumerate(videos, 1):
                title = video.get('title', 'Unknown')
                video_url = f"https://www.youtube.com/watch?v={video['id']}"

                # Primero verificamos si existe
                if self.check_if_exists(title):
                    self.update_status(f"Saltando {i}/{total}: {title} (ya existe)")
                    continue

                # Si no existe, procedemos con la descarga
                self.update_status(f"Descargando {i}/{total}: {title}")

                # Configuración de yt-dlp
                ydl_opts = {
                    "format": "bestaudio/best",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "320",
                    }],
                    "ffmpeg_location": ffmpeg_path,
                    "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
                    "quiet": True,
                    "sleep_interval": 1,  # Esperar 1 segundo entre solicitudes
                    "max_sleep_interval": 5,  # Máximo 5 segundos de espera
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "http_headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language": "en-us,en;q=0.5",
                        "Sec-Fetch-Mode": "navigate"
                    }
                }

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                    downloaded += 1
                except Exception as e:
                    self.update_status(f"Error al descargar {title}: {str(e)}")
                    continue

            if downloaded > 0:
                status = f"¡Descargas completadas!\nCanciones descargadas: {downloaded}"
                self.update_status(status)
                messagebox.showinfo("Éxito", f"{status}\nGuardadas en:\n{self.output_dir}")
            else:
                self.update_status("No se descargaron nuevas canciones")
            
            self.download_button.config(state=tk.NORMAL)

        except Exception as e:
            self.update_status("Error durante la descarga")
            messagebox.showerror("Error", str(e))
            self.download_button.config(state=tk.NORMAL)

    def on_playlist_selection(self, selected_videos):
        if selected_videos:
            Thread(target=self.download_videos, args=(selected_videos,), daemon=True).start()
        else:
            self.update_status("No se seleccionaron videos")
            self.download_button.config(state=tk.NORMAL)

    def analyze_url(self, url):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ffmpeg_path = os.path.join(current_dir, "ffmpeg", "ffmpeg-7.1-essentials_build", "bin")

            # Detectar si es un Mix de YouTube
            is_mix = 'mix' in url.lower() or 'RD' in url or 'start_radio=1' in url
            
            if is_mix:
                self.update_status("Mix de YouTube detectado\nNota: Los Mix son dinámicos y pueden variar de los que ves en el navegador")
                # Configuración especial para Mix de YouTube
                ydl_opts = {
                    "quiet": True,
                    "dump_single_json": True,
                    "ffmpeg_location": ffmpeg_path,
                    "extract_flat": False,
                    "playlist_items": "1-50",
                    "sleep_interval": 1,  # Esperar 1 segundo entre solicitudes
                    "max_sleep_interval": 5,  # Máximo 5 segundos de espera
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "http_headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language": "en-us,en;q=0.5",
                        "Sec-Fetch-Mode": "navigate"
                    }
                }
            else:
                # Configuración normal para playlists regulares
                ydl_opts = {
                    "quiet": True,
                    "dump_single_json": True,
                    "ffmpeg_location": ffmpeg_path,
                    "extract_flat": "in_playlist",
                    "playlist_items": "1-50",
                    "sleep_interval": 1,  # Esperar 1 segundo entre solicitudes
                    "max_sleep_interval": 5,  # Máximo 5 segundos de espera
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "http_headers": {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language": "en-us,en;q=0.5",
                        "Sec-Fetch-Mode": "navigate"
                    }
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                except Exception as e:
                    raise Exception(f"Error al obtener información: {str(e)}")
                if 'entries' in info:  # Es una playlist
                    existing_count = 0
                    new_videos = []
                    
                    entries = []
                    if isinstance(info.get('entries'), list):
                        entries = [e for e in info['entries'] if e is not None]

                    if not is_mix:  # Para playlists normales
                        for entry in entries:
                            title = entry.get('title', 'Sin título')
                            if self.check_if_exists(title):
                                existing_count += 1
                            else:
                                video_id = entry.get('id', '')
                                if not video_id and 'url' in entry:
                                    video_id = entry['url'].split('watch?v=')[-1].split('&')[0]
                                if video_id:
                                    new_videos.append({
                                        'id': video_id,
                                        'title': title
                                    })
                    else:  # Si es un Mix de YouTube, extraer información específicamente
                        for entry in entries:
                            title = entry.get('title', '')
                            if not title:
                                continue
                            
                            if self.check_if_exists(title):
                                existing_count += 1
                                continue

                            # Para Mix, intentar obtener el ID de varias formas
                            video_id = None
                            if isinstance(entry, dict):
                                video_id = entry.get('id')
                                if not video_id and 'url' in entry:
                                    url_parts = entry['url'].split('?')
                                    if len(url_parts) > 1:
                                        params = dict(param.split('=') for param in url_parts[1].split('&'))
                                        video_id = params.get('v')

                            if video_id:
                                new_videos.append({
                                    'id': video_id,
                                    'title': title.strip()
                                })
                                if len(new_videos) >= 50:  # Limitar a 50 canciones
                                    self.update_status("Nota: Los Mix de YouTube son personalizados y no muestran exactamente las mismas canciones que en el navegador.\nSe han encontrado canciones relacionadas que puedes seleccionar.")
                                    break
                    
                    if new_videos:
                        self.update_status(f"Encontradas {len(new_videos)} canciones nuevas")
                        PlaylistSelector(self.window, new_videos, existing_count, self.on_playlist_selection)
                    else:
                        msg = f"Todas las canciones ({existing_count}) ya existen en la carpeta"
                        self.update_status(msg)
                        messagebox.showinfo("Información", msg)
                        self.download_button.config(state=tk.NORMAL)
                
                else:  # Es un solo video
                    title = info.get('title', 'Unknown')
                    if self.check_if_exists(title):
                        msg = f"La canción '{title}' ya existe en la carpeta"
                        self.update_status(msg)
                        messagebox.showinfo("Información", msg)
                        self.download_button.config(state=tk.NORMAL)
                    else:
                        video = {'id': info['id'], 'title': title}
                        Thread(target=self.download_videos, args=([video],), daemon=True).start()

        except Exception as e:
            self.update_status("Error al analizar la URL")
            messagebox.showerror("Error", str(e))
            self.download_button.config(state=tk.NORMAL)

    def start_analysis(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Error", "Por favor, ingresa una URL de YouTube")
            return

        self.download_button.config(state=tk.DISABLED)
        self.update_status("Analizando URL...")
        Thread(target=self.analyze_url, args=(url,), daemon=True).start()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = SimpleConverterGUI()
    app.run()