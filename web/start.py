"""
智题坊 - 启动脚本
支持开发模式和打包后运行
"""
import subprocess
import sys
import os
import time
import webbrowser
import threading
from pathlib import Path

# 判断是否是打包后运行
if getattr(sys, 'frozen', False):
    # 打包后运行 - 使用 _MEIPASS 临时目录
    APP_ROOT = Path(sys._MEIPASS)
    IS_FROZEN = True
else:
    # 开发模式
    APP_ROOT = Path(__file__).parent.parent
    IS_FROZEN = False

# 解决打包后无控制台导致的 stdout 为 None 的问题
if IS_FROZEN:
    class NullWriter:
        def write(self, text): pass
        def flush(self): pass
        def isatty(self): return False
    
    if sys.stdout is None:
        sys.stdout = NullWriter()
    if sys.stderr is None:
        sys.stderr = NullWriter()

# 路径定义
WEB_ROOT = APP_ROOT / "web"
BACKEND_DIR = WEB_ROOT / "backend"
FRONTEND_DIST = WEB_ROOT / "frontend" / "dist"
FRONTEND_DEV = WEB_ROOT / "frontend"


def check_dependencies():
    """检查依赖（仅开发模式）"""
    if IS_FROZEN:
        return
        
    # 检查 fastapi
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("正在安装后端依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn"])


def start_production_server():
    """生产模式：使用 FastAPI 同时服务 API 和静态文件"""
    # 将项目根目录添加到 Python 路径
    sys.path.insert(0, str(APP_ROOT))
    sys.path.insert(0, str(BACKEND_DIR))
    
    import uvicorn
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    # 导入后端应用
    from main import app
    
    # 挂载静态文件
    if FRONTEND_DIST.exists():
        # 挂载 assets 目录
        assets_dir = FRONTEND_DIST / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        
        # 挂载 images 目录
        images_dir = FRONTEND_DIST / "images"
        if images_dir.exists():
            app.mount("/images", StaticFiles(directory=str(images_dir)), name="images")
            
        # 挂载 video 目录
        video_dir = FRONTEND_DEV / "video"
        if video_dir.exists():
            app.mount("/video", StaticFiles(directory=str(video_dir)), name="video")
        
        # 根路由
        @app.get("/")
        async def serve_root():
            return FileResponse(str(FRONTEND_DIST / "index.html"))
        
        # SPA 路由支持
        @app.get("/{path:path}")
        async def serve_spa(path: str):
            # 如果是 API 路径，跳过（让 FastAPI 处理）
            if path.startswith("api/"):
                return None
            
            # 尝试返回静态文件
            file_path = FRONTEND_DIST / path
            if file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))
            
            # 返回 index.html 以支持 SPA 路由
            return FileResponse(str(FRONTEND_DIST / "index.html"))
    
    print()
    print("=" * 50)
    print("           智 题 坊")
    print("=" * 50)
    print()
    print("  服务正在启动...")
    print()
    print("  访问地址: http://localhost:8000")
    print()
    print("  按 Ctrl+C 停止服务")
    print()
    
    # 自动打开浏览器
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8000")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 启动服务
    # 在打包环境下禁用颜色输出，避免 isatty 错误
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning", use_colors=not IS_FROZEN)


def start_dev_server():
    """开发模式：分别启动前后端"""
    print("=" * 50)
    print("    智题坊 - 开发模式")
    print("=" * 50)
    print()
    
    # 检查依赖
    check_dependencies()
    
    # 设置环境变量以强制使用 UTF-8 编码，解决 Windows 下的编码问题
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    
    # 启动后端
    print("启动后端 API 服务...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=str(BACKEND_DIR),
        env=env
    )
    time.sleep(2)
    
    # 检查前端是否需要 npm install
    if not (FRONTEND_DEV / "node_modules").exists():
        print("正在安装前端依赖...")
        subprocess.run(["npm", "install"], cwd=str(FRONTEND_DEV), shell=True)
    
    # 启动前端
    print("启动前端开发服务器...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(FRONTEND_DEV),
        shell=True
    )
    time.sleep(3)
    
    print()
    print("服务已启动！")
    print()
    print("  后端 API: http://localhost:8000")
    print("  API 文档: http://localhost:8000/docs")
    print("  前端界面: http://localhost:5173")
    print()
    print("按 Ctrl+C 停止服务...")
    
    # 自动打开浏览器
    webbrowser.open("http://localhost:5173")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        backend_process.terminate()
        frontend_process.terminate()
        print("服务已停止")


def main():
    """主入口"""
    # 如果是作为子进程运行命令（如 select-folder），则不启动服务器
    if len(sys.argv) > 1 and sys.argv[1] == "-c":
        return

    # 打包后强制使用生产模式
    if IS_FROZEN:
        start_production_server()
        return
    
    # 开发模式：检查是否有前端构建产物
    use_production = FRONTEND_DIST.exists() and "--dev" not in sys.argv
    
    if use_production:
        start_production_server()
    else:
        start_dev_server()


if __name__ == "__main__":
    main()
