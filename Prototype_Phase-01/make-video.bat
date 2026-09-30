@echo off
setlocal
REM ===========================================================================
REM  Renders one narrated, animated MP4 per lesson (42 videos, 4-8 minutes each)
REM  into dist\video\, and a narration script per video into dist\scripts\.
REM  Each video follows its storyboard: content\<module>\<lesson>.video.md.
REM  First run takes a while. After that, only changed scenes re-render.
REM  Add --modules to also join each module into one file, --course for one big file.
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
echo  Step 2 of 2 - rendering one video per lesson at 4K. Leave the window open.
echo  (one lesson:           python engine\make_videos.py --engine edge --episode 2.8)
echo  (quick 1080p preview:  python engine\make_videos.py --engine edge --quality 1080p)
echo  (one file per module:  make-video.bat --modules)
echo  ------------------------------------------------------------------
python engine\make_videos.py --engine edge %*
if errorlevel 1 goto :failed

echo.
echo  ==========================================================
echo   DONE. Videos:   %cd%\dist\video\
echo         Scripts:  %cd%\dist\scripts\
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
