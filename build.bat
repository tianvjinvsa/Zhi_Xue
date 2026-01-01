@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ==========================================
:: 智题坊 - 一键打包脚本
:: ==========================================

echo.
echo ========================================
echo         智题坊 - 一键打包工具
echo ========================================
echo.

:: 检查是否在正确目录
if not exist "build.spec" (
    echo [错误] 请在项目根目录运行此脚本
    pause
    exit /b 1
)

:: 步骤1: 检查 Python 环境
echo [1/5] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python
    pause
    exit /b 1
)
echo      √ Python 环境正常

:: 步骤2: 检查 Node.js 环境
echo [2/5] 检查 Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)
echo      √ Node.js 环境正常

:: 步骤3: 安装/更新 Python 依赖
echo [3/5] 检查 Python 依赖...
pip install -r requirements.txt -q
pip install pyinstaller -q
echo      √ Python 依赖已就绪

:: 步骤4: 构建前端
echo [4/5] 构建前端...
cd web\frontend

:: 检查 node_modules
if not exist "node_modules" (
    echo      正在安装前端依赖...
    call npm install --silent
)

:: 构建前端
echo      正在构建前端...
call npm run build

if errorlevel 1 (
    echo [错误] 前端构建失败
    cd ..\..
    pause
    exit /b 1
)
echo      √ 前端构建完成

cd ..\..

:: 步骤5: PyInstaller 打包
echo [5/5] 正在打包应用...
echo.

:: 清理之前的构建
if exist "dist" rmdir /s /q dist
if exist "build\build" rmdir /s /q build\build

:: 执行打包
pyinstaller build.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [错误] 打包失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo            打包完成！
echo ========================================
echo.
echo 输出文件: dist\智题坊.exe
echo.

:: 显示文件大小
for %%A in ("dist\智题坊.exe") do (
    set size=%%~zA
    set /a sizeMB=!size! / 1048576
    echo 文件大小: !sizeMB! MB
)

echo.
echo 提示: 
echo   - 调试模式: 修改 build.spec 中 RELEASE_MODE = False
echo   - 发布模式: 修改 build.spec 中 RELEASE_MODE = True
echo.

pause
