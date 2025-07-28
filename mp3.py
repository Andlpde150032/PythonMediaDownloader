import yt_dlp
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import subprocess
from ttkthemes import ThemedTk

# Configuration file to store the last used directory
CONFIG_FILE = "config.txt"

class StdoutRedirector:
    """A class to redirect stdout to a Tkinter Text widget."""
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.after(0, self.insert_text, string)

    def insert_text(self, string):
        self.text_space.insert(tk.END, string)
        self.text_space.see(tk.END)
        self.text_space.update_idletasks()

    def flush(self):
        pass

class CompletionDialog(tk.Toplevel):
    """Custom dialog window shown on download completion."""
    def __init__(self, parent, title, directory_path):
        super().__init__(parent)
        self.title(title)
        self.directory_path = directory_path
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        message = "The download queue has finished processing."
        ttk.Label(main_frame, text=message, font=('Segoe UI', 10)).pack(pady=(0, 20))

        ok_button = ttk.Button(main_frame, text="OK", command=self.on_ok)
        ok_button.pack()

        # Center the dialog over the parent window
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        self.focus_set()

    def on_ok(self):
        """Handle the OK button click."""
        self.destroy() # Close the dialog first
        self.open_folder()

    def open_folder(self):
        """Opens the specified folder in the default file explorer."""
        try:
            if sys.platform == "win32":
                os.startfile(os.path.realpath(self.directory_path))
            elif sys.platform == "darwin": # macOS
                subprocess.run(["open", self.directory_path])
            else: # Linux
                subprocess.run(["xdg-open", self.directory_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}", parent=self.master)

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("All-in-One Media Downloader - Batch Edition")
        self.root.geometry("800x750")
        self.root.resizable(True, True)

        self.download_queue = []
        self.job_counter = 0
        self.is_downloading = False

        # --- Style Configuration ---
        self.style = ttk.Style(self.root)
        self.style.configure('TLabel', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=8)
        self.style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        self.style.configure('TLabelframe.Label', font=('Segoe UI', 11, 'bold'))

        # --- Main Paned Window for resizable layout ---
        paned_window = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Top Frame for Controls ---
        controls_frame = ttk.Frame(paned_window, padding="10")
        paned_window.add(controls_frame, weight=0)

        # --- URL Input ---
        url_frame = ttk.LabelFrame(controls_frame, text="Add Links to Queue", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 10))
        self.url_text = tk.Text(url_frame, height=4, font=('Segoe UI', 10))
        self.url_text.pack(fill=tk.X, expand=True)

        # --- Settings and Add to Queue Button ---
        settings_container = ttk.Frame(controls_frame)
        settings_container.pack(fill=tk.X, expand=True, pady=(0, 10))
        
        # --- Format Selection ---
        format_frame = ttk.LabelFrame(settings_container, text="Format & Type", padding="10")
        format_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.download_type = tk.StringVar(value="audio")
        audio_radio = ttk.Radiobutton(format_frame, text="Audio", variable=self.download_type, value="audio", command=self.toggle_format_options)
        audio_radio.grid(row=0, column=0, sticky=tk.W)
        video_radio = ttk.Radiobutton(format_frame, text="Video", variable=self.download_type, value="video", command=self.toggle_format_options)
        video_radio.grid(row=1, column=0, sticky=tk.W)
        self.audio_format = tk.StringVar(value='mp3')
        self.audio_combo = ttk.Combobox(format_frame, textvariable=self.audio_format, values=['mp3', 'wav', 'm4a'], state='readonly', width=8)
        self.audio_combo.grid(row=0, column=1, padx=5)
        self.video_format = tk.StringVar(value='mp4')
        self.video_combo = ttk.Combobox(format_frame, textvariable=self.video_format, values=['mp4', 'mkv', 'webm'], state='disabled', width=8)
        self.video_combo.grid(row=1, column=1, padx=5)

        # --- Trimming Options ---
        trim_frame = ttk.LabelFrame(settings_container, text="Trimming (Optional)", padding="10")
        trim_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        ttk.Label(trim_frame, text="Start:").grid(row=0, column=0, sticky=tk.W)
        self.start_time_entry = ttk.Entry(trim_frame, width=10)
        self.start_time_entry.grid(row=0, column=1, padx=5)
        ttk.Label(trim_frame, text="End:").grid(row=1, column=0, sticky=tk.W)
        self.end_time_entry = ttk.Entry(trim_frame, width=10)
        self.end_time_entry.grid(row=1, column=1, padx=5)

        # --- Add to Queue Button ---
        add_button_frame = ttk.Frame(settings_container)
        add_button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        self.add_to_queue_button = ttk.Button(add_button_frame, text="Add to Queue", command=self.add_to_queue)
        self.add_to_queue_button.pack(expand=True, fill=tk.BOTH)

        # --- Queue Management Frame ---
        queue_frame = ttk.LabelFrame(controls_frame, text="Download Queue (Click cell to edit)", padding="10")
        queue_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # --- Treeview for Queue Display ---
        columns = ('#', 'url', 'type', 'format', 'trim', 'status')
        self.queue_tree = ttk.Treeview(queue_frame, columns=columns, show='headings')
        for col in columns:
            self.queue_tree.heading(col, text=col.capitalize())
        self.queue_tree.column('#', width=40, anchor=tk.CENTER)
        self.queue_tree.column('url', width=250)
        self.queue_tree.column('type', width=60, anchor=tk.CENTER)
        self.queue_tree.column('format', width=60, anchor=tk.CENTER)
        self.queue_tree.column('trim', width=120)
        self.queue_tree.column('status', width=100, anchor=tk.W)
        self.queue_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.queue_tree.bind("<Button-1>", self.on_tree_click)
        
        scrollbar = ttk.Scrollbar(queue_frame, orient=tk.VERTICAL, command=self.queue_tree.yview)
        self.queue_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Queue Control Buttons ---
        queue_button_frame = ttk.Frame(controls_frame)
        queue_button_frame.pack(fill=tk.X, pady=(10, 0))
        self.start_queue_button = ttk.Button(queue_button_frame, text="Start Queue", command=self.start_download_thread)
        self.start_queue_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        self.remove_button = ttk.Button(queue_button_frame, text="Remove Selected", command=self.remove_selected)
        self.remove_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.clear_button = ttk.Button(queue_button_frame, text="Clear Queue", command=self.clear_queue)
        self.clear_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        # --- Bottom Frame for Progress and Status ---
        bottom_frame = ttk.Frame(paned_window, padding="10")
        paned_window.add(bottom_frame, weight=1)
        
        # --- Save Location ---
        dir_frame = ttk.LabelFrame(bottom_frame, text="Save Location", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        self.output_path = tk.StringVar(value=self.load_last_directory())
        dir_entry = ttk.Entry(dir_frame, textvariable=self.output_path, state='readonly')
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        browse_button = ttk.Button(dir_frame, text="Browse...", command=self.select_directory)
        browse_button.pack(side=tk.RIGHT)

        # --- Progress and Status ---
        self.progress_bar = ttk.Progressbar(bottom_frame, orient='horizontal', length=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        self.status_box = scrolledtext.ScrolledText(bottom_frame, font=('Courier New', 9), wrap=tk.WORD, height=5)
        self.status_box.pack(fill=tk.BOTH, expand=True)
        
        # Redirect stdout
        sys.stdout = StdoutRedirector(self.status_box)
        sys.stderr = StdoutRedirector(self.status_box)

    def on_tree_click(self, event):
        """Handle single-click events on the queue tree for in-place editing."""
        if self.is_downloading: return

        region = self.queue_tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column_id = self.queue_tree.identify_column(event.x)
        column_index = int(column_id.replace('#', '')) - 1
        column_name = self.queue_tree['columns'][column_index]
        
        item_id = self.queue_tree.identify_row(event.y)
        if not item_id: return

        job = next((j for j in self.download_queue if j['id'] == item_id), None)
        if not job: return

        if column_name == 'type':
            self.create_cell_editor(item_id, column_name, ['Audio', 'Video'])
        elif column_name == 'format':
            values = ['mp3', 'wav', 'm4a'] if job['type'] == 'audio' else ['mp4', 'mkv', 'webm']
            self.create_cell_editor(item_id, column_name, values)
        elif column_name == 'trim':
            self.create_trim_editor_dialog(job)

    def create_cell_editor(self, item_id, column_name, values):
        """Create a combobox over the selected cell for editing."""
        x, y, width, height = self.queue_tree.bbox(item_id, column_name)
        
        current_value = self.queue_tree.set(item_id, column_name)
        
        editor = ttk.Combobox(self.queue_tree, values=values, state='readonly')
        editor.place(x=x, y=y, width=width, height=height)
        editor.set(current_value)
        editor.focus_force()

        editor.after(10, lambda: editor.event_generate('<F4>'))

        def on_editor_close(event):
            new_value = editor.get()
            editor.destroy()
            
            job = next((j for j in self.download_queue if j['id'] == item_id), None)
            if not job: return

            if column_name == 'type':
                job['type'] = new_value.lower()
                job['format'] = 'mp3' if job['type'] == 'audio' else 'mp4'
            elif column_name == 'format':
                job['format'] = new_value
            
            self.update_queue_display(clear_selection=True)

        editor.bind("<FocusOut>", on_editor_close)
        editor.bind("<Return>", on_editor_close)
        editor.bind("<<ComboboxSelected>>", on_editor_close)

    def create_trim_editor_dialog(self, job):
        """Create a dialog to edit the start and end times for a job."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Trim Times")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding="20")
        frame.pack()

        ttk.Label(frame, text="Start Time (HH:MM:SS):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        start_entry = ttk.Entry(frame)
        start_entry.grid(row=0, column=1, padx=5, pady=5)
        start_entry.insert(0, job['start_time'])

        ttk.Label(frame, text="End Time (HH:MM:SS):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        end_entry = ttk.Entry(frame)
        end_entry.grid(row=1, column=1, padx=5, pady=5)
        end_entry.insert(0, job['end_time'])

        def save_and_close():
            job['start_time'] = start_entry.get().strip()
            job['end_time'] = end_entry.get().strip()
            self.update_queue_display(clear_selection=True)
            dialog.destroy()

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, columnspan=2, pady=10)
        ttk.Button(button_frame, text="OK", command=save_and_close).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def toggle_format_options(self):
        if self.download_type.get() == "audio":
            self.audio_combo.config(state='readonly')
            self.video_combo.config(state='disabled')
        else:
            self.audio_combo.config(state='disabled')
            self.video_combo.config(state='readonly')

    def add_to_queue(self):
        urls = self.url_text.get("1.0", tk.END).strip().splitlines()
        urls = [url for url in urls if url.strip()]
        if not urls:
            messagebox.showwarning("Warning", "Please enter at least one URL.")
            return

        for url in urls:
            self.job_counter += 1
            job = {
                'id': f'job_{self.job_counter}',
                'url': url,
                'type': self.download_type.get(),
                'format': self.audio_format.get() if self.download_type.get() == 'audio' else self.video_format.get(),
                'start_time': self.start_time_entry.get().strip(),
                'end_time': self.end_time_entry.get().strip(),
                'status': 'Pending'
            }
            self.download_queue.append(job)
        
        self.update_queue_display()
        self.url_text.delete("1.0", tk.END)

    def update_queue_display(self, clear_selection=False):
        """Refreshes the queue display. Can optionally clear the current selection."""
        selected_items = self.queue_tree.selection()
        self.queue_tree.delete(*self.queue_tree.get_children())
        for i, job in enumerate(self.download_queue):
            trim_str = f"{job['start_time']} - {job['end_time']}" if job['start_time'] or job['end_time'] else "Full"
            values = (i + 1, job['url'], job['type'].capitalize(), job['format'], trim_str, job['status'])
            self.queue_tree.insert('', tk.END, iid=job['id'], values=values)
        
        if selected_items and not clear_selection:
            self.queue_tree.selection_set(selected_items)

    def remove_selected(self):
        selected_items = self.queue_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select items to remove.")
            return
        
        for item_id in selected_items:
            self.download_queue = [job for job in self.download_queue if job['id'] != item_id]
        
        self.update_queue_display()

    def clear_queue(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the entire queue?"):
            self.download_queue.clear()
            self.update_queue_display()

    def save_last_directory(self, path):
        try:
            with open(CONFIG_FILE, 'w') as f: f.write(path)
        except Exception as e: print(f"Error saving config: {e}")

    def load_last_directory(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    path = f.read().strip()
                    if os.path.isdir(path): return path
            return os.getcwd()
        except Exception as e:
            print(f"Error loading config: {e}")
            return os.getcwd()

    def select_directory(self):
        path = filedialog.askdirectory(title="Select a Folder", initialdir=self.output_path.get())
        if path:
            self.output_path.set(path)
            self.save_last_directory(path)
            print(f"Output directory set to: {path}\n")

    def toggle_controls(self, is_active):
        state = tk.NORMAL if is_active else tk.DISABLED
        self.add_to_queue_button.config(state=state)
        self.remove_button.config(state=state)
        self.clear_button.config(state=state)
        self.start_queue_button.config(state=state)
        self.start_queue_button.config(text="Start Queue" if is_active else "Downloading...")

    def start_download_thread(self):
        if self.is_downloading: return
        if not self.download_queue:
            messagebox.showerror("Error", "The download queue is empty.")
            return
        if not os.popen('ffmpeg -version').read():
            messagebox.showerror("Dependency Missing", "FFmpeg not found.")
            return
            
        self.toggle_controls(False)
        self.is_downloading = True
        
        download_thread = threading.Thread(target=self.run_queue_download, daemon=True)
        download_thread.start()
        
    def run_queue_download(self):
        directory = self.output_path.get()
        for job in self.download_queue:
            if job['status'] != 'Pending': continue

            try:
                self.update_job_status(job['id'], 'Downloading...')
                self.progress_bar['value'] = 0
                
                ydl_opts = {
                    'outtmpl': os.path.join(directory, '%(title)s.%(ext)s'),
                    'noplaylist': True,
                    'progress_hooks': [lambda d, j=job: self.yt_dlp_hook(d, j)],
                    'noprogress': True,
                }
                
                trim_args = []
                if job['start_time']: trim_args.extend(['-ss', job['start_time']])
                if job['end_time']: trim_args.extend(['-to', job['end_time']])

                if job['type'] == 'audio':
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': job['format'],
                        'preferredquality': '192',
                    }]
                    if trim_args:
                        ydl_opts['postprocessors'].append({
                            'key': 'FFmpegPostProcessor',
                            'args': trim_args,
                        })
                else: # video
                    ydl_opts['format'] = f'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext={job["format"]}]/best'
                    ydl_opts['merge_output_format'] = job['format']
                    if trim_args:
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegPostProcessor',
                            'args': trim_args,
                        }]

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([job['url']])
                
                job['status'] = 'Complete'
                self.update_job_status(job['id'], 'Complete')

            except Exception as e:
                job['status'] = 'Error'
                self.update_job_status(job['id'], 'Error')
                print(f"\nERROR downloading {job['url']}: {e}")

        self.is_downloading = False
        self.root.after(0, self.toggle_controls, True)
        self.root.after(0, lambda: CompletionDialog(self.root, "Complete", directory))

    def update_job_status(self, job_id, status_text):
        """Safely updates a job's status in the Treeview from any thread."""
        try:
            job_index = next((i for i, job in enumerate(self.download_queue) if job['id'] == job_id), None)
            if job_index is None: return

            job = self.download_queue[job_index]
            trim_str = f"{job['start_time']} - {job['end_time']}" if job['start_time'] or job['end_time'] else "Full"
            new_values = (job_index + 1, job['url'], job['type'].capitalize(), job['format'], trim_str, status_text)
            
            self.root.after(0, lambda j=job_id, v=new_values: self.queue_tree.item(j, values=v))
        except Exception as e:
            print(f"Error updating GUI: {e}")

    def yt_dlp_hook(self, d, job):
        """Hook to update progress. Now receives the current job."""
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes_estimate') or d.get('total_bytes')
            if total_bytes:
                percentage = (d.get('downloaded_bytes', 0) / total_bytes) * 100
                self.progress_bar['value'] = percentage
                self.update_job_status(job['id'], f'Downloading {percentage:.1f}%')
        elif d['status'] == 'finished':
            self.progress_bar['value'] = 100
            self.update_job_status(job['id'], 'Processing...')
            print("\nDownload finished, now processing...")

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = DownloaderApp(root)
    root.mainloop()
