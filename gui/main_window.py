"""
主窗口
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QFrame, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QFont, QIcon, QDesktopServices

from config import config, ICONS_DIR
from .bank_view import BankView
from .paper_view import PaperView
from .exam_view import ExamView
from .result_view import ResultView
from .ai_import_view import AIImportView
from .settings_view import SettingsView
from .favorite_view import FavoriteView


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能答题系统")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        self._setup_ui()
        self._apply_styles()
        
        # 自动全屏
        self.showMaximized()
    
    def _setup_ui(self):
        """设置UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 左侧导航栏
        nav_widget = self._create_nav_panel()
        main_layout.addWidget(nav_widget)
        
        # 右侧内容区
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")
        main_layout.addWidget(self.content_stack, 1)
        
        # 创建各个视图
        self.bank_view = BankView()
        self.paper_view = PaperView()
        self.exam_view = ExamView()
        self.result_view = ResultView()
        self.ai_import_view = AIImportView()
        self.settings_view = SettingsView()
        self.favorite_view = FavoriteView()
        
        # 添加到堆栈
        self.content_stack.addWidget(self.bank_view)      # 0
        self.content_stack.addWidget(self.paper_view)     # 1
        self.content_stack.addWidget(self.exam_view)      # 2
        self.content_stack.addWidget(self.result_view)    # 3
        self.content_stack.addWidget(self.ai_import_view) # 4
        self.content_stack.addWidget(self.settings_view)  # 5
        self.content_stack.addWidget(self.favorite_view)  # 6
        
        # 连接信号
        self.paper_view.start_exam_signal.connect(self._start_exam)
        self.exam_view.exam_finished.connect(self._show_result)
        self.result_view.back_to_papers.connect(lambda: self._switch_view(1))
        self.ai_import_view.questions_generated.connect(self._on_ai_questions_generated)
        
        # 默认显示题库管理
        self._switch_view(0)
        self.nav_buttons[0].setChecked(True)
    
    def _create_nav_panel(self) -> QWidget:
        """创建导航面板"""
        nav_widget = QFrame()
        nav_widget.setObjectName("navPanel")
        nav_widget.setFixedWidth(220)
        
        layout = QVBoxLayout(nav_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo区域
        logo_frame = QFrame()
        logo_frame.setObjectName("logoFrame")
        logo_frame.setFixedHeight(80)
        logo_layout = QVBoxLayout(logo_frame)
        
        logo_label = QLabel("📚 智能答题系统")
        logo_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("color: white;")
        logo_layout.addWidget(logo_label)
        
        layout.addWidget(logo_frame)
        
        # 导航按钮
        nav_items = [
            ("📁 题库管理", 0),
            ("📝 试卷管理", 1),
            ("✏️ 开始答题", 2),
            ("📊 答题记录", 3),
            ("⭐ 我的收藏", 6),
            ("🤖 AI导入", 4),
            ("⚙️ 系统设置", 5),
        ]
        
        self.nav_buttons = []
        self.nav_index_map = {}  # 存储视图索引到按钮索引的映射
        
        for btn_idx, (text, view_idx) in enumerate(nav_items):
            btn = QPushButton(text)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda checked, idx=view_idx: self._on_nav_clicked(idx))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
            self.nav_index_map[view_idx] = btn_idx
        
        layout.addStretch()
        
        # 关于作者按钮
        about_btn = QPushButton("👤 关于作者")
        about_btn.setObjectName("navButton")
        about_btn.setFixedHeight(50)
        about_btn.clicked.connect(self._open_author_page)
        layout.addWidget(about_btn)
        
        # 版本信息
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #888; padding: 10px;")
        layout.addWidget(version_label)
        
        return nav_widget
    
    def _open_author_page(self):
        """打开作者主页"""
        QDesktopServices.openUrl(QUrl("http://matehub.top"))
    
    def _on_nav_clicked(self, view_index: int):
        """导航点击处理"""
        # 更新按钮状态 - 根据视图索引找到对应的按钮索引
        btn_index = self.nav_index_map.get(view_index, 0)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == btn_index)
        
        self._switch_view(view_index)
    
    def _switch_view(self, index: int):
        """切换视图"""
        self.content_stack.setCurrentIndex(index)
        
        # 刷新视图数据
        if index == 0:
            self.bank_view.refresh()
        elif index == 1:
            self.paper_view.refresh()
        elif index == 2:
            self.exam_view.refresh_papers()
        elif index == 3:
            self.result_view.refresh()
        elif index == 6:
            self.favorite_view.refresh()
    
    def _start_exam(self, paper_id: str):
        """开始答题"""
        self.exam_view.start_exam(paper_id)
        self._on_nav_clicked(2)
    
    def _show_result(self, result_id: str):
        """显示答题结果"""
        self.result_view.show_result(result_id)
        self._on_nav_clicked(3)
    
    def _on_ai_questions_generated(self, questions: list):
        """AI生成题目回调 - 导入完成后刷新题库视图"""
        # 刷新题库视图以显示新导入的题目
        self.bank_view.refresh()
    
    def _apply_styles(self):
        """应用样式"""
        from config import STYLES_DIR
        import os
        
        # 尝试加载外部样式表
        style_file = os.path.join(STYLES_DIR, "main.qss")
        if os.path.exists(style_file):
            with open(style_file, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        else:
            # 内置默认样式
            self.setStyleSheet("""
                * {
                    font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
                }
                
                QMainWindow {
                    background-color: #f8fafc;
                }
                
                #navPanel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
                }
                
                #logoFrame {
                    background: rgba(255, 255, 255, 0.1);
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }
                
                #navButton {
                    text-align: left;
                    padding: 14px 20px;
                    border: none;
                    background-color: transparent;
                    color: rgba(255, 255, 255, 0.85);
                    font-size: 14px;
                    font-weight: 500;
                    margin: 2px 8px;
                    border-radius: 8px;
                }
                
                #navButton:hover {
                    background-color: rgba(255, 255, 255, 0.15);
                    color: white;
                }
                
                #navButton:checked {
                    background-color: rgba(255, 255, 255, 0.25);
                    color: white;
                    font-weight: 600;
                }
                
                #contentStack {
                    background-color: #f8fafc;
                }
                
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                
                QScrollBar:vertical {
                    border: none;
                    background-color: transparent;
                    width: 8px;
                }
                
                QScrollBar::handle:vertical {
                    background-color: #cbd5e1;
                    border-radius: 4px;
                    min-height: 40px;
                }
                
                QScrollBar::handle:vertical:hover {
                    background-color: #94a3b8;
                }
                
                QPushButton {
                    padding: 10px 20px;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 500;
                    border: none;
                    background-color: #f1f5f9;
                    color: #475569;
                }
                
                QPushButton:hover {
                    background-color: #e2e8f0;
                }
                
                QPushButton#primaryButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: none;
                    padding: 10px 24px;
                }
                
                QPushButton#primaryButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #5a67d8, stop:1 #6b46a1);
                }
                
                QPushButton#secondaryButton {
                    background-color: white;
                    color: #667eea;
                    border: 2px solid #667eea;
                    padding: 8px 22px;
                }
                
                QPushButton#secondaryButton:hover {
                    background-color: #f5f3ff;
                }
                
                QPushButton#dangerButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #ef4444, stop:1 #dc2626);
                    color: white;
                    border: none;
                }
                
                QLineEdit, QTextEdit, QComboBox, QSpinBox {
                    padding: 10px 14px;
                    border: 2px solid #e2e8f0;
                    border-radius: 8px;
                    background-color: white;
                    font-size: 13px;
                }
                
                QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
                    border-color: #667eea;
                }
                
                QTableWidget {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    gridline-color: #f1f5f9;
                }
                
                QTableWidget::item {
                    padding: 12px 8px;
                }
                
                QTableWidget::item:selected {
                    background-color: #f5f3ff;
                    color: #1e293b;
                }
                
                QHeaderView::section {
                    background-color: #f8fafc;
                    padding: 14px 8px;
                    border: none;
                    border-bottom: 2px solid #e2e8f0;
                    font-weight: 600;
                    color: #475569;
                }
            """)
    
    def closeEvent(self, event):
        """关闭事件"""
        # 检查是否有未完成的答题
        if self.exam_view.has_active_exam():
            reply = QMessageBox.question(
                self, "确认退出",
                "当前有未完成的答题，确定要退出吗？\n退出后答题进度将丢失。",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        event.accept()
