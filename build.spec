# -*- mode: python ; coding: utf-8 -*-
"""
智题坊 - PyInstaller 打包配置文件
使用方法: pyinstaller build.spec

打包前请确保:
1. 已安装所有 Python 依赖: pip install -r requirements.txt
2. 已构建前端: cd web/frontend && npm run build
"""

import sys
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(SPECPATH)

a = Analysis(
    ['web/start.py'],  # 使用 web 版本的启动脚本作为入口
    pathex=[str(ROOT_DIR), str(ROOT_DIR / 'web' / 'backend')],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('web/frontend/dist', 'web/frontend/dist'),  # 包含前端构建产物
        ('web/frontend/video', 'web/frontend/video'),  # 包含视频文件
        ('web/backend/main.py', 'web/backend'),  # 后端主文件
        ('models', 'models'),
        ('services', 'services'),
        ('utils', 'utils'),
        ('config.py', '.'),
    ],
    hiddenimports=[
        'fastapi',
        'fastapi.staticfiles',
        'fastapi.responses',
        'fastapi.middleware',
        'fastapi.middleware.cors',
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.wsproto_impl',
        'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'starlette',
        'starlette.routing',
        'starlette.responses',
        'starlette.staticfiles',
        'starlette.middleware',
        'starlette.middleware.cors',
        'pydantic',
        'pydantic_core',
        'openai',
        'httpx',
        'httpx._transports',
        'httpx._transports.default',
        'anyio',
        'anyio._backends',
        'anyio._backends._asyncio',
        'pandas',
        'openpyxl',
        'docx',
        'PIL',
        'cryptography',
        'python_multipart',
        'email_validator',
        'h11',
        'sniffio',
        'typing_extensions',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'tkinter',
        'test',
        'unittest',
        'PySide6',
        'PyQt5',
        'PyQt6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='智题坊',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 先开启控制台方便调试
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app.ico' if Path('resources/icons/app.ico').exists() else None,
)
