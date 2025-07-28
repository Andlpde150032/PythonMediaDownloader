# All-in-One Media Downloader
<img width="647" height="580" alt="down" src="https://github.com/user-attachments/assets/03f5e0a1-8efd-4e17-9980-95a381920f13" />



A Python-based GUI application for downloading audio (MP3) and video (MP4) files from various online sources using yt-dlp.

## Features

- **User-friendly GUI**: Clean and modern interface built with tkinter
- **Multiple Format Support**: Download as MP3 audio or MP4 video
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

1. **Enter Media URL**: Paste the URL of the video/audio you want to download
2. **Choose Save Location**: Click "Browse..." to select where to save files
3. **Select Format**: Choose between "Audio (MP3)" or "Video (MP4)"
4. **Start Download**: Click the "Download" button
5. **Monitor Progress**: Watch the progress bar and status console for updates

### Supported Sources

This tool supports downloading from various platforms including:
- YouTube
- Vimeo
- SoundCloud
- And many other sites supported by yt-dlp

## File Structure

```
mp3downloader/
├── mp3.py              # Main application file
├── install_libraries.bat  # Automatic library installer
├── run.bat             # Application launcher
└── README.md           # This file
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
- **Audio Processing**: FFmpeg for MP3 conversion
- **Threading**: Downloads run in background threads to keep GUI responsive

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

**Note**: This tool is for personal use only. Please respect copyright laws and terms of service of the platforms you download from. 
