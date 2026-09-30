@echo off
setlocal
REM  Hear the course narration paragraph in several voices, then choose one.
REM  Writes dist\voice-samples\index.html with a player per voice.
cd /d "%~dp0"
title DesignAI Curriculum - voice samples
echo.
echo  Folder: %cd%
echo  Rendering the sample paragraph in each shortlisted voice (needs internet)...
echo.
python engine\voice_samples.py %*
if errorlevel 1 (
  echo.
  echo  Could not render the samples. Is edge-tts installed?   pip install edge-tts
  pause
  exit /b 1
)
echo.
echo  Opening the player...
start "" "dist\voice-samples\index.html"
echo  To use a voice, edit course.yml:   voice: "en-US-JennyNeural"   (the line is shown under each sample)
pause
