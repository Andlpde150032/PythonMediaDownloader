@echo off
TITLE Library Installer

echo This script will install the Python libraries required for the Media Downloader.
echo Please ensure you have Python installed and added to your PATH.
echo.
pause
echo.

echo Installing 'yt-dlp'...
pip install yt-dlp

echo.
echo Installing 'ttkthemes'...
pip install ttkthemes

echo.
echo -----------------------------------------
echo All required Python libraries have been installed.
echo.
echo IMPORTANT: You still need to install FFmpeg manually.
echo You can download it from https://ffmpeg.org/download.html
echo -----------------------------------------
echo.
pause
