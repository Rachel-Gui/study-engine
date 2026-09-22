@echo off
setlocal
REM ===========================================================================
REM  Renders the narrated MP4 into dist\course.mp4
REM  First run takes a while. After that, only changed scenes re-render.
REM ===========================================================================
cd /d "%~dp0"
title DesignAI Curriculum - render video

echo.
echo  Folder: %cd%
echo.
echo  Step 1 of 2 - checking what is installed
echo  ---------------------------------------
python engine\build.py --doctor
if errorlevel 1 goto :notready

echo.
echo  Step 2 of 2 - rendering at 4K. This takes a while. Leave the window open.
echo  (for a quick 1080p preview run:  python engine\build.py --video --engine edge --quality 1080p)
echo  ------------------------------------------------------------------
python engine\build.py --video --engine edge %*
if errorlevel 1 goto :failed

echo.
echo  ==========================================================
echo   DONE. The video is at:  %cd%\dist\course.mp4
echo  ==========================================================
echo.
pause
exit /b 0

:notready
echo.
echo  ==========================================================
echo   NOT READY. Install everything marked MISSING above.
echo.
echo   ffmpeg is a PROGRAM, not a Python package:
echo       winget install Gyan.FFmpeg
echo   then CLOSE THIS WINDOW and open a new one - Windows only
echo   sees a new PATH in a fresh terminal.
echo.
echo   Nothing was rendered.
echo  ==========================================================
echo.
pause
exit /b 1

:failed
echo.
echo  ==========================================================
echo   RENDER FAILED. Read the message above - it says why.
echo   Nothing usable was written to dist.
echo  ==========================================================
echo.
pause
exit /b 1
