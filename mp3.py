import yt_dlp
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import re
from ttkthemes import ThemedTk

class StdoutRedirector:
    """A class to redirect stdout to a Tkinter Text widget."""
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        # Ensure updates happen on the main thread to prevent GUI errors
        self.text_space.after(0, self.insert_text, string)

    def insert_text(self, string):
        self.text_space.insert(tk.END, string)
        self.text_space.see(tk.END)
        self.text_space.update_idletasks()

    def flush(self):
        pass

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("All-in-One Media Downloader")
        self.root.geometry("650x550")
        self.root.resizable(False, False)

        # --- Style Configuration ---
        self.style = ttk.Style(self.root)
        self.style.configure('TLabel', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=10)
        self.style.configure('TRadiobutton', font=('Segoe UI', 10))
        self.style.configure('TLabelframe.Label', font=('Segoe UI', 11, 'bold'))

        # --- Main Frame ---
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- URL Input ---
        url_label = ttk.Label(main_frame, text="Media URL:")
        url_label.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.url_entry = ttk.Entry(main_frame, font=('Segoe UI', 10))
        self.url_entry.pack(fill=tk.X, padx=5, pady=(0, 20))

        # --- Options Frame ---
        options_container = ttk.Frame(main_frame)
        options_container.pack(fill=tk.X, expand=True)

        # --- Save Location ---
        dir_frame = ttk.LabelFrame(options_container, text="Save Location", padding="10")
        dir_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        
        self.output_path = tk.StringVar(value=os.getcwd())
        dir_entry = ttk.Entry(dir_frame, textvariable=self.output_path, state='readonly', font=('Segoe UI', 9))
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        browse_button = ttk.Button(dir_frame, text="Browse...", command=self.select_directory, style='TButton')
        browse_button.pack(side=tk.RIGHT)

        # --- Download Type ---
        type_frame = ttk.LabelFrame(options_container, text="Format", padding="10")
        type_frame.pack(side=tk.RIGHT, fill=tk.X, padx=(10, 5))
        
        self.download_type = tk.StringVar(value="audio")
        audio_radio = ttk.Radiobutton(type_frame, text="Audio (MP3)", variable=self.download_type, value="audio")
        audio_radio.pack(anchor=tk.W)
        video_radio = ttk.Radiobutton(type_frame, text="Video (MP4)", variable=self.download_type, value="video")
        video_radio.pack(anchor=tk.W)

        # --- Download Button ---
        self.download_button = ttk.Button(main_frame, text="Download", command=self.start_download_thread)
        self.download_button.pack(fill=tk.X, padx=5, pady=20)

        # --- Progress Bar ---
        self.progress_bar = ttk.Progressbar(main_frame, orient='horizontal', length=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # --- Status Console ---
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        self.status_box = scrolledtext.ScrolledText(status_frame, font=('Courier New', 9), wrap=tk.WORD, state='normal')
        self.status_box.pack(fill=tk.BOTH, expand=True)
        
        # Redirect stdout
        sys.stdout = StdoutRedirector(self.status_box)
        sys.stderr = StdoutRedirector(self.status_box)

    def select_directory(self):
        path = filedialog.askdirectory(title="Select a Folder")
        if path:
            self.output_path.set(path)
            print(f"Output directory set to: {path}\n")

    def start_download_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a media URL.")
            return

        if not os.popen('ffmpeg -version').read():
            messagebox.showerror("Dependency Missing", "FFmpeg not found. Please install it from https://ffmpeg.org/download.html")
            return
            
        self.download_button.config(state=tk.DISABLED, text="Downloading...")
        self.status_box.delete('1.0', tk.END)
        self.progress_bar['value'] = 0
        
        directory = self.output_path.get()
        download_thread = threading.Thread(target=self.run_download, args=(url, directory), daemon=True)
        download_thread.start()
        
    def run_download(self, url, directory):
        try:
            choice = self.download_type.get()
            ydl_opts = {
                'outtmpl': os.path.join(directory, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'progress_hooks': [self.yt_dlp_hook],
                'noprogress': True, # Disable default progress bar to use our own
            }
            if choice == 'audio':
                print("Starting audio download...")
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                })
            else: # video
                print("Starting video download...")
                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        except Exception as e:
            print(f"\nAn error occurred: {e}")
        finally:
            self.download_button.config(state=tk.NORMAL, text="Download")
            # FIXED: Removed the faulty playlist check and now shows a single, reliable completion message.
            messagebox.showinfo("Complete", "Download process finished. Check the status window for details.")


    def yt_dlp_hook(self, d):
        if d['status'] == 'downloading':
            # Extract percentage from the progress string
            total_bytes_str = d.get('total_bytes_estimate') or d.get('total_bytes')
            if total_bytes_str:
                downloaded_bytes = d.get('downloaded_bytes', 0)
                percentage = (downloaded_bytes / total_bytes_str) * 100
                self.progress_bar['value'] = percentage
                self.root.update_idletasks() # Update GUI
        elif d['status'] == 'finished':
            self.progress_bar['value'] = 100
            print("\nDownload finished, now processing file...")
        elif d['status'] == 'error':
            print("\nAn error occurred during download.")
            self.progress_bar['value'] = 0


if __name__ == "__main__":
    # ThemedTk requires the 'ttkthemes' library: pip install ttkthemes
    # Using the "arc" theme for a clean, light interface
    root = ThemedTk(theme="arc")
    app = DownloaderApp(root)
    root.mainloop()
