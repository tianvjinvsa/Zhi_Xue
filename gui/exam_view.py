"""
答题界面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QMessageBox, QProgressBar, QStackedWidget,
    QListWidget, QListWidgetItem, QSplitter, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from services import ExamService, PaperService, FavoriteService
from models import Question, QuestionType
from .components import QuestionCard


class ExamView(QWidget):
    """答题视图"""
    
    exam_finished = Signal(str)  # result_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exam_service = ExamService()
        self.paper_service = PaperService()
        self.favorite_service = FavoriteService()
        
        self.current_index = 0
        self.questions = []
        self.answers = {}
        self.marked = set()
        self.timer = QTimer()
        self.remaining_seconds = 0
        self.current_bank_id = ""
        self.current_bank_name = ""
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 堆栈切换：选择试卷 / 答题界面
        self.stack = QStackedWidget()
        
        # 选择试卷页面
        self.select_page = self._create_select_page()
        self.stack.addWidget(self.select_page)
        
        # 答题页面
        self.exam_page = self._create_exam_page()
        self.stack.addWidget(self.exam_page)
        
        self.main_layout.addWidget(self.stack)
    
    def _create_select_page(self) -> QWidget:
        """创建选择试卷页面"""
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
        
        title_label = QLabel("✏️ 开始答题")
        title_label.setFont(QFont("Microsoft YaHei UI", 20, QFont.Bold))
        title_label.setStyleSheet("color: #1e293b; border: none; background: transparent;")
        title_layout.addWidget(title_label)
        
        tip_label = QLabel("选择一份试卷，开始您的答题之旅")
        tip_label.setStyleSheet("color: #64748b; font-size: 14px; border: none; background: transparent;")
        title_layout.addWidget(tip_label)
        
        layout.addWidget(title_frame)
        
        # 试卷列表卡片
        list_frame = QFrame()
        list_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        self.paper_list = QListWidget()
        self.paper_list.setStyleSheet("""
            QListWidget {
                border: none;
                border-radius: 16px;
                background-color: white;
                padding: 8px;
            }
            QListWidget::item {
                padding: 20px;
                border-radius: 12px;
                margin: 4px 8px;
                background-color: #f8fafc;
                border: 1px solid transparent;
            }
            QListWidget::item:hover {
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
            }
            QListWidget::item:selected {
                background-color: #f5f3ff;
                border: 2px solid #667eea;
            }
        """)
        self.paper_list.itemDoubleClicked.connect(self._on_paper_double_clicked)
        list_layout.addWidget(self.paper_list)
        
        layout.addWidget(list_frame, 1)
        
        # 开始按钮
        start_btn = QPushButton("🚀 开始答题")
        start_btn.setObjectName("primaryButton")
        start_btn.setFixedHeight(48)
        start_btn.setFont(QFont("Microsoft YaHei UI", 13, QFont.Bold))
        start_btn.clicked.connect(self._start_selected_exam)
        layout.addWidget(start_btn)
        
        return page
    
    def _create_exam_page(self) -> QWidget:
        """创建答题页面"""
        page = QWidget()
        page.setStyleSheet("background-color: #f8fafc;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 顶部信息栏
        top_bar = QFrame()
        top_bar.setObjectName("examTopBar")
        top_bar.setFixedHeight(70)
        top_bar.setStyleSheet("""
            #examTopBar {
                background-color: white;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 0, 24, 0)
        
        # 试卷标题
        self.paper_title_label = QLabel("📄 试卷标题")
        self.paper_title_label.setFont(QFont("Microsoft YaHei UI", 16, QFont.Bold))
        self.paper_title_label.setStyleSheet("color: #1e293b;")
        top_layout.addWidget(self.paper_title_label)
        
        top_layout.addStretch()
        
        # 倒计时
        self.timer_label = QLabel("⏱️ --:--:--")
        self.timer_label.setFont(QFont("Microsoft YaHei UI", 15, QFont.Bold))
        self.timer_label.setStyleSheet("""
            color: #ef4444;
            padding: 10px 20px;
            background-color: #fef2f2;
            border-radius: 10px;
            border: 1px solid #fecaca;
        """)
        top_layout.addWidget(self.timer_label)
        
        layout.addWidget(top_bar)
        
        # 主内容区
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e2e8f0;
                width: 1px;
            }
        """)
        
        # 左侧：题目区
        left_widget = self._create_question_area()
        content_splitter.addWidget(left_widget)
        
        # 右侧：答题卡
        right_widget = self._create_answer_card_area()
        content_splitter.addWidget(right_widget)
        
        content_splitter.setSizes([900, 300])
        layout.addWidget(content_splitter, 1)
        
        # 底部操作栏 - 使用可滚动的按钮区域
        bottom_bar = QFrame()
        bottom_bar.setObjectName("examBottomBar")
        bottom_bar.setFixedHeight(90)
        bottom_bar.setStyleSheet("""
            #examBottomBar {
                background-color: white;
                border-top: 1px solid #e2e8f0;
            }
        """)
        
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(16, 10, 16, 10)
        bottom_layout.setSpacing(8)
        
        # 进度标签 - 固定在左侧
        self.progress_label = QLabel("第 1 题 / 共 10 题")
        self.progress_label.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        self.progress_label.setStyleSheet("""
            color: #475569;
            padding: 8px 12px;
            background-color: #f1f5f9;
            border-radius: 8px;
        """)
        self.progress_label.setFixedWidth(140)
        bottom_layout.addWidget(self.progress_label)
        
        # 可滚动的按钮区域
        self.btn_scroll_area = QScrollArea()
        self.btn_scroll_area.setWidgetResizable(True)
        self.btn_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.btn_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.btn_scroll_area.setFixedHeight(70)
        self.btn_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:horizontal {
                border: none;
                background-color: #f1f5f9;
                height: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #94a3b8;
                border-radius: 4px;
                min-width: 40px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #64748b;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        btn_container = QWidget()
        btn_container.setStyleSheet("background-color: transparent;")
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(12)
        
        # 按钮通用样式 - 更大更清晰
        large_btn_style = """
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 10px;
                min-width: 110px;
                min-height: 50px;
            }
        """
        
        # 上一题
        self.prev_btn = QPushButton("◀ 上一题")
        self.prev_btn.setStyleSheet(large_btn_style + """
            QPushButton {
                background-color: white;
                color: #667eea;
                border: 2px solid #667eea;
            }
            QPushButton:hover {
                background-color: #f5f3ff;
            }
            QPushButton:pressed {
                background-color: #ede9fe;
            }
        """)
        self.prev_btn.clicked.connect(self._prev_question)
        btn_layout.addWidget(self.prev_btn)
        
        # 标记
        self.mark_btn = QPushButton("⚑ 标记本题")
        self.mark_btn.setCheckable(True)
        self.mark_btn.setStyleSheet(large_btn_style + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f59e0b, stop:1 #d97706);
                color: white;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #d97706, stop:1 #b45309);
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #b45309, stop:1 #92400e);
            }
        """)
        self.mark_btn.clicked.connect(self._toggle_mark)
        btn_layout.addWidget(self.mark_btn)
        
        # 收藏按钮
        self.fav_btn = QPushButton("⭐ 收藏本题")
        self.fav_btn.setStyleSheet(large_btn_style + """
            QPushButton {
                background-color: #fef3c7;
                color: #d97706;
                border: 2px solid #fcd34d;
            }
            QPushButton:hover {
                background-color: #fde68a;
            }
            QPushButton[favorited="true"] {
                background-color: #fbbf24;
                color: white;
                border: none;
            }
        """)
        self.fav_btn.clicked.connect(self._toggle_favorite)
        btn_layout.addWidget(self.fav_btn)
        
        # 下一题
        self.next_btn = QPushButton("下一题 ▶")
        self.next_btn.setStyleSheet(large_btn_style + """
            QPushButton {
                background-color: white;
                color: #667eea;
                border: 2px solid #667eea;
            }
            QPushButton:hover {
                background-color: #f5f3ff;
            }
            QPushButton:pressed {
                background-color: #ede9fe;
            }
        """)
        self.next_btn.clicked.connect(self._next_question)
        btn_layout.addWidget(self.next_btn)
        
        # 交卷按钮 - 使用醒目的红色渐变样式
        submit_btn = QPushButton("📤 提交试卷")
        submit_btn.setFont(QFont("Microsoft YaHei UI", 14, QFont.Bold))
        submit_btn.setStyleSheet(large_btn_style + """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ef4444, stop:1 #dc2626);
                color: white;
                border: none;
                min-width: 130px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #dc2626, stop:1 #b91c1c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #b91c1c, stop:1 #991b1b);
            }
        """)
        submit_btn.clicked.connect(self._submit_exam)
        btn_layout.addWidget(submit_btn)
        
        btn_layout.addStretch()
        
        self.btn_scroll_area.setWidget(btn_container)
        bottom_layout.addWidget(self.btn_scroll_area, 1)
        
        layout.addWidget(bottom_bar)
        
        return page
    
    def _create_question_area(self) -> QWidget:
        """创建题目区域"""
        widget = QFrame()
        widget.setStyleSheet("background-color: #f8fafc;")
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: transparent;
            }
        """)
        
        self.question_container = QWidget()
        self.question_container.setStyleSheet("background-color: transparent;")
        self.question_layout = QVBoxLayout(self.question_container)
        self.question_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area.setWidget(self.question_container)
        layout.addWidget(self.scroll_area)
        
        return widget
    
    def _create_answer_card_area(self) -> QWidget:
        """创建答题卡区域"""
        widget = QFrame()
        widget.setObjectName("answerCardArea")
        widget.setStyleSheet("""
            #answerCardArea {
                background-color: white;
                border-left: 1px solid #e2e8f0;
            }
        """)
        widget.setFixedWidth(300)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 标题
        card_title = QLabel("📋 答题卡")
        card_title.setFont(QFont("Microsoft YaHei UI", 14, QFont.Bold))
        card_title.setStyleSheet("color: #1e293b;")
        layout.addWidget(card_title)
        
        # 图例
        legend_frame = QFrame()
        legend_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        legend_layout = QHBoxLayout(legend_frame)
        legend_layout.setContentsMargins(12, 8, 12, 8)
        legend_layout.setSpacing(16)
        
        answered_box = QLabel("🟢 已答")
        answered_box.setStyleSheet("color: #059669; font-size: 12px;")
        legend_layout.addWidget(answered_box)
        
        unanswered_box = QLabel("⚪ 未答")
        unanswered_box.setStyleSheet("color: #94a3b8; font-size: 12px;")
        legend_layout.addWidget(unanswered_box)
        
        marked_box = QLabel("🟡 标记")
        marked_box.setStyleSheet("color: #d97706; font-size: 12px;")
        legend_layout.addWidget(marked_box)
        
        legend_layout.addStretch()
        layout.addWidget(legend_frame)
        
        # 答题卡网格
        self.card_scroll = QScrollArea()
        self.card_scroll.setWidgetResizable(True)
        self.card_scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: transparent;
            }
        """)
        
        self.card_container = QWidget()
        self.card_layout = QHBoxLayout(self.card_container)
        self.card_layout.setContentsMargins(0, 10, 0, 10)
        self.card_layout.setSpacing(0)
        
        # 使用FlowLayout效果
        from PySide6.QtWidgets import QGridLayout
        self.card_grid = QGridLayout()
        self.card_grid.setSpacing(10)
        self.card_layout.addLayout(self.card_grid)
        self.card_layout.addStretch()
        
        self.card_scroll.setWidget(self.card_container)
        layout.addWidget(self.card_scroll, 1)
        
        # 统计
        self.stats_label = QLabel("已答: 0 / 10")
        self.stats_label.setFont(QFont("Microsoft YaHei UI", 13))
        self.stats_label.setStyleSheet("""
            color: #475569; 
            padding: 12px;
            background-color: #f8fafc;
            border-radius: 8px;
        """)
        layout.addWidget(self.stats_label)
        
        return widget
    
    def refresh_papers(self):
        """刷新试卷列表"""
        self.paper_list.clear()
        
        papers = self.paper_service.get_all_papers()
        for paper in papers:
            time_text = f"{paper.time_limit}分钟" if paper.time_limit > 0 else "不限时"
            item_text = f"{paper.title}\n📝 {len(paper.questions)}题  |  💯 总分{int(paper.total_score)}分  |  ⏱️ {time_text}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, paper.id)
            self.paper_list.addItem(item)
    
    def _on_paper_double_clicked(self, item: QListWidgetItem):
        """双击试卷开始答题"""
        paper_id = item.data(Qt.UserRole)
        self.start_exam(paper_id)
    
    def _start_selected_exam(self):
        """开始选中的试卷"""
        item = self.paper_list.currentItem()
        if not item:
            QMessageBox.warning(self, "提示", "请选择一份试卷")
            return
        
        paper_id = item.data(Qt.UserRole)
        self.start_exam(paper_id)
    
    def start_exam(self, paper_id: str):
        """开始答题"""
        # 初始化考试
        result = self.exam_service.start_exam(paper_id)
        if not result:
            QMessageBox.warning(self, "错误", "无法开始答题，请检查试卷是否有效")
            return
        
        paper = self.exam_service.get_current_paper()
        self.questions = self.exam_service.get_all_questions()
        
        if not self.questions:
            QMessageBox.warning(self, "错误", "试卷中没有题目")
            return
        
        # 获取题库信息用于收藏
        if paper.source_banks:
            self.current_bank_id = paper.source_banks[0]
            # 尝试获取题库名称
            from services import BankService
            bank_service = BankService()
            bank = bank_service.get_bank(self.current_bank_id)
            self.current_bank_name = bank.name if bank else "未知题库"
        else:
            self.current_bank_id = "unknown"
            self.current_bank_name = "未知题库"
        
        # 重置状态
        self.current_index = 0
        self.answers = {}
        self.marked = set()
        
        # 更新UI
        self.paper_title_label.setText(paper.title)
        
        # 初始化答题卡
        self._init_answer_card()
        
        # 设置计时器
        if paper.time_limit > 0:
            self.remaining_seconds = paper.time_limit * 60
            self.timer.timeout.connect(self._on_timer_tick)
            self.timer.start(1000)
            self._update_timer_display()
        else:
            self.timer_label.setText("⏱️ 不限时")
        
        # 显示第一题
        self._show_question(0)
        
        # 切换到答题页面
        self.stack.setCurrentIndex(1)
    
    def _init_answer_card(self):
        """初始化答题卡"""
        # 清除旧按钮
        while self.card_grid.count():
            item = self.card_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 创建新按钮
        self.card_buttons = []
        cols = 5
        for i, q in enumerate(self.questions):
            btn = QPushButton(str(i + 1))
            btn.setFixedSize(40, 40)
            btn.setStyleSheet(self._get_card_btn_style(i))
            btn.clicked.connect(lambda checked, idx=i: self._jump_to_question(idx))
            
            row = i // cols
            col = i % cols
            self.card_grid.addWidget(btn, row, col)
            self.card_buttons.append(btn)
        
        self._update_stats()
    
    def _get_card_btn_style(self, index: int) -> str:
        """获取答题卡按钮样式"""
        base = """
            QPushButton {
                border-radius: 20px;
                font-weight: bold;
                font-size: 12px;
            }
        """
        
        q_id = self.questions[index].id if index < len(self.questions) else None
        is_answered = q_id in self.answers and self.answers[q_id] is not None
        is_marked = index in self.marked
        is_current = index == self.current_index
        
        if is_current:
            return base + "QPushButton { background-color: #1976D2; color: white; border: 2px solid #0D47A1; }"
        elif is_marked:
            return base + "QPushButton { background-color: #FF9800; color: white; }"
        elif is_answered:
            return base + "QPushButton { background-color: #4CAF50; color: white; }"
        else:
            return base + "QPushButton { background-color: #f0f0f0; color: #666; border: 1px solid #ddd; }"
    
    def _update_answer_card(self):
        """更新答题卡状态"""
        for i, btn in enumerate(self.card_buttons):
            btn.setStyleSheet(self._get_card_btn_style(i))
        self._update_stats()
    
    def _update_stats(self):
        """更新统计"""
        answered = sum(1 for q in self.questions if q.id in self.answers and self.answers[q.id] is not None)
        self.stats_label.setText(f"已答: {answered} / {len(self.questions)}")
    
    def _show_question(self, index: int):
        """显示指定题目"""
        if index < 0 or index >= len(self.questions):
            return
        
        self.current_index = index
        question = self.questions[index]
        
        # 清除旧内容
        while self.question_layout.count():
            item = self.question_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 创建题目卡片
        user_answer = self.answers.get(question.id)
        card = QuestionCard(question, index + 1, show_answer=False, user_answer=user_answer)
        card.answer_changed.connect(self._on_answer_changed)
        self.question_layout.addWidget(card)
        self.question_layout.addStretch()
        
        # 更新导航状态
        self.prev_btn.setEnabled(index > 0)
        self.next_btn.setEnabled(index < len(self.questions) - 1)
        self.progress_label.setText(f"{index + 1} / {len(self.questions)}")
        
        # 更新标记按钮
        self.mark_btn.setChecked(index in self.marked)
        
        # 更新收藏按钮状态
        self._update_favorite_button()
        
        # 更新答题卡
        self._update_answer_card()
    
    def _on_answer_changed(self, question_id: str, answer):
        """答案变更回调"""
        self.answers[question_id] = answer
        self.exam_service.submit_answer(question_id, answer)
        self._update_answer_card()
    
    def _prev_question(self):
        """上一题"""
        if self.current_index > 0:
            self._show_question(self.current_index - 1)
    
    def _next_question(self):
        """下一题"""
        if self.current_index < len(self.questions) - 1:
            self._show_question(self.current_index + 1)
    
    def _jump_to_question(self, index: int):
        """跳转到指定题目"""
        self._show_question(index)
    
    def _toggle_mark(self):
        """切换标记状态"""
        if self.current_index in self.marked:
            self.marked.discard(self.current_index)
        else:
            self.marked.add(self.current_index)
        self._update_answer_card()
    
    def _toggle_favorite(self):
        """切换收藏状态"""
        if self.current_index >= len(self.questions):
            return
        
        question = self.questions[self.current_index]
        
        if self.favorite_service.is_favorited(question.id):
            # 取消收藏
            if self.favorite_service.remove_favorite(question.id):
                QMessageBox.information(self, "提示", "已取消收藏")
        else:
            # 添加收藏
            success, msg = self.favorite_service.add_favorite(
                question, 
                self.current_bank_id, 
                self.current_bank_name
            )
            QMessageBox.information(self, "提示", msg)
        
        self._update_favorite_button()
    
    def _update_favorite_button(self):
        """更新收藏按钮状态"""
        if self.current_index >= len(self.questions):
            return
        
        question = self.questions[self.current_index]
        is_favorited = self.favorite_service.is_favorited(question.id)
        
        if is_favorited:
            self.fav_btn.setText("⭐ 已收藏")
            self.fav_btn.setStyleSheet("""
                QPushButton {
                    background-color: #fbbf24;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f59e0b;
                }
            """)
        else:
            self.fav_btn.setText("⭐ 收藏")
            self.fav_btn.setStyleSheet("""
                QPushButton {
                    background-color: #fef3c7;
                    color: #d97706;
                    border: 1px solid #fcd34d;
                    border-radius: 8px;
                    padding: 10px 16px;
                }
                QPushButton:hover {
                    background-color: #fde68a;
                }
            """)
    
    def _on_timer_tick(self):
        """计时器回调"""
        self.remaining_seconds -= 1
        self._update_timer_display()
        
        if self.remaining_seconds <= 0:
            self.timer.stop()
            self._timeout_submit()
    
    def _update_timer_display(self):
        """更新计时器显示"""
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        
        color = "#FF5722" if self.remaining_seconds < 300 else "#333"
        self.timer_label.setStyleSheet(f"color: {color};")
        self.timer_label.setText(f"⏱️ {minutes:02d}:{seconds:02d}")
    
    def _submit_exam(self):
        """交卷"""
        # 检查未答题目
        unanswered = [i+1 for i, q in enumerate(self.questions) 
                     if q.id not in self.answers or self.answers[q.id] is None]
        
        if unanswered:
            msg = f"还有 {len(unanswered)} 道题未作答（第{', '.join(map(str, unanswered[:5]))}{'...' if len(unanswered) > 5 else ''}题），确定要交卷吗？"
        else:
            msg = "确定要交卷吗？"
        
        reply = QMessageBox.question(
            self, "确认交卷", msg,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._do_submit()
    
    def _timeout_submit(self):
        """超时交卷"""
        QMessageBox.warning(self, "时间到", "答题时间已结束，系统将自动交卷。")
        self._do_submit(timeout=True)
    
    def _do_submit(self, timeout: bool = False):
        """执行交卷"""
        self.timer.stop()
        
        result = self.exam_service.finish_exam(timeout)
        if result:
            self.exam_finished.emit(result.id)
        
        # 返回选择页面
        self.stack.setCurrentIndex(0)
        self.refresh_papers()
    
    def has_active_exam(self) -> bool:
        """是否有进行中的答题"""
        return self.stack.currentIndex() == 1
