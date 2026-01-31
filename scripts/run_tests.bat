@echo off
chcp 65001 >nul
echo Running unit tests...
echo.

cd /d %~dp0
python run_tests.py

pause
