@echo off
chcp 65001 >nul
echo 正在测试本地 API 服务...
echo.

cd /d %~dp0
python test_api.py

pause
