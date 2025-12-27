"""
试卷管理界面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QTextEdit, QMessageBox, QSpinBox,
    QListWidget, QListWidgetItem, QCheckBox, QGroupBox, QFrame,
    QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from services import BankService, PaperService
from services.paper_service import PaperGenerateConfig
from models import Paper


class PaperView(QWidget):
    """试卷管理视图"""
    
    start_exam_signal = Signal(str)  # paper_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.paper_service = PaperService()
        self.bank_service = BankService()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # 标题区域
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 20px;
            }
        """)
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(24, 20, 24, 20)
        
        # 标题
        title_label = QLabel("📝 试卷管理")
        title_label.setFont(QFont("Microsoft YaHei UI", 20, QFont.Bold))
        title_label.setStyleSheet("color: #1e293b; border: none; background: transparent;")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("创建、管理和预览您的试卷")
        subtitle_label.setStyleSheet("color: #64748b; font-size: 14px; border: none; background: transparent;")
        title_layout.addWidget(subtitle_label)
        
        layout.addWidget(title_frame)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        generate_btn = QPushButton("🎲 智能组卷")
        generate_btn.setObjectName("primaryButton")
        generate_btn.setFixedHeight(42)
        generate_btn.setMinimumWidth(120)
        generate_btn.clicked.connect(self._show_generate_dialog)
        btn_layout.addWidget(generate_btn)
        
        create_btn = QPushButton("+ 手动创建")
        create_btn.setObjectName("secondaryButton")
        create_btn.setFixedHeight(42)
        create_btn.setMinimumWidth(120)
        create_btn.clicked.connect(self._show_create_dialog)
        btn_layout.addWidget(create_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 试卷列表卡片
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
        
        # 试卷列表
        self.paper_table = QTableWidget()
        self.paper_table.setColumnCount(6)
        self.paper_table.setHorizontalHeaderLabels(["试卷名称", "题目数", "总分", "时限", "创建时间", "操作"])
        self.paper_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.paper_table.setColumnWidth(1, 80)
        self.paper_table.setColumnWidth(2, 80)
        self.paper_table.setColumnWidth(3, 100)
        self.paper_table.setColumnWidth(4, 160)
        self.paper_table.setColumnWidth(5, 240)
        self.paper_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.paper_table.verticalHeader().setVisible(False)
        self.paper_table.setShowGrid(False)
        self.paper_table.setAlternatingRowColors(True)
        self.paper_table.setStyleSheet("""
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
            QHeaderView::section:first {
                border-top-left-radius: 16px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 16px;
            }
        """)
        
        table_layout.addWidget(self.paper_table)
        layout.addWidget(table_frame, 1)
        
        # 设置表格行高
        self.paper_table.verticalHeader().setDefaultSectionSize(50)
    
    def refresh(self):
        """刷新数据"""
        self._load_papers()
    
    def _load_papers(self):
        """加载试卷列表"""
        self.paper_table.setRowCount(0)
        
        papers = self.paper_service.get_all_papers()
        for paper in papers:
            row = self.paper_table.rowCount()
            self.paper_table.insertRow(row)
            
            # 名称
            name_item = QTableWidgetItem(paper.title)
            name_item.setData(Qt.UserRole, paper.id)
            self.paper_table.setItem(row, 0, name_item)
            
            # 题目数
            count_item = QTableWidgetItem(str(len(paper.questions)))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.paper_table.setItem(row, 1, count_item)
            
            # 总分
            score_item = QTableWidgetItem(str(int(paper.total_score)))
            score_item.setTextAlignment(Qt.AlignCenter)
            self.paper_table.setItem(row, 2, score_item)
            
            # 时限
            time_text = f"{paper.time_limit}分钟" if paper.time_limit > 0 else "不限时"
            time_item = QTableWidgetItem(time_text)
            time_item.setTextAlignment(Qt.AlignCenter)
            self.paper_table.setItem(row, 3, time_item)
            
            # 创建时间
            self.paper_table.setItem(row, 4, QTableWidgetItem(paper.created_at))
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(4)
            
            start_btn = QPushButton("开始")
            start_btn.setFixedSize(54, 30)
            start_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #10b981, stop:1 #059669);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #059669, stop:1 #047857);
                }
            """)
            start_btn.clicked.connect(lambda checked, pid=paper.id: self._start_exam(pid))
            btn_layout.addWidget(start_btn)
            
            preview_btn = QPushButton("预览")
            preview_btn.setFixedSize(54, 30)
            preview_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f5f3ff;
                    color: #667eea;
                    border: 1px solid #667eea;
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #ede9fe;
                }
            """)
            preview_btn.clicked.connect(lambda checked, p=paper: self._preview_paper(p))
            btn_layout.addWidget(preview_btn)
            
            delete_btn = QPushButton("删除")
            delete_btn.setFixedSize(54, 30)
            delete_btn.setStyleSheet("""
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
            delete_btn.clicked.connect(lambda checked, pid=paper.id: self._delete_paper(pid))
            btn_layout.addWidget(delete_btn)
            
            self.paper_table.setCellWidget(row, 5, btn_widget)
    
    def _show_generate_dialog(self):
        """显示智能组卷对话框"""
        banks = self.bank_service.get_banks_summary()
        if not banks:
            QMessageBox.warning(self, "提示", "请先创建题库并添加题目")
            return
        
        dialog = PaperGenerateDialog(banks, self)
        if dialog.exec() == QDialog.Accepted:
            config = dialog.get_config()
            paper, error = self.paper_service.generate_paper(config)
            
            if error:
                QMessageBox.warning(self, "组卷失败", error)
            elif paper:
                QMessageBox.information(
                    self, "成功", 
                    f"试卷 '{paper.title}' 创建成功！\n共 {len(paper.questions)} 道题，总分 {int(paper.total_score)} 分"
                )
                self.refresh()
    
    def _show_create_dialog(self):
        """显示手动创建对话框"""
        dialog = PaperCreateDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            paper = self.paper_service.create_manual_paper(
                title=data['title'],
                description=data['description'],
                time_limit=data['time_limit']
            )
            QMessageBox.information(self, "成功", f"试卷 '{paper.title}' 创建成功！")
            self.refresh()
    
    def _start_exam(self, paper_id: str):
        """开始答题"""
        self.start_exam_signal.emit(paper_id)
    
    def _preview_paper(self, paper: Paper):
        """预览试卷"""
        questions = self.paper_service.get_paper_questions(paper.id)
        dialog = PaperPreviewDialog(paper, questions, self)
        dialog.exec()
    
    def _delete_paper(self, paper_id: str):
        """删除试卷"""
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这份试卷吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.paper_service.delete_paper(paper_id)
            self.refresh()


class PaperGenerateDialog(QDialog):
    """智能组卷对话框"""
    
    def __init__(self, banks: list, parent=None):
        super().__init__(parent)
        self.banks = banks
        self.setWindowTitle("🎲 智能组卷")
        self.setMinimumSize(550, 700)
        
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 16px;
                padding: 20px 16px 16px 16px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 16px;
                padding: 0 8px;
                color: #334155;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # 基本信息
        basic_group = QGroupBox("📋 基本信息")
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(12)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("请输入试卷名称")
        self.title_input.setText("随机测试卷")
        self.title_input.setMinimumHeight(38)
        basic_layout.addRow("试卷名称:", self.title_input)
        
        self.time_spin = QSpinBox()
        self.time_spin.setRange(0, 300)
        self.time_spin.setValue(60)
        self.time_spin.setSuffix(" 分钟")
        self.time_spin.setSpecialValueText("不限时")
        self.time_spin.setMinimumHeight(38)
        basic_layout.addRow("时间限制:", self.time_spin)
        
        layout.addWidget(basic_group)
        
        # 选择题库
        bank_group = QGroupBox("📚 选择题库")
        bank_layout = QVBoxLayout(bank_group)
        
        self.bank_list = QListWidget()
        self.bank_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: #f8fafc;
                padding: 4px;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-radius: 6px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background-color: #f1f5f9;
            }
        """)
        for bank in self.banks:
            item = QListWidgetItem(f"✓ {bank['name']} ({bank.get('question_count', 0)}题)")
            item.setData(Qt.UserRole, bank['id'])
            item.setCheckState(Qt.Unchecked)
            self.bank_list.addItem(item)
        
        bank_layout.addWidget(self.bank_list)
        layout.addWidget(bank_group)
        
        # 题目数量设置
        count_group = QGroupBox("📝 题目数量")
        count_layout = QFormLayout(count_group)
        count_layout.setSpacing(10)
        
        self.single_spin = QSpinBox()
        self.single_spin.setRange(0, 100)
        self.single_spin.setValue(10)
        self.single_spin.setMinimumHeight(36)
        count_layout.addRow("单选题:", self.single_spin)
        
        self.multiple_spin = QSpinBox()
        self.multiple_spin.setRange(0, 100)
        self.multiple_spin.setValue(5)
        self.multiple_spin.setMinimumHeight(36)
        count_layout.addRow("多选题:", self.multiple_spin)
        
        self.judge_spin = QSpinBox()
        self.judge_spin.setRange(0, 100)
        self.judge_spin.setValue(5)
        self.judge_spin.setMinimumHeight(36)
        count_layout.addRow("判断题:", self.judge_spin)
        
        layout.addWidget(count_group)
        
        # 分值设置
        score_group = QGroupBox("💯 分值设置")
        score_layout = QFormLayout(score_group)
        score_layout.setSpacing(10)
        
        self.single_score_spin = QSpinBox()
        self.single_score_spin.setRange(1, 20)
        self.single_score_spin.setValue(5)
        self.single_score_spin.setMinimumHeight(36)
        score_layout.addRow("单选题分值:", self.single_score_spin)
        
        self.multiple_score_spin = QSpinBox()
        self.multiple_score_spin.setRange(1, 20)
        self.multiple_score_spin.setValue(5)
        self.multiple_score_spin.setMinimumHeight(36)
        score_layout.addRow("多选题分值:", self.multiple_score_spin)
        
        self.judge_score_spin = QSpinBox()
        self.judge_score_spin.setRange(1, 20)
        self.judge_score_spin.setValue(2)
        self.judge_score_spin.setMinimumHeight(36)
        score_layout.addRow("判断题分值:", self.judge_score_spin)
        
        layout.addWidget(score_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        generate_btn = QPushButton("🎯 生成试卷")
        generate_btn.setFixedSize(120, 40)
        generate_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46a1);
            }
        """)
        generate_btn.clicked.connect(self._generate)
        btn_layout.addWidget(generate_btn)
        
        layout.addLayout(btn_layout)
    
    def _generate(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "提示", "请输入试卷名称")
            return
        
        # 检查是否选择了题库
        selected_banks = []
        for i in range(self.bank_list.count()):
            item = self.bank_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_banks.append(item.data(Qt.UserRole))
        
        if not selected_banks:
            QMessageBox.warning(self, "提示", "请至少选择一个题库")
            return
        
        # 检查题目数量
        total = self.single_spin.value() + self.multiple_spin.value() + self.judge_spin.value()
        if total == 0:
            QMessageBox.warning(self, "提示", "请设置题目数量")
            return
        
        self.accept()
    
    def get_config(self) -> PaperGenerateConfig:
        selected_banks = []
        for i in range(self.bank_list.count()):
            item = self.bank_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_banks.append(item.data(Qt.UserRole))
        
        return PaperGenerateConfig(
            title=self.title_input.text().strip(),
            time_limit=self.time_spin.value(),
            bank_ids=selected_banks,
            single_count=self.single_spin.value(),
            multiple_count=self.multiple_spin.value(),
            judge_count=self.judge_spin.value(),
            score_rules={
                "single": float(self.single_score_spin.value()),
                "multiple": float(self.multiple_score_spin.value()),
                "judge": float(self.judge_score_spin.value()),
                "fill": 5.0,
                "essay": 10.0
            }
        )


class PaperCreateDialog(QDialog):
    """手动创建试卷对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 创建试卷")
        self.setMinimumWidth(480)
        
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
            QLabel {
                color: #334155;
                font-size: 13px;
                font-weight: 500;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("请输入试卷名称")
        self.title_input.setMinimumHeight(40)
        self.title_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        form.addRow("名称:", self.title_input)
        
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        self.desc_input.setPlaceholderText("试卷描述（可选）")
        self.desc_input.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                font-size: 13px;
            }
            QTextEdit:focus {
                border-color: #667eea;
            }
        """)
        form.addRow("描述:", self.desc_input)
        
        self.time_spin = QSpinBox()
        self.time_spin.setRange(0, 300)
        self.time_spin.setValue(60)
        self.time_spin.setSuffix(" 分钟")
        self.time_spin.setSpecialValueText("不限时")
        self.time_spin.setMinimumHeight(40)
        self.time_spin.setStyleSheet("""
            QSpinBox {
                padding: 10px 14px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                font-size: 13px;
            }
            QSpinBox:focus {
                border-color: #667eea;
            }
        """)
        form.addRow("时间限制:", self.time_spin)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("✓ 创建")
        save_btn.setFixedSize(100, 40)
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46a1);
            }
        """)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _save(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "提示", "请输入试卷名称")
            return
        self.accept()
    
    def get_data(self) -> dict:
        return {
            'title': self.title_input.text().strip(),
            'description': self.desc_input.toPlainText().strip(),
            'time_limit': self.time_spin.value()
        }


class PaperPreviewDialog(QDialog):
    """试卷预览对话框"""
    
    def __init__(self, paper: Paper, questions: list, parent=None):
        super().__init__(parent)
        self.paper = paper
        self.questions = questions
        self.setWindowTitle(f"📄 预览 - {paper.title}")
        self.setMinimumSize(800, 700)
        
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # 试卷信息卡片
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 16px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(24, 20, 24, 20)
        
        title_label = QLabel(f"📋 {self.paper.title}")
        title_label.setFont(QFont("Microsoft YaHei UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: white; background: transparent;")
        info_layout.addWidget(title_label)
        
        time_text = f"{self.paper.time_limit}分钟" if self.paper.time_limit > 0 else "不限时"
        stats_label = QLabel(f"💯 总分: {int(self.paper.total_score)}分  |  📝 题目数: {len(self.questions)}  |  ⏱️ 时限: {time_text}")
        stats_label.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 14px; background: transparent;")
        info_layout.addWidget(stats_label)
        
        layout.addWidget(info_frame)
        
        # 题目列表卡片
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        content_layout_outer = QVBoxLayout(content_frame)
        content_layout_outer.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(12)
        
        from models import QuestionType
        
        for i, question in enumerate(self.questions):
            q_frame = QFrame()
            q_frame.setStyleSheet("""
                QFrame {
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                }
                QFrame:hover {
                    border-color: #667eea;
                    background-color: #f5f3ff;
                }
            """)
            q_layout = QVBoxLayout(q_frame)
            q_layout.setContentsMargins(16, 14, 16, 14)
            q_layout.setSpacing(8)
            
            # 题号和类型
            header_layout = QHBoxLayout()
            
            num_label = QLabel(f"第 {i+1} 题")
            num_label.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
            num_label.setStyleSheet("color: #1e293b; background: transparent;")
            header_layout.addWidget(num_label)
            
            type_badge = QLabel(QuestionType.get_display_name(question.type))
            type_badge.setStyleSheet("""
                background-color: #667eea;
                color: white;
                padding: 4px 12px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
            """)
            header_layout.addWidget(type_badge)
            
            # 难度显示
            difficulty = question.difficulty if hasattr(question, 'difficulty') else 3
            stars = "★" * difficulty + "☆" * (5 - difficulty)
            diff_label = QLabel(stars)
            diff_label.setStyleSheet("color: #f59e0b; font-size: 12px; background: transparent;")
            header_layout.addWidget(diff_label)
            
            header_layout.addStretch()
            q_layout.addLayout(header_layout)
            
            # 题目内容
            q_text = QLabel(question.question)
            q_text.setWordWrap(True)
            q_text.setStyleSheet("color: #334155; font-size: 14px; line-height: 1.6; background: transparent;")
            q_layout.addWidget(q_text)
            
            # 选项
            if question.options:
                options_frame = QFrame()
                options_frame.setStyleSheet("background-color: white; border-radius: 8px; border: none;")
                options_layout = QVBoxLayout(options_frame)
                options_layout.setContentsMargins(12, 8, 12, 8)
                options_layout.setSpacing(4)
                
                for opt in question.options:
                    opt_label = QLabel(f"  {opt}")
                    opt_label.setStyleSheet("color: #475569; font-size: 13px; background: transparent;")
                    options_layout.addWidget(opt_label)
                
                q_layout.addWidget(options_frame)
            
            content_layout.addWidget(q_frame)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        content_layout_outer.addWidget(scroll)
        layout.addWidget(content_frame, 1)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("✓ 关闭预览")
        close_btn.setFixedSize(120, 40)
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46a1);
            }
        """)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
