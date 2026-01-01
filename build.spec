# -*- mode: python ; coding: utf-8 -*-
"""
智题坊 - PyInstaller 打包配置文件 (优化版)
使用方法: pyinstaller build.spec

打包前请确保:
1. 已安装所有 Python 依赖: pip install -r requirements.txt
2. 已构建前端: cd web/frontend && npm run build
3. 安装 UPX 压缩工具 (可选，用于减小体积): https://github.com/upx/upx/releases

打包优化说明:
- 使用 UPX 压缩减小体积
- 排除不必要的模块减少体积
- 隐藏控制台窗口 (发布时设置 RELEASE_MODE=True)
"""

import sys
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(SPECPATH)

# ==================== 配置选项 ====================
# 发布模式: True=隐藏控制台, False=显示控制台(调试用)
RELEASE_MODE = False

# 是否使用单文件打包 (True=单exe, False=文件夹)
SINGLE_FILE = True

# 应用名称
APP_NAME = '智题坊'

# ==================== 分析配置 ====================
a = Analysis(
    ['web/start.py'],  # 入口脚本
    pathex=[
        str(ROOT_DIR), 
        str(ROOT_DIR / 'web' / 'backend'),
        str(ROOT_DIR / 'services'),
        str(ROOT_DIR / 'models'),
        str(ROOT_DIR / 'utils'),
    ],
    binaries=[],
    datas=[
        # 资源文件
        ('resources', 'resources'),
        # 前端构建产物
        ('web/frontend/dist', 'web/frontend/dist'),
        # 后端模块
        ('web/backend/main.py', 'web/backend'),
        # 核心模块
        ('models', 'models'),
        ('services', 'services'),
        ('utils', 'utils'),
        # 配置文件
        ('config.py', '.'),
    ],
    hiddenimports=[
        # 高性能 JSON
        'orjson',

        # FastAPI 相关
        'fastapi',
        'fastapi.staticfiles',
        'fastapi.responses',
        'fastapi.middleware',
        'fastapi.middleware.cors',
        'fastapi.encoders',
        'fastapi.exceptions',
        
        # Uvicorn 相关
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
        
        # Starlette 相关
        'starlette',
        'starlette.routing',
        'starlette.responses',
        'starlette.staticfiles',
        'starlette.middleware',
        'starlette.middleware.cors',
        'starlette.exceptions',
        
        # Pydantic 相关
        'pydantic',
        'pydantic_core',
        'pydantic.deprecated.decorator',
        'pydantic.networks',
        
        # HTTP 客户端
        'openai',
        'httpx',
        'httpx._transports',
        'httpx._transports.default',
        'httpcore',
        
        # 异步支持
        'anyio',
        'anyio._backends',
        'anyio._backends._asyncio',
        
        # 文件处理
        'pandas',
        'openpyxl',
        'docx',
        'PIL',
        'PIL.Image',
        
        # 加密
        'cryptography',
        'cryptography.fernet',
        
        # 其他依赖
        'python_multipart',
        'email_validator',
        'h11',
        'sniffio',
        'typing_extensions',
        'dataclasses',
        'json',
        'uuid',
        'datetime',
        
        # 编码支持
        'encodings',
        'encodings.utf_8',
        'encodings.ascii',
        'encodings.gbk',
        'encodings.gb2312',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 图形界面库 (使用 Web 界面，不需要这些)
        # 'tkinter',  # 后端文件夹选择功能需要 tkinter
        # '_tkinter',
        'PySide6',
        'PyQt5',
        'PyQt6',
        'wx',
        'gtk',
        
        # 科学计算库 (如果不需要)
        'matplotlib',
        'scipy',
        'numpy.testing',
        
        # 测试框架
        'test',
        'unittest',
        'pytest',
        'nose',
        
        # 开发工具
        'IPython',
        'jupyter',
        'notebook',
        
        # 其他不需要的模块
        'distutils',
        'setuptools',
        'pkg_resources',
        
        # 大型可选依赖
        'tensorflow',
        'torch',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# ==================== 过滤不必要的文件 ====================
# 移除不必要的本地化文件
a.datas = [x for x in a.datas if not any([
    'locale' in x[0] and not any(loc in x[0] for loc in ['zh', 'en']),  # 只保留中英文
    # 'tcl' in x[0].lower() and 'tk' in x[0].lower(),  # 保留 Tk/Tcl 资源
    '.pyc' in x[0],  # 移除编译缓存
    '__pycache__' in x[0],  # 移除缓存目录
    '.pyo' in x[0],
])]

# ==================== 编译配置 ====================
pyz = PYZ(
    a.pure, 
    a.zipped_data, 
    cipher=None,
)

# ==================== 打包配置 ====================
if SINGLE_FILE:
    # 单文件模式
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name=APP_NAME,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,  # Windows 上设为 False
        upx=True,  # 启用 UPX 压缩
        upx_exclude=[
            'vcruntime140.dll',
            'python*.dll',
            'api-ms-win*.dll',
            'ucrtbase.dll',
        ],
        runtime_tmpdir=None,
        console=not RELEASE_MODE,  # 发布模式隐藏控制台
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=str(ROOT_DIR / 'resources/icons/app.ico') if (ROOT_DIR / 'resources/icons/app.ico').exists() else None,
        version=str(ROOT_DIR / 'version_info.txt') if (ROOT_DIR / 'version_info.txt').exists() else None,
    )
else:
    # 文件夹模式
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=APP_NAME,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=not RELEASE_MODE,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=str(ROOT_DIR / 'resources/icons/app.ico') if (ROOT_DIR / 'resources/icons/app.ico').exists() else None,
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[
            'vcruntime140.dll',
            'python*.dll',
            'api-ms-win*.dll',
        ],
        name=APP_NAME,
    )
