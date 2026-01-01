"""
答题结果展示界面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QStackedWidget, QSizePolicy, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from services import ExamService, BankService, PaperService
from models import ExamResult, Question, QuestionType
from .components import QuestionCard


class ResultView(QWidget):
    """答题结果视图"""
    
    back_to_papers = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exam_service = ExamService()
        self.bank_service = BankService()
        self.paper_service = PaperService()
        self.filter_bank_id = None  # 用于筛选的题库ID
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 堆栈：历史列表 / 结果详情
        self.stack = QStackedWidget()
        
        # 历史列表页
        self.history_page = self._create_history_page()
        self.stack.addWidget(self.history_page)
        
        # 结果详情页
        self.detail_page = self._create_detail_page()
        self.stack.addWidget(self.detail_page)
        
        self.main_layout.addWidget(self.stack)
    
    def _create_history_page(self) -> QWidget:
        """创建历史列表页"""
        page = QWidget()
        page.setStyleSheet("background-color: #f8fafc;")
        layout = QVBoxLayout(page)
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
        
        title_label = QLabel("📊 答题记录")
        title_label.setFont(QFont("Microsoft YaHei UI", 20, QFont.Bold))
        title_label.setStyleSheet("color: #1e293b; border: none; background: transparent;")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("查看您的学习进度和历史成绩")
        subtitle_label.setStyleSheet("color: #64748b; font-size: 14px; border: none; background: transparent;")
        title_layout.addWidget(subtitle_label)
        
        layout.addWidget(title_frame)
        
        # 统计卡片
        stats_widget = self._create_stats_cards()
        layout.addWidget(stats_widget)
        
        # 筛选框
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        
        filter_label = QLabel("📚 题库筛选:")
        filter_label.setStyleSheet("color: #475569; font-size: 14px; border: none;")
        filter_layout.addWidget(filter_label)
        
        self.bank_filter_combo = QComboBox()
        self.bank_filter_combo.setMinimumWidth(200)
        self.bank_filter_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: #f8fafc;
            }
            QComboBox:hover {
                border-color: #667eea;
            }
        """)
        self.bank_filter_combo.currentIndexChanged.connect(self._on_bank_filter_changed)
        filter_layout.addWidget(self.bank_filter_combo)
        filter_layout.addStretch()
        
        layout.addWidget(filter_frame)
        
        # 历史表格卡片
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(["试卷名称", "得分", "正确率", "用时", "完成时间", "操作"])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.history_table.setColumnWidth(1, 100)
        self.history_table.setColumnWidth(2, 100)
        self.history_table.setColumnWidth(3, 100)
        self.history_table.setColumnWidth(4, 160)
        self.history_table.setColumnWidth(5, 180)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setShowGrid(False)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 16px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 14px 12px;
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
                padding: 14px 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: 600;
                font-size: 13px;
                color: #475569;
            }
        """)
        
        table_layout.addWidget(self.history_table)
        layout.addWidget(table_frame, 1)
        
        # 设置表格行高
        self.history_table.verticalHeader().setDefaultSectionSize(50)
        
        return page
    
    def _create_stats_cards(self) -> QWidget:
        """创建统计卡片"""
        widget = QFrame()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # 总答题次数
        self.total_card = self._create_stat_card("📝 总答题次数", "0", "#667eea", "#f5f3ff")
        layout.addWidget(self.total_card)
        
        # 平均得分率
        self.avg_card = self._create_stat_card("📈 平均得分率", "0%", "#10b981", "#ecfdf5")
        layout.addWidget(self.avg_card)
        
        # 总答题数
        self.questions_card = self._create_stat_card("💡 总答题数", "0", "#f59e0b", "#fef3c7")
        layout.addWidget(self.questions_card)
        
        # 正确题数
        self.correct_card = self._create_stat_card("✅ 正确题数", "0", "#8b5cf6", "#f5f3ff")
        layout.addWidget(self.correct_card)
        
        return widget
    
    def _create_stat_card(self, title: str, value: str, color: str, bg_color: str = "#f8fafc") -> QFrame:
        """创建单个统计卡片"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }}
        """)
        card.setFixedHeight(120)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #64748b; font-size: 13px;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setFont(QFont("Microsoft YaHei UI", 28, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        layout.addStretch()
        
        card.value_label = value_label
        return card
    
    def _create_detail_page(self) -> QWidget:
        """创建结果详情页"""
        page = QWidget()
        page.setStyleSheet("background-color: #f8fafc;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # 返回按钮
        back_btn = QPushButton("← 返回列表")
        back_btn.setObjectName("ghostButton")
        back_btn.setFixedWidth(120)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #64748b;
                border: none;
                font-size: 13px;
                text-align: left;
            }
            QPushButton:hover {
                color: #667eea;
            }
        """)
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(back_btn)
        
        # 结果概览
        self.result_header = QFrame()
        self.result_header.setObjectName("resultHeader")
        self.result_header.setStyleSheet("""
            QFrame#resultHeader {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        
        header_layout = QVBoxLayout(self.result_header)
        header_layout.setContentsMargins(24, 20, 24, 20)
        header_layout.setSpacing(16)
        
        self.result_title_label = QLabel("📄 试卷名称")
        self.result_title_label.setFont(QFont("Microsoft YaHei UI", 18, QFont.Bold))
        self.result_title_label.setStyleSheet("color: #1e293b;")
        header_layout.addWidget(self.result_title_label)
        
        score_layout = QHBoxLayout()
        score_layout.setSpacing(24)
        
        self.score_label = QLabel("得分: 85/100")
        self.score_label.setFont(QFont("Microsoft YaHei UI", 32, QFont.Bold))
        self.score_label.setStyleSheet("color: #10b981;")
        score_layout.addWidget(self.score_label)
        
        score_layout.addStretch()
        
        self.detail_stats_label = QLabel("正确率: 85% | 用时: 30分钟")
        self.detail_stats_label.setFont(QFont("Microsoft YaHei UI", 14))
        self.detail_stats_label.setStyleSheet("""
            color: #64748b;
            background-color: #f8fafc;
            padding: 10px 16px;
            border-radius: 10px;
        """)
        score_layout.addWidget(self.detail_stats_label)
        
        header_layout.addLayout(score_layout)
        layout.addWidget(self.result_header)
        
        # 题目详情滚动区
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.detail_container = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_container)
        self.detail_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.detail_container)
        layout.addWidget(scroll, 1)
        
        return page
    
    def refresh(self):
        """刷新数据"""
        # 更新题库筛选下拉框
        current_filter = self.bank_filter_combo.currentData()
        self.bank_filter_combo.blockSignals(True)
        self.bank_filter_combo.clear()
        self.bank_filter_combo.addItem("全部记录", None)
        banks = self.bank_service.get_banks_summary()
        for bank in banks:
            self.bank_filter_combo.addItem(f"{bank['name']}", bank['id'])
        # 恢复之前的选择
        if current_filter:
            idx = self.bank_filter_combo.findData(current_filter)
            if idx >= 0:
                self.bank_filter_combo.setCurrentIndex(idx)
        self.bank_filter_combo.blockSignals(False)
        
        self._load_history()
        self._update_stats()
    
    def _on_bank_filter_changed(self, index: int):
        """题库筛选变化"""
        self.filter_bank_id = self.bank_filter_combo.currentData()
        self._load_history()
    
    def _load_history(self):
        """加载历史记录"""
        self.history_table.setRowCount(0)
        
        results = self.exam_service.get_all_results()
        
        for result in results:
            # 如果设置了筛选，检查试卷是否包含该题库
            if self.filter_bank_id:
                paper = self.paper_service.get_paper(result.paper_id)
                if paper and self.filter_bank_id not in paper.source_banks:
                    continue
            
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            
            # 试卷名称
            name_item = QTableWidgetItem(result.paper_title or "未知试卷")
            name_item.setData(Qt.UserRole, result.id)
            self.history_table.setItem(row, 0, name_item)
            
            # 得分
            score_text = f"{result.user_score:.0f}/{result.total_score:.0f}"
            score_item = QTableWidgetItem(score_text)
            score_item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row, 1, score_item)
            
            # 正确率
            stats = result.get_statistics()
            rate_text = f"{stats['accuracy']:.1f}%"
            rate_item = QTableWidgetItem(rate_text)
            rate_item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row, 2, rate_item)
            
            # 用时
            duration_item = QTableWidgetItem(result.get_duration_display())
            duration_item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row, 3, duration_item)
            
            # 完成时间
            self.history_table.setItem(row, 4, QTableWidgetItem(result.end_time or result.start_time))
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(4)
            
            view_btn = QPushButton("查看")
            view_btn.setFixedSize(54, 30)
            view_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #5a67d8, stop:1 #6b46a1);
                }
            """)
            view_btn.clicked.connect(lambda checked, rid=result.id: self.show_result(rid))
            btn_layout.addWidget(view_btn)
            
            del_btn = QPushButton("删除")
            del_btn.setFixedSize(54, 30)
            del_btn.setStyleSheet("""
                QPushButton {
                    background-color: #fef2f2;
                    color: #ef4444;
                    border: 1px solid #fecaca;
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #fee2e2;
                }
            """)
            del_btn.clicked.connect(lambda checked, rid=result.id: self._delete_result(rid))
            btn_layout.addWidget(del_btn)
            
            self.history_table.setCellWidget(row, 5, btn_widget)
    
    def _update_stats(self):
        """更新统计信息"""
        summary = self.exam_service.get_statistics_summary()
        
        self.total_card.value_label.setText(str(summary['total_exams']))
        self.avg_card.value_label.setText(f"{summary['average_score_rate']:.1f}%")
        self.questions_card.value_label.setText(str(summary['total_questions']))
        self.correct_card.value_label.setText(str(summary['correct_questions']))
    
    def show_result(self, result_id: str):
        """显示结果详情"""
        result, questions = self.exam_service.get_result_with_questions(result_id)
        if not result:
            return
        
        # 更新标题
        self.result_title_label.setText(result.paper_title or "答题结果")
        
        # 更新得分
        stats = result.get_statistics()
        score_color = "#4CAF50" if stats['score_rate'] >= 60 else "#F44336"
        self.score_label.setText(f"得分: {result.user_score:.0f}/{result.total_score:.0f}")
        self.score_label.setStyleSheet(f"color: {score_color}; font-size: 24px; font-weight: bold;")
        
        # 更新统计
        self.detail_stats_label.setText(
            f"正确率: {stats['accuracy']:.1f}% | 用时: {result.get_duration_display()}"
        )
        
        # 清除旧内容
        while self.detail_layout.count():
            item = self.detail_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加题目详情
        for i, qr in enumerate(result.details):
            question = questions.get(qr.question_id)
            if not question:
                continue
            
            card = QuestionCard(
                question=question,
                index=i + 1,
                show_answer=True,
                user_answer=qr.user_answer
            )
            self.detail_layout.addWidget(card)
        
        self.detail_layout.addStretch()
        
        # 切换到详情页
        self.stack.setCurrentIndex(1)
    
    def _delete_result(self, result_id: str):
        """删除答题记录"""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这条答题记录吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.exam_service.delete_result(result_id)
            self.refresh()
