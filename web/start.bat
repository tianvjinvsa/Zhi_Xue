@echo off
chcp 65001 >nul
echo ========================================
echo           智 题 坊
echo ========================================
echo.

:: 检查 Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

:: 启动服务
echo 正在启动服务...
cd /d "%~dp0"
python start.py

pause
