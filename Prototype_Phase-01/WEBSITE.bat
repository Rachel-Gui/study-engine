@echo off
setlocal
REM ===========================================================================
REM  AI for Architecture - build and open the website
REM  Double-click this file. Everything it needs is checked (and installed where
REM  possible) first. Arguments: see tools\website.py
REM ===========================================================================
cd /d "%~dp0"
title AI for Architecture - build and open the website
set "PY="
python --version >nul 2>nul && set "PY=python"
if not defined PY py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY (
  echo.
  echo  Python is not installed. Install it from python.org ^(Lesson 1.1^), then run this again.
  echo.
  pause
  exit /b 1
)
%PY% tools\website.py %*
echo.
pause
