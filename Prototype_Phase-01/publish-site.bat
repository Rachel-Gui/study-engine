@echo off
setlocal
REM ===========================================================================
REM  Builds the site and copies it into the folder of your PUBLIC website
REM  repository, ready to commit and push in GitHub Desktop.
REM
REM  One-time: set SITE_REPO to the folder where GitHub Desktop cloned that
REM  repository (README section 1, "Publish it as a website").
REM ===========================================================================
set "SITE_REPO=D:\ai-for-architecture"

cd /d "%~dp0"
if not exist "%SITE_REPO%\.git" (
  echo.
  echo  The folder %SITE_REPO% is not a cloned repository.
  echo  Edit the SITE_REPO line at the top of publish-site.bat so it points at
  echo  the folder where GitHub Desktop cloned your website repository.
  echo.
  pause
  exit /b 1
)

echo.
echo  Step 1 of 2 - building the site
echo  -------------------------------
python engine\build.py
if errorlevel 1 (
  echo.
  echo  BUILD FAILED - read the message above.
  pause
  exit /b 1
)

echo.
echo  Step 2 of 2 - copying site\ into %SITE_REPO%
echo  ---------------------------------------------
robocopy "site" "%SITE_REPO%" /MIR /XD .git /XF CNAME /NFL /NDL /NJH /NJS
if errorlevel 8 (
  echo  COPY FAILED - is the folder open in another program?
  pause
  exit /b 1
)

echo.
echo  ==========================================================
echo   Done. Now in GitHub Desktop:
echo     1. Current repository: your website repo
echo     2. Summary: "Update site"  ->  Commit to main
echo     3. Push origin
echo   About a minute later the site is updated.
echo  ==========================================================
echo.
pause
