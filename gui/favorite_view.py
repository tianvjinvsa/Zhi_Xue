"""
收藏管理界面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QMessageBox, QListWidget, QListWidgetItem, QSplitter,
    QScrollArea, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QBrush

from services import FavoriteService
from models import QuestionType, FavoriteQuestion


class FavoriteView(QWidget):
    """收藏管理视图"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.favorite_service = FavoriteService()
        self.current_bank_id = None  # 当前选中的题库ID，None表示全部
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # 标题卡片
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(24, 20, 24, 20)
        
        title_label = QLabel("⭐ 我的收藏")
        title_label.setFont(QFont("Microsoft YaHei UI", 20, QFont.Bold))
        title_label.setStyleSheet("color: #1e293b; border: none; background: transparent;")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("收藏的题目按题库分类整理，方便复习")
        subtitle_label.setStyleSheet("color: #64748b; font-size: 14px; border: none; background: transparent;")
        title_layout.addWidget(subtitle_label)
        
        layout.addWidget(title_frame)
        
        # 统计卡片
        stats_widget = self._create_stats_cards()
        layout.addWidget(stats_widget)
        
        # 主内容区
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e2e8f0;
                width: 1px;
            }
        """)
        
        # 左侧：题库分类列表
        left_widget = self._create_bank_list_panel()
        content_splitter.addWidget(left_widget)
        
        # 右侧：收藏题目列表
        right_widget = self._create_question_list_panel()
        content_splitter.addWidget(right_widget)
        
        content_splitter.setSizes([280, 900])
        layout.addWidget(content_splitter, 1)

    def showEvent(self, event):
        """界面显示时自动刷新"""
        super().showEvent(event)
        self.refresh()
    
    def _create_stats_cards(self) -> QWidget:
        """创建统计卡片"""
        widget = QFrame()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # 总收藏数
        self.total_card = self._create_stat_card("⭐ 总收藏数", "0", "#f59e0b")
        layout.addWidget(self.total_card)
        
        # 题库数
        self.bank_card = self._create_stat_card("📚 涉及题库", "0", "#667eea")
        layout.addWidget(self.bank_card)
        
        # 单选题
        self.single_card = self._create_stat_card("📌 单选题", "0", "#10b981")
        layout.addWidget(self.single_card)
        
        # 多选题
        self.multiple_card = self._create_stat_card("☑️ 多选题", "0", "#8b5cf6")
        layout.addWidget(self.multiple_card)
        
        return widget
    
    def _create_stat_card(self, title: str, value: str, color: str) -> QFrame:
        """创建单个统计卡片"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }}
        """)
        card.setFixedHeight(100)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-size: 13px; border: none;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Microsoft YaHei UI", 24, QFont.Bold))
        value_label.setStyleSheet(f"color: {color}; border: none;")
        layout.addWidget(value_label)
        
        layout.addStretch()
        
        card.value_label = value_label
        return card
    
    def _create_bank_list_panel(self) -> QWidget:
        """创建题库分类面板"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        widget.setFixedWidth(280)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 标题
        header_label = QLabel("📁 题库分类")
        header_label.setFont(QFont("Microsoft YaHei UI", 14, QFont.Bold))
        header_label.setStyleSheet("color: #1e293b; border: none;")
        layout.addWidget(header_label)
        
        # 题库列表
        self.bank_list = QListWidget()
        self.bank_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: transparent;
                outline: none;
            }
            QListWidget::item {
                padding: 12px 16px;
                border-radius: 8px;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background-color: #f8fafc;
            }
            QListWidget::item:selected {
                background-color: #f5f3ff;
                color: #667eea;
            }
        """)
        self.bank_list.itemClicked.connect(self._on_bank_selected)
        layout.addWidget(self.bank_list, 1)
        
        # 清空按钮
        clear_btn = QPushButton("🗑️ 清空所有收藏")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #fef2f2;
                color: #ef4444;
                border: 1px solid #fecaca;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #fee2e2;
            }
        """)
        clear_btn.clicked.connect(self._clear_all_favorites)
        layout.addWidget(clear_btn)
        
        return widget
    
    def _create_question_list_panel(self) -> QWidget:
        """创建题目列表面板"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 标题
        self.list_header = QLabel("📝 全部收藏")
        self.list_header.setFont(QFont("Microsoft YaHei UI", 14, QFont.Bold))
        self.list_header.setStyleSheet("color: #1e293b; border: none;")
        layout.addWidget(self.list_header)
        
        # 题目表格
        self.question_table = QTableWidget()
        self.question_table.setColumnCount(6)
        self.question_table.setHorizontalHeaderLabels(["题库", "类型", "题目内容", "难度", "收藏时间", "操作"])
        self.question_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.question_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.question_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.question_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.question_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.question_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.question_table.setColumnWidth(0, 120)
        self.question_table.setColumnWidth(1, 80)
        self.question_table.setColumnWidth(3, 80)
        self.question_table.setColumnWidth(4, 140)
        self.question_table.setColumnWidth(5, 130)
        self.question_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.question_table.verticalHeader().setVisible(False)
        self.question_table.setShowGrid(False)
        self.question_table.setAlternatingRowColors(True)
        self.question_table.verticalHeader().setDefaultSectionSize(45)
        self.question_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                background-color: #f5f3ff;
                color: #1e293b;
            }
            QTableWidget::item:alternate {
                background-color: #fafbfc;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: 600;
                font-size: 13px;
                color: #475569;
            }
        """)
        
        layout.addWidget(self.question_table, 1)
        
        return widget
    
    def refresh(self):
        """刷新数据"""
        self.favorite_service.reload()
        self._load_banks()
        self._load_questions()
        self._update_stats()
    
    def _load_banks(self):
        """加载题库分类"""
        self.bank_list.clear()
        
        # 添加"全部"选项
        all_item = QListWidgetItem("📋 全部收藏")
        all_item.setData(Qt.UserRole, None)
        self.bank_list.addItem(all_item)
        
        # 加载有收藏的题库
        banks = self.favorite_service.get_banks_with_favorites()
        for bank in banks:
            item = QListWidgetItem(f"📁 {bank['name']} ({bank['count']})")
            item.setData(Qt.UserRole, bank['id'])
            self.bank_list.addItem(item)
        
        # 默认选中第一项
        if self.bank_list.count() > 0:
            self.bank_list.setCurrentRow(0)
    
    def _load_questions(self):
        """加载题目列表"""
        self.question_table.setRowCount(0)
        
        if self.current_bank_id:
            favorites = self.favorite_service.get_favorites_by_bank(self.current_bank_id)
        else:
            favorites = self.favorite_service.get_all_favorites()
        
        for fav in favorites:
            row = self.question_table.rowCount()
            self.question_table.insertRow(row)
            
            # 题库
            bank_item = QTableWidgetItem(fav.bank_name)
            bank_item.setData(Qt.UserRole, fav.question_id)
            self.question_table.setItem(row, 0, bank_item)
            
            # 类型
            type_text = QuestionType.get_display_name(fav.question_type)
            type_item = QTableWidgetItem(type_text)
            type_item.setTextAlignment(Qt.AlignCenter)
            self.question_table.setItem(row, 1, type_item)
            
            # 题目内容
            content = fav.question_content[:40] + "..." if len(fav.question_content) > 40 else fav.question_content
            self.question_table.setItem(row, 2, QTableWidgetItem(content))
            
            # 难度
            diff_text = "★" * fav.difficulty
            diff_item = QTableWidgetItem(diff_text)
            diff_item.setTextAlignment(Qt.AlignCenter)
            diff_item.setForeground(QBrush(QColor("#f59e0b")))
            self.question_table.setItem(row, 3, diff_item)
            
            # 收藏时间
            time_item = QTableWidgetItem(fav.favorite_time[:10] if fav.favorite_time else "")
            time_item.setTextAlignment(Qt.AlignCenter)
            self.question_table.setItem(row, 4, time_item)
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(4)
            
            view_btn = QPushButton("查看")
            view_btn.setFixedSize(54, 28)
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f5f3ff;
                    color: #667eea;
                    border: 1px solid #667eea;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #ede9fe;
                }
            """)
            view_btn.clicked.connect(lambda checked, f=fav: self._view_question(f))
            btn_layout.addWidget(view_btn)
            
            remove_btn = QPushButton("移除")
            remove_btn.setFixedSize(54, 28)
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #fef2f2;
                    color: #ef4444;
                    border: 1px solid #fecaca;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #fee2e2;
                }
            """)
            remove_btn.clicked.connect(lambda checked, qid=fav.question_id: self._remove_favorite(qid))
            btn_layout.addWidget(remove_btn)
            
            self.question_table.setCellWidget(row, 5, btn_widget)
    
    def _update_stats(self):
        """更新统计信息"""
        stats = self.favorite_service.get_statistics()
        
        self.total_card.value_label.setText(str(stats['total']))
        self.bank_card.value_label.setText(str(stats['bank_count']))
        
        type_stats = stats['type_stats']
        self.single_card.value_label.setText(str(type_stats.get('single', 0)))
        self.multiple_card.value_label.setText(str(type_stats.get('multiple', 0)))
    
    def _on_bank_selected(self, item: QListWidgetItem):
        """题库选择事件"""
        self.current_bank_id = item.data(Qt.UserRole)
        
        if self.current_bank_id:
            self.list_header.setText(f"📝 {item.text()}")
        else:
            self.list_header.setText("📝 全部收藏")
        
        self._load_questions()
    
    def _view_question(self, fav: FavoriteQuestion):
        """查看题目详情"""
        from PySide6.QtWidgets import QDialog
        
        dialog = QDialog(self)
        dialog.setWindowTitle("题目详情")
        dialog.setMinimumSize(600, 500)
        dialog.setStyleSheet("QDialog { background-color: #f8fafc; }")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # 题目信息卡片
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(20, 16, 20, 16)
        info_layout.setSpacing(12)
        
        # 类型和难度
        header_layout = QHBoxLayout()
        type_label = QLabel(f"📌 {QuestionType.get_display_name(fav.question_type)}")
        type_label.setStyleSheet("""
            background-color: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 12px;
        """)
        header_layout.addWidget(type_label)
        
        diff_label = QLabel("★" * fav.difficulty + "☆" * (5 - fav.difficulty))
        diff_label.setStyleSheet("color: #f59e0b; font-size: 14px;")
        header_layout.addWidget(diff_label)
        
        header_layout.addStretch()
        
        bank_label = QLabel(f"📁 {fav.bank_name}")
        bank_label.setStyleSheet("color: #64748b; font-size: 12px;")
        header_layout.addWidget(bank_label)
        
        info_layout.addLayout(header_layout)
        
        # 题目内容
        q_label = QLabel(fav.question_content)
        q_label.setWordWrap(True)
        q_label.setStyleSheet("font-size: 15px; color: #1e293b; line-height: 1.6;")
        info_layout.addWidget(q_label)
        
        # 选项
        if fav.options:
            for opt in fav.options:
                opt_label = QLabel(f"  {opt}")
                opt_label.setStyleSheet("color: #475569; font-size: 14px;")
                info_layout.addWidget(opt_label)
        
        layout.addWidget(info_frame)
        
        # 答案和解析
        answer_frame = QFrame()
        answer_frame.setStyleSheet("""
            QFrame {
                background-color: #ecfdf5;
                border: 1px solid #a7f3d0;
                border-radius: 12px;
            }
        """)
        answer_layout = QVBoxLayout(answer_frame)
        answer_layout.setContentsMargins(20, 16, 20, 16)
        
        answer_title = QLabel("✅ 正确答案")
        answer_title.setStyleSheet("color: #059669; font-weight: bold; font-size: 14px;")
        answer_layout.addWidget(answer_title)
        
        answer_text = str(fav.answer)
        if isinstance(fav.answer, list):
            answer_text = ", ".join(fav.answer)
        elif isinstance(fav.answer, bool):
            answer_text = "正确" if fav.answer else "错误"
        
        answer_label = QLabel(answer_text)
        answer_label.setStyleSheet("color: #047857; font-size: 16px; font-weight: bold;")
        answer_layout.addWidget(answer_label)
        
        if fav.explanation:
            exp_label = QLabel(f"💡 {fav.explanation}")
            exp_label.setWordWrap(True)
            exp_label.setStyleSheet("color: #065f46; font-size: 13px; margin-top: 8px;")
            answer_layout.addWidget(exp_label)
        
        layout.addWidget(answer_frame)
        
        # 笔记编辑区域
        note_frame = QFrame()
        note_frame.setStyleSheet("""
            QFrame {
                background-color: #fef3c7;
                border: 1px solid #fcd34d;
                border-radius: 12px;
            }
        """)
        note_layout = QVBoxLayout(note_frame)
        note_layout.setContentsMargins(20, 16, 20, 16)
        
        note_title = QLabel("📝 我的笔记")
        note_title.setStyleSheet("color: #92400e; font-weight: bold; font-size: 14px;")
        note_layout.addWidget(note_title)
        
        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("在这里记录你的学习笔记...")
        self.note_edit.setText(fav.note if fav.note else "")
        self.note_edit.setMaximumHeight(100)
        self.note_edit.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        note_layout.addWidget(self.note_edit)
        
        save_note_btn = QPushButton("💾 保存笔记")
        save_note_btn.setFixedHeight(32)
        save_note_btn.setStyleSheet("""
            QPushButton {
                background-color: #d97706;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #b45309;
            }
        """)
        save_note_btn.clicked.connect(lambda: self._save_note(fav.question_id, self.note_edit.toPlainText()))
        note_layout.addWidget(save_note_btn, alignment=Qt.AlignRight)
        
        layout.addWidget(note_frame)
        
        layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setFixedSize(100, 36)
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46a1);
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
        
        dialog.exec()
    
    def _save_note(self, question_id: str, note: str):
        """保存笔记"""
        if self.favorite_service.update_note(question_id, note):
            QMessageBox.information(self, "成功", "笔记已保存")
        else:
            QMessageBox.warning(self, "失败", "保存笔记失败")
    
    def _remove_favorite(self, question_id: str):
        """移除收藏"""
        reply = QMessageBox.question(
            self, "确认移除", "确定要移除这道收藏的题目吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.favorite_service.remove_favorite(question_id):
                self.refresh()
    
    def _clear_all_favorites(self):
        """清空所有收藏"""
        if self.favorite_service.get_favorites_count() == 0:
            QMessageBox.information(self, "提示", "暂无收藏内容")
            return
        
        reply = QMessageBox.warning(
            self, "确认清空", "确定要清空所有收藏吗？此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.favorite_service.clear_all()
            self.refresh()
            QMessageBox.information(self, "成功", "已清空所有收藏")
