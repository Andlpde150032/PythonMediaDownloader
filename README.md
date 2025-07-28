# All-in-One Media Downloader
<img width="1919" height="1032" alt="Screenshot_17" src="https://github.com/user-attachments/assets/6ff8e259-6792-4e44-b463-a092895847f8" />


A Python-based GUI application for downloading audio and video files from various online sources using yt-dlp.

## Features

- **Batch Download & Queue Management**: Add multiple links, manage a download queue, and process all at once
- **In-Place Editing**: Click on the queue to edit type (audio/video), format, or trim times for any job, even after adding
- **Live Per-Job Status**: See real-time status for each item (Pending, Downloading %, Processing, Complete, Error)
- **User-friendly, Resizable GUI**: Modern, resizable interface with queue and status panels
- **Multiple Format Support**: Download audio as MP3, WAV, or M4A; video as MP4, MKV, or WEBM
- **Trimming**: Optionally trim each download by specifying start and end times (HH:MM:SS)
- **Queue Controls**: Remove selected, clear all, and reorder downloads
- **Remembers Last Directory**: Automatically loads your last used download folder
- **Progress Tracking**: Real-time download progress with status console
- **Custom Save Location**: Choose where to save your downloaded files
- **Cross-platform**: Works on Windows, macOS, and Linux

## Prerequisites

Before using this tool, you need to install:

1. **Python 3.7 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **FFmpeg** (Required for audio/video processing)
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Add FFmpeg to your system PATH

## Installation

### Quick Setup (Windows)

1. **Install Python Libraries**:
   - Double-click `install_libraries.bat` to install required Python packages
   - This will install `yt-dlp` and `ttkthemes` automatically

2. **Install FFmpeg**:
   - Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Extract and add the `bin` folder to your system PATH
   - Verify installation by opening Command Prompt and typing `ffmpeg -version`

### Manual Installation

If you prefer to install manually:

```bash
pip install yt-dlp ttkthemes
```

## Usage

### Starting the Application

**Option 1: Using the batch file (Recommended)**
- Double-click `run.bat` to launch the application

**Option 2: Command line**
```bash
python mp3.py
```

### How to Use

1. **Add Links to Queue**: Paste one or more URLs (one per line) in the "Add Links to Queue" box.
2. **Set Download Options** (applies to all links being added):
   - **Format & Type**: Choose Audio (MP3, WAV, M4A) or Video (MP4, MKV, WEBM)
   - **Trimming (Optional)**: Enter start and/or end time (HH:MM:SS) to download only a segment
3. **Add to Queue**: Click "Add to Queue" to add all links with the selected options.
4. **Edit Queue Items**: Click on any cell in the queue to change type, format, or trim times for that job—even after adding it. A dialog or dropdown will appear for editing.
5. **Queue Management**:
   - Remove selected items, clear the queue, or review status for each item
   - You can add more links with different options at any time
6. **Choose Save Location**: Click "Browse..." to select where to save files (remembers your last used folder)
7. **Start Download**: Click "Start Queue" to begin downloading all items in the queue
8. **Monitor Progress**: Each item shows its own status (Pending, Downloading %, Processing, Complete, Error) and the progress bar shows current download progress

### Supported Sources

This tool supports downloading from various platforms including:
- YouTube
- Vimeo
- SoundCloud
- And many other sites supported by yt-dlp

## File Structure

```
mp3downloader/
├── mp3.py                 # Main application file
├── install_libraries.bat  # Automatic library installer
├── run.bat                # Application launcher
├── config.txt             # Stores last used directory (auto-generated)
└── README.md              # This file
```

## Troubleshooting

### Common Issues

1. **"FFmpeg not found" error**
   - Make sure FFmpeg is installed and added to your system PATH
   - Restart your computer after adding FFmpeg to PATH

2. **"Module not found" errors**
   - Run `install_libraries.bat` again
   - Or manually install: `pip install yt-dlp ttkthemes`

3. **Download fails**
   - Check your internet connection
   - Verify the URL is valid and accessible
   - Some videos may be restricted or region-locked

### Getting Help

If you encounter issues:
1. Check the status console for error messages
2. Ensure all prerequisites are properly installed
3. Try downloading from a different source

## Technical Details

- **Framework**: tkinter with ttkthemes for modern UI
- **Download Engine**: yt-dlp (YouTube-DL fork)
- **Audio/Video Processing**: FFmpeg for conversion and trimming
- **Threading**: Downloads run in background threads to keep GUI responsive
- **Config File**: Remembers last used directory in `config.txt`
- **Batch/Queue Logic**: Each download in the queue is processed with its own options and status
- **In-Place Editing**: Clickable queue cells for type, format, and trim (with dialogs/dropdowns)
- **Live Status**: Per-job status updates, including download percentage and error reporting
- **Resizable GUI**: The window and queue are fully resizable for better usability

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

**Note**: This tool is for personal use only. Please respect copyright laws and terms of service of the platforms you download from. 
