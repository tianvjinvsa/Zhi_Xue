"""
智能答题系统 - 主入口
"""
import sys
import os

# 确保项目根目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from config import config, DATA_DIR, BANKS_DIR, PAPERS_DIR, RESULTS_DIR
from gui import MainWindow


def setup_environment():
    """设置运行环境"""
    # 确保数据目录存在
    for dir_path in [DATA_DIR, BANKS_DIR, PAPERS_DIR, RESULTS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)


def main():
    """主函数"""
    # 设置环境
    setup_environment()
    
    # 设置高DPI支持 - 必须在创建QApplication之前
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("智能答题系统")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SmartQuiz")
    
    # 设置默认字体
    font = QFont("Microsoft YaHei UI", 10)
    app.setFont(font)
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
