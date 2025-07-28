import yt_dlp
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import re
from ttkthemes import ThemedTk

# Configuration file to store the last used directory
CONFIG_FILE = "config.txt"

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
        self.root.geometry("650x650") # Increased height for new options
        self.root.resizable(False, False)

        # --- Style Configuration ---
        self.style = ttk.Style(self.root)
        self.style.configure('TLabel', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=10)
        self.style.configure('TRadiobutton', font=('Segoe UI', 10))
        self.style.configure('TLabelframe.Label', font=('Segoe UI', 11, 'bold'))
        self.style.configure('TCombobox', font=('Segoe UI', 10))

        # --- Main Frame ---
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- URL Input ---
        url_label = ttk.Label(main_frame, text="Media URL:")
        url_label.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.url_entry = ttk.Entry(main_frame, font=('Segoe UI', 10))
        self.url_entry.pack(fill=tk.X, padx=5, pady=(0, 15))
        
        # --- Save Location ---
        dir_frame = ttk.LabelFrame(main_frame, text="Save Location", padding="10")
        dir_frame.pack(fill=tk.X, padx=5, pady=(0, 15))
        self.output_path = tk.StringVar(value=self.load_last_directory())
        dir_entry = ttk.Entry(dir_frame, textvariable=self.output_path, state='readonly', font=('Segoe UI', 9))
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        browse_button = ttk.Button(dir_frame, text="Browse...", command=self.select_directory, style='TButton')
        browse_button.pack(side=tk.RIGHT)

        # --- Download Options ---
        options_container = ttk.Frame(main_frame)
        options_container.pack(fill=tk.X, expand=True, pady=(0, 15))

        # --- Format Selection ---
        format_frame = ttk.LabelFrame(options_container, text="Format Selection", padding="10")
        format_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 10))
        
        self.download_type = tk.StringVar(value="audio")
        audio_radio = ttk.Radiobutton(format_frame, text="Audio", variable=self.download_type, value="audio", command=self.toggle_format_options)
        audio_radio.grid(row=0, column=0, sticky=tk.W, pady=(0,5))
        video_radio = ttk.Radiobutton(format_frame, text="Video", variable=self.download_type, value="video", command=self.toggle_format_options)
        video_radio.grid(row=1, column=0, sticky=tk.W)

        self.audio_format = tk.StringVar(value='mp3')
        self.audio_combo = ttk.Combobox(format_frame, textvariable=self.audio_format, values=['mp3', 'wav', 'm4a'], state='readonly', width=10)
        self.audio_combo.grid(row=0, column=1, padx=10)

        self.video_format = tk.StringVar(value='mp4')
        self.video_combo = ttk.Combobox(format_frame, textvariable=self.video_format, values=['mp4', 'mkv', 'webm'], state='disabled', width=10)
        self.video_combo.grid(row=1, column=1, padx=10)

        # --- Trimming Options ---
        trim_frame = ttk.LabelFrame(options_container, text="Trimming (Optional)", padding="10")
        trim_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 5))
        
        ttk.Label(trim_frame, text="Start (HH:MM:SS):").grid(row=0, column=0, sticky=tk.W)
        self.start_time_entry = ttk.Entry(trim_frame, width=12)
        self.start_time_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(trim_frame, text="End (HH:MM:SS):").grid(row=1, column=0, sticky=tk.W, pady=(5,0))
        self.end_time_entry = ttk.Entry(trim_frame, width=12)
        self.end_time_entry.grid(row=1, column=1, padx=5, pady=(5,0))


        # --- Download Button ---
        self.download_button = ttk.Button(main_frame, text="Download", command=self.start_download_thread)
        self.download_button.pack(fill=tk.X, padx=5, pady=15)

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

    def toggle_format_options(self):
        """Enable/disable format comboboxes based on radio button selection."""
        if self.download_type.get() == "audio":
            self.audio_combo.config(state='readonly')
            self.video_combo.config(state='disabled')
        else:
            self.audio_combo.config(state='disabled')
            self.video_combo.config(state='readonly')

    def save_last_directory(self, path):
        """Saves the given path to the config file."""
        try:
            with open(CONFIG_FILE, 'w') as f:
                f.write(path)
        except Exception as e:
            print(f"Error saving config file: {e}")

    def load_last_directory(self):
        """Loads the last used path from the config file."""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    path = f.read().strip()
                    if os.path.isdir(path):
                        return path
            return os.getcwd()
        except Exception as e:
            print(f"Error loading config file: {e}")
            return os.getcwd()

    def select_directory(self):
        initial_dir = self.output_path.get()
        path = filedialog.askdirectory(title="Select a Folder", initialdir=initial_dir)
        if path:
            self.output_path.set(path)
            self.save_last_directory(path)
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
            start_time = self.start_time_entry.get().strip()
            end_time = self.end_time_entry.get().strip()

            # Base options
            ydl_opts = {
                'outtmpl': os.path.join(directory, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'progress_hooks': [self.yt_dlp_hook],
                'noprogress': True,
            }

            # --- Postprocessor and Trimming Logic ---
            postprocessor_args = []
            if start_time:
                postprocessor_args.extend(['-ss', start_time])
            if end_time:
                postprocessor_args.extend(['-to', end_time])

            if choice == 'audio':
                audio_format = self.audio_format.get()
                print(f"Starting audio download (Format: {audio_format})...")
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': audio_format,
                        'preferredquality': '192',
                    }],
                })
                # Add trimming args if specified
                if postprocessor_args:
                    ydl_opts['postprocessor_args'] = postprocessor_args

            else: # video
                video_format = self.video_format.get()
                print(f"Starting video download (Format: {video_format})...")
                ydl_opts.update({
                    'format': f'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext={video_format}]/best',
                    'merge_output_format': video_format,
                })
                # Add trimming args if specified
                if postprocessor_args:
                     ydl_opts['postprocessor_args'] = ['-c', 'copy'] + postprocessor_args


            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        except Exception as e:
            print(f"\nAn error occurred: {e}")
        finally:
            self.download_button.config(state=tk.NORMAL, text="Download")
            messagebox.showinfo("Complete", "Download process finished. Check the status window for details.")


    def yt_dlp_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes_str = d.get('total_bytes_estimate') or d.get('total_bytes')
            if total_bytes_str:
                downloaded_bytes = d.get('downloaded_bytes', 0)
                percentage = (downloaded_bytes / total_bytes_str) * 100
                self.progress_bar['value'] = percentage
                self.root.update_idletasks()
        elif d['status'] == 'finished':
            self.progress_bar['value'] = 100
            print("\nDownload finished, now processing file...")
        elif d['status'] == 'error':
            print("\nAn error occurred during download.")
            self.progress_bar['value'] = 0


if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = DownloaderApp(root)
    root.mainloop()
