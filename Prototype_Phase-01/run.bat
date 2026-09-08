@echo off
REM Builds the site and opens it at http://localhost:8000
cd /d "%~dp0"
title DesignAI Curriculum - %cd%
echo.
echo  Folder: %cd%
echo.
python engine\build.py --serve
pause
