"""
题库管理界面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QTextEdit, QMessageBox, QMenu,
    QFileDialog, QSplitter, QFrame, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QAction

from services import BankService, ImportService
from models import Question, QuestionBank, QuestionType


class BankView(QWidget):
    """题库管理视图"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bank_service = BankService()
        self.import_service = ImportService()
        self.current_bank_id = None
        self._pending_questions = []  # 待导入的题目
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 标题
        title_label = QLabel("📁 题库管理")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        layout.addWidget(title_label)
        
        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：题库列表
        left_widget = self._create_bank_list_panel()
        splitter.addWidget(left_widget)
        
        # 右侧：题目列表
        right_widget = self._create_question_list_panel()
        splitter.addWidget(right_widget)
        
        splitter.setSizes([350, 850])
        layout.addWidget(splitter, 1)
    
    def _create_bank_list_panel(self) -> QWidget:
        """创建题库列表面板"""
        widget = QFrame()
        widget.setObjectName("bankListPanel")
        widget.setStyleSheet("""
            #bankListPanel {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 标题和按钮
        header = QHBoxLayout()
        header_label = QLabel("📚 题库列表")
        header_label.setFont(QFont("Microsoft YaHei UI", 14, QFont.Bold))
        header_label.setStyleSheet("color: #1e293b;")
        header.addWidget(header_label)
        header.addStretch()
        
        add_btn = QPushButton("+ 新建题库")
        add_btn.setObjectName("primaryButton")
        add_btn.setFixedHeight(36)
        add_btn.clicked.connect(self._show_create_bank_dialog)
        header.addWidget(add_btn)
        
        layout.addLayout(header)
        
        # 题库表格
        self.bank_table = QTableWidget()
        self.bank_table.setColumnCount(3)
        self.bank_table.setHorizontalHeaderLabels(["名称", "题目数", "操作"])
        self.bank_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.bank_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.bank_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.bank_table.setColumnWidth(1, 80)
        self.bank_table.setColumnWidth(2, 120)
        self.bank_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.bank_table.setSelectionMode(QTableWidget.SingleSelection)
        self.bank_table.verticalHeader().setVisible(False)
        self.bank_table.setShowGrid(False)
        self.bank_table.setAlternatingRowColors(True)
        self.bank_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 12px 8px;
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
        self.bank_table.cellClicked.connect(self._on_bank_selected)
        self.bank_table.verticalHeader().setDefaultSectionSize(45)
        
        layout.addWidget(self.bank_table)
        
        # 导入导出按钮
        btn_layout = QHBoxLayout()
        
        import_btn = QPushButton("📥 导入题库")
        import_btn.setObjectName("secondaryButton")
        import_btn.clicked.connect(self._import_bank)
        btn_layout.addWidget(import_btn)
        
        export_btn = QPushButton("📤 导出题库")
        export_btn.setObjectName("secondaryButton")
        export_btn.clicked.connect(self._export_bank)
        btn_layout.addWidget(export_btn)
        
        layout.addLayout(btn_layout)
        
        return widget
    
    def _create_question_list_panel(self) -> QWidget:
        """创建题目列表面板"""
        widget = QFrame()
        widget.setObjectName("questionListPanel")
        widget.setStyleSheet("""
            #questionListPanel {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 标题和按钮
        header = QHBoxLayout()
        self.question_header_label = QLabel("📝 题目列表")
        self.question_header_label.setFont(QFont("Microsoft YaHei UI", 14, QFont.Bold))
        self.question_header_label.setStyleSheet("color: #1e293b;")
        header.addWidget(self.question_header_label)
        header.addStretch()
        
        add_question_btn = QPushButton("+ 添加题目")
        add_question_btn.setObjectName("primaryButton")
        add_question_btn.setFixedHeight(36)
        add_question_btn.clicked.connect(self._show_create_question_dialog)
        header.addWidget(add_question_btn)
        
        import_question_btn = QPushButton("📥 批量导入")
        import_question_btn.setObjectName("secondaryButton")
        import_question_btn.setFixedHeight(36)
        import_question_btn.clicked.connect(self._import_questions)
        header.addWidget(import_question_btn)
        
        batch_delete_btn = QPushButton("🗑️ 批量删除")
        batch_delete_btn.setFixedHeight(36)
        batch_delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #fef2f2;
                color: #ef4444;
                border: 1px solid #fecaca;
                border-radius: 6px;
                padding: 0 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #fee2e2;
            }
        """)
        batch_delete_btn.clicked.connect(self._batch_delete_questions)
        header.addWidget(batch_delete_btn)
        
        layout.addLayout(header)
        
        # 题目表格
        self.question_table = QTableWidget()
        self.question_table.setColumnCount(6)
        self.question_table.setHorizontalHeaderLabels(["类型", "题目内容", "答案", "难度", "来源", "操作"])
        self.question_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.question_table.setColumnWidth(0, 80)
        self.question_table.setColumnWidth(2, 80)
        self.question_table.setColumnWidth(3, 80)
        self.question_table.setColumnWidth(4, 80)
        self.question_table.setColumnWidth(5, 120)
        self.question_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.question_table.setSelectionMode(QTableWidget.ExtendedSelection)  # 支持多选
        self.question_table.verticalHeader().setVisible(False)
        self.question_table.setShowGrid(False)
        self.question_table.setAlternatingRowColors(True)
        self.question_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 12px 8px;
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
        self.question_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.question_table.customContextMenuRequested.connect(self._show_question_context_menu)
        self.question_table.verticalHeader().setDefaultSectionSize(42)
        
        layout.addWidget(self.question_table)
        
        return widget
    
    def refresh(self):
        """刷新数据"""
        self._load_banks()
        if self.current_bank_id:
            self._load_questions(self.current_bank_id)
    
    def _load_banks(self):
        """加载题库列表"""
        self.bank_table.setRowCount(0)
        
        banks = self.bank_service.get_banks_summary()
        for bank in banks:
            row = self.bank_table.rowCount()
            self.bank_table.insertRow(row)
            
            # 名称
            name_item = QTableWidgetItem(bank['name'])
            name_item.setData(Qt.UserRole, bank['id'])
            self.bank_table.setItem(row, 0, name_item)
            
            # 题目数
            count_item = QTableWidgetItem(str(bank.get('question_count', 0)))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.bank_table.setItem(row, 1, count_item)
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            btn_layout.setSpacing(4)
            
            edit_btn = QPushButton("编辑")
            edit_btn.setFixedSize(52, 30)
            edit_btn.setStyleSheet("""
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
            edit_btn.clicked.connect(lambda checked, bid=bank['id']: self._edit_bank(bid))
            btn_layout.addWidget(edit_btn)
            
            del_btn = QPushButton("删除")
            del_btn.setFixedSize(52, 30)
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
            del_btn.clicked.connect(lambda checked, bid=bank['id']: self._delete_bank(bid))
            btn_layout.addWidget(del_btn)
            
            self.bank_table.setCellWidget(row, 2, btn_widget)
    
    def _load_questions(self, bank_id: str):
        """加载题目列表"""
        self.question_table.setRowCount(0)
        
        bank = self.bank_service.get_bank(bank_id)
        if not bank:
            return
        
        self.question_header_label.setText(f"题目列表 - {bank.name} ({len(bank.questions)}题)")
        
        for question in bank.questions:
            row = self.question_table.rowCount()
            self.question_table.insertRow(row)
            
            # 类型
            type_item = QTableWidgetItem(QuestionType.get_display_name(question.type))
            type_item.setData(Qt.UserRole, question.id)
            self.question_table.setItem(row, 0, type_item)
            
            # 题目内容（截断显示）
            content = question.question[:50] + "..." if len(question.question) > 50 else question.question
            self.question_table.setItem(row, 1, QTableWidgetItem(content))
            
            # 答案
            answer_text = self._format_answer(question.answer)
            self.question_table.setItem(row, 2, QTableWidgetItem(answer_text))
            
            # 难度
            diff_text = "★" * question.difficulty
            diff_item = QTableWidgetItem(diff_text)
            diff_item.setTextAlignment(Qt.AlignCenter)
            self.question_table.setItem(row, 3, diff_item)
            
            # 来源
            source_map = {"manual": "手动", "ai_generated": "AI生成", "imported": "导入"}
            source_text = source_map.get(question.source, question.source)
            self.question_table.setItem(row, 4, QTableWidgetItem(source_text))
            
            # 操作
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            btn_layout.setSpacing(4)
            
            edit_btn = QPushButton("编辑")
            edit_btn.setFixedSize(45, 26)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f5f3ff;
                    color: #667eea;
                    border: 1px solid #667eea;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #ede9fe;
                }
            """)
            edit_btn.clicked.connect(lambda checked, q=question: self._edit_question(q))
            btn_layout.addWidget(edit_btn)
            
            del_btn = QPushButton("删除")
            del_btn.setFixedSize(45, 26)
            del_btn.setStyleSheet("""
                QPushButton {
                    background-color: #fef2f2;
                    color: #ef4444;
                    border: 1px solid #fecaca;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #fee2e2;
                }
            """)
            del_btn.clicked.connect(lambda checked, qid=question.id: self._delete_question(qid))
            btn_layout.addWidget(del_btn)
            
            self.question_table.setCellWidget(row, 5, btn_widget)
    
    def _format_answer(self, answer) -> str:
        """格式化答案显示"""
        if isinstance(answer, bool):
            return "正确" if answer else "错误"
        if isinstance(answer, list):
            return ",".join(answer)
        return str(answer)
    
    def _on_bank_selected(self, row: int, column: int):
        """题库选择事件"""
        item = self.bank_table.item(row, 0)
        if item:
            bank_id = item.data(Qt.UserRole)
            self.current_bank_id = bank_id
            self._load_questions(bank_id)
    
    def _show_create_bank_dialog(self):
        """显示创建题库对话框"""
        dialog = BankEditDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self.bank_service.create_bank(
                name=data['name'],
                description=data['description'],
                subject=data['subject']
            )
            self.refresh()
    
    def _edit_bank(self, bank_id: str):
        """编辑题库"""
        bank = self.bank_service.get_bank(bank_id)
        if not bank:
            return
        
        dialog = BankEditDialog(self, bank)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            bank.name = data['name']
            bank.description = data['description']
            bank.subject = data['subject']
            self.bank_service.update_bank(bank)
            self.refresh()
    
    def _delete_bank(self, bank_id: str):
        """删除题库"""
        bank = self.bank_service.get_bank(bank_id)
        if not bank:
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除题库「{bank.name}」吗？\n\n该题库包含 {len(bank.questions)} 道题目，删除后无法恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.bank_service.delete_bank(bank_id):
                # 如果删除的是当前选中的题库，清空选择
                if self.current_bank_id == bank_id:
                    self.current_bank_id = None
                    self.question_table.setRowCount(0)
                    self.question_header_label.setText("题目列表")
                self.refresh()
                QMessageBox.information(self, "成功", f"题库「{bank.name}」已删除")
            else:
                QMessageBox.warning(self, "失败", "删除题库失败")
    
    def _show_create_question_dialog(self):
        """显示创建题目对话框"""
        if not self.current_bank_id:
            QMessageBox.warning(self, "提示", "请先选择一个题库")
            return
        
        dialog = QuestionEditDialog(self)
        if dialog.exec() == QDialog.Accepted:
            question = dialog.get_question()
            self.bank_service.add_question_to_bank(self.current_bank_id, question)
            self._load_questions(self.current_bank_id)
            self._load_banks()
    
    def _edit_question(self, question: Question):
        """编辑题目"""
        dialog = QuestionEditDialog(self, question)
        if dialog.exec() == QDialog.Accepted:
            updated = dialog.get_question()
            updated.id = question.id
            self.bank_service.update_question_in_bank(self.current_bank_id, updated)
            self._load_questions(self.current_bank_id)
    
    def _delete_question(self, question_id: str):
        """删除题目"""
        if not self.current_bank_id:
            QMessageBox.warning(self, "提示", "请先选择一个题库")
            return
            
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这道题目吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success = self.bank_service.delete_question_from_bank(self.current_bank_id, question_id)
            if success:
                self._load_questions(self.current_bank_id)
                self._load_banks()
            else:
                QMessageBox.warning(self, "失败", "删除题目失败")
    
    def _batch_delete_questions(self):
        """批量删除选中的题目"""
        if not self.current_bank_id:
            QMessageBox.warning(self, "提示", "请先选择一个题库")
            return
        
        selected_rows = self.question_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择要删除的题目")
            return
        
        # 收集选中的题目ID
        question_ids = []
        for index in selected_rows:
            item = self.question_table.item(index.row(), 0)
            if item:
                question_ids.append(item.data(Qt.UserRole))
        
        if not question_ids:
            return
        
        reply = QMessageBox.question(
            self, "确认批量删除", 
            f"确定要删除选中的 {len(question_ids)} 道题目吗？\n\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success_count = 0
            for qid in question_ids:
                if self.bank_service.delete_question_from_bank(self.current_bank_id, qid):
                    success_count += 1
            
            self._load_questions(self.current_bank_id)
            self._load_banks()
            QMessageBox.information(self, "完成", f"成功删除 {success_count} 道题目")
    
    def _show_question_context_menu(self, pos):
        """显示题目右键菜单"""
        menu = QMenu(self)
        edit_action = menu.addAction("编辑")
        delete_action = menu.addAction("删除")
        
        action = menu.exec(self.question_table.mapToGlobal(pos))
        
        row = self.question_table.currentRow()
        if row < 0:
            return
        
        item = self.question_table.item(row, 0)
        if not item:
            return
        
        question_id = item.data(Qt.UserRole)
        bank = self.bank_service.get_bank(self.current_bank_id)
        question = bank.get_question(question_id) if bank else None
        
        if action == edit_action and question:
            self._edit_question(question)
        elif action == delete_action:
            self._delete_question(question_id)
    
    def _import_bank(self):
        """导入题库"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择题库文件", "",
            "JSON文件 (*.json)"
        )
        if file_path:
            bank = self.bank_service.import_bank(file_path)
            if bank:
                QMessageBox.information(self, "成功", f"题库 '{bank.name}' 导入成功！")
                self.refresh()
            else:
                QMessageBox.warning(self, "失败", "导入题库失败，请检查文件格式")
    
    def _export_bank(self):
        """导出题库"""
        if not self.current_bank_id:
            QMessageBox.warning(self, "提示", "请先选择一个题库")
            return
        
        bank = self.bank_service.get_bank(self.current_bank_id)
        if not bank:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出题库", f"{bank.name}.json",
            "JSON文件 (*.json)"
        )
        if file_path:
            if self.bank_service.export_bank(self.current_bank_id, file_path):
                QMessageBox.information(self, "成功", "题库导出成功！")
            else:
                QMessageBox.warning(self, "失败", "导出题库失败")
    
    def _import_questions(self):
        """批量导入题目"""
        if not self.current_bank_id:
            QMessageBox.warning(self, "提示", "请先选择一个题库")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "",
            "所有支持格式 (*.json *.xlsx *.xls *.csv);;JSON文件 (*.json);;Excel文件 (*.xlsx *.xls);;CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
        
        # 根据文件类型选择导入方式
        if file_path.endswith('.json'):
            questions, error = self.import_service.import_from_json(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            questions, error = self.import_service.import_from_excel(file_path)
        elif file_path.endswith('.csv'):
            questions, error = self.import_service.import_from_csv(file_path)
        else:
            QMessageBox.warning(self, "错误", "不支持的文件格式")
            return
        
        if error:
            QMessageBox.warning(self, "导入失败", error)
            return
        
        # 添加到题库
        count = 0
        for q in questions:
            if self.bank_service.add_question_to_bank(self.current_bank_id, q):
                count += 1
        
        QMessageBox.information(self, "成功", f"成功导入 {count} 道题目！")
        self._load_questions(self.current_bank_id)
        self._load_banks()
    
    def import_questions(self, questions: list):
        """导入AI生成的题目"""
        if not questions:
            return
        
        self._pending_questions = questions
        
        if not self.current_bank_id:
            # 如果没有选中题库，提示选择
            banks = self.bank_service.get_banks_summary()
            if not banks:
                reply = QMessageBox.question(
                    self, "创建题库",
                    f"当前没有题库，是否创建新题库来存储 {len(questions)} 道题目？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self._show_create_bank_dialog()
                return
            
            QMessageBox.information(
                self, "选择题库",
                f"请在左侧选择一个题库，然后点击确认导入 {len(questions)} 道题目。"
            )
            return
        
        self._do_import_pending_questions()
    
    def _do_import_pending_questions(self):
        """执行导入待处理的题目"""
        if not self._pending_questions or not self.current_bank_id:
            return
        
        count = 0
        for q in self._pending_questions:
            if self.bank_service.add_question_to_bank(self.current_bank_id, q):
                count += 1
        
        self._pending_questions = []
        QMessageBox.information(self, "成功", f"成功导入 {count} 道AI生成的题目！")
        self._load_questions(self.current_bank_id)
        self._load_banks()


class BankEditDialog(QDialog):
    """题库编辑对话框"""
    
    def __init__(self, parent=None, bank: QuestionBank = None):
        super().__init__(parent)
        self.bank = bank
        self.setWindowTitle("编辑题库" if bank else "新建题库")
        self.setMinimumWidth(400)
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入题库名称")
        if self.bank:
            self.name_input.setText(self.bank.name)
        form.addRow("名称:", self.name_input)
        
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("如: 数学、英语、计算机基础")
        if self.bank:
            self.subject_input.setText(self.bank.subject)
        form.addRow("科目:", self.subject_input)
        
        self.desc_input = QTextEdit()
        self.desc_input.setMinimumHeight(80)
        self.desc_input.setMaximumHeight(120)
        self.desc_input.setPlaceholderText("请输入题库描述（可选）")
        if self.bank:
            self.desc_input.setText(self.bank.description)
        form.addRow("描述:", self.desc_input)
        
        layout.addLayout(form)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _save(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "提示", "请输入题库名称")
            return
        self.accept()
    
    def get_data(self) -> dict:
        return {
            'name': self.name_input.text().strip(),
            'subject': self.subject_input.text().strip(),
            'description': self.desc_input.toPlainText().strip()
        }


class QuestionEditDialog(QDialog):
    """题目编辑对话框"""
    
    def __init__(self, parent=None, question: Question = None):
        super().__init__(parent)
        self.question = question
        self.setWindowTitle("📝 编辑题目" if question else "📝 添加题目")
        self.setMinimumSize(650, 600)
        
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
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # 题目类型
        self.type_combo = QComboBox()
        self.type_combo.addItem("📌 单选题", "single")
        self.type_combo.addItem("☑️ 多选题", "multiple")
        self.type_combo.addItem("✓ 判断题", "judge")
        self.type_combo.addItem("📝 填空题", "fill")
        self.type_combo.setMinimumHeight(40)
        self.type_combo.setStyleSheet("""
            QComboBox {
                padding: 10px 14px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #667eea;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
        """)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        if self.question:
            index = self.type_combo.findData(self.question.type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        form.addRow("类型:", self.type_combo)
        
        # 题目内容
        self.question_input = QTextEdit()
        self.question_input.setMinimumHeight(90)
        self.question_input.setMaximumHeight(130)
        self.question_input.setPlaceholderText("请输入题目内容")
        self.question_input.setStyleSheet("""
            QTextEdit {
                padding: 12px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #667eea;
            }
        """)
        if self.question:
            self.question_input.setText(self.question.question)
        form.addRow("题目:", self.question_input)
        
        # 选项（单选/多选）
        self.options_widget = QFrame()
        self.options_widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        options_layout = QVBoxLayout(self.options_widget)
        options_layout.setContentsMargins(12, 12, 12, 12)
        options_layout.setSpacing(8)
        
        self.option_inputs = []
        for i, letter in enumerate(['A', 'B', 'C', 'D']):
            opt_layout = QHBoxLayout()
            opt_label = QLabel(f"{letter}.")
            opt_label.setFixedWidth(25)
            opt_label.setStyleSheet("font-weight: bold; color: #667eea; font-size: 14px;")
            opt_input = QLineEdit()
            opt_input.setPlaceholderText(f"选项{letter}")
            opt_input.setMinimumHeight(36)
            opt_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px 12px;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    background-color: #f8fafc;
                    font-size: 13px;
                }
                QLineEdit:focus {
                    border-color: #667eea;
                    background-color: white;
                }
            """)
            if self.question and i < len(self.question.options):
                # 移除前缀
                opt_text = self.question.options[i]
                if opt_text.startswith(f"{letter}.") or opt_text.startswith(f"{letter}、"):
                    opt_text = opt_text[2:].strip()
                opt_input.setText(opt_text)
            opt_layout.addWidget(opt_label)
            opt_layout.addWidget(opt_input)
            options_layout.addLayout(opt_layout)
            self.option_inputs.append(opt_input)
        
        form.addRow("选项:", self.options_widget)
        
        # 答案
        self.answer_input = QLineEdit()
        self.answer_input.setMinimumHeight(40)
        self.answer_input.setPlaceholderText("填字母如A")
        self.answer_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
                font-weight: bold;
                color: #10b981;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        if self.question:
            if isinstance(self.question.answer, bool):
                self.answer_input.setText("对" if self.question.answer else "错")
            elif isinstance(self.question.answer, list):
                self.answer_input.setText("".join(self.question.answer))
            else:
                self.answer_input.setText(str(self.question.answer))
        form.addRow("答案:", self.answer_input)
        
        # 解析
        self.explanation_input = QTextEdit()
        self.explanation_input.setMinimumHeight(70)
        self.explanation_input.setMaximumHeight(100)
        self.explanation_input.setPlaceholderText("答案解析（可选）")
        self.explanation_input.setStyleSheet("""
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
        if self.question:
            self.explanation_input.setText(self.question.explanation)
        form.addRow("解析:", self.explanation_input)
        
        # 难度
        self.difficulty_spin = QSpinBox()
        self.difficulty_spin.setRange(1, 5)
        self.difficulty_spin.setValue(self.question.difficulty if self.question else 3)
        self.difficulty_spin.setMinimumHeight(40)
        self.difficulty_spin.setStyleSheet("""
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
        form.addRow("难度:", self.difficulty_spin)
        
        # 标签
        self.tags_input = QLineEdit()
        self.tags_input.setMinimumHeight(40)
        self.tags_input.setPlaceholderText("多个标签用逗号分隔")
        self.tags_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        if self.question and self.question.tags:
            self.tags_input.setText(",".join(self.question.tags))
        form.addRow("标签:", self.tags_input)
        
        layout.addLayout(form)
        
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
        
        save_btn = QPushButton("💾 保存")
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
        
        # 初始化显示
        self._on_type_changed()
    
    def _on_type_changed(self):
        """题目类型变更"""
        q_type = self.type_combo.currentData()
        show_options = q_type in ['single', 'multiple']
        self.options_widget.setVisible(show_options)
        
        if q_type == 'judge':
            self.answer_input.setPlaceholderText("填'对'或'错'")
        elif q_type == 'multiple':
            self.answer_input.setPlaceholderText("填多个字母如ABC")
        else:
            self.answer_input.setPlaceholderText("填字母如A")
    
    def _save(self):
        if not self.question_input.toPlainText().strip():
            QMessageBox.warning(self, "提示", "请输入题目内容")
            return
        
        if not self.answer_input.text().strip():
            QMessageBox.warning(self, "提示", "请输入正确答案")
            return
        
        self.accept()
    
    def get_question(self) -> Question:
        """获取题目数据"""
        q_type = self.type_combo.currentData()
        
        # 处理选项
        options = []
        if q_type in ['single', 'multiple']:
            for i, inp in enumerate(self.option_inputs):
                text = inp.text().strip()
                if text:
                    letter = chr(ord('A') + i)
                    options.append(f"{letter}. {text}")
        
        # 处理答案
        answer_text = self.answer_input.text().strip()
        if q_type == 'judge':
            answer = answer_text in ['对', '正确', 'True', 'true', '1']
        elif q_type == 'multiple':
            answer = list(answer_text.upper().replace(',', '').replace('，', ''))
        else:
            answer = answer_text.upper()
        
        # 处理标签
        tags_text = self.tags_input.text().strip()
        tags = [t.strip() for t in tags_text.split(',') if t.strip()] if tags_text else []
        
        return Question(
            type=q_type,
            question=self.question_input.toPlainText().strip(),
            options=options,
            answer=answer,
            explanation=self.explanation_input.toPlainText().strip(),
            difficulty=self.difficulty_spin.value(),
            tags=tags,
            source='manual'
        )
