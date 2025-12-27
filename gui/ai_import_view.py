"""
AI导入界面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QFileDialog, QMessageBox, QProgressBar,
    QTabWidget, QScrollArea, QGroupBox, QSpinBox, QCheckBox,
    QDialog, QComboBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QPixmap

from services import AIService, BankService
from models import Question


class AIWorker(QThread):
    """AI处理工作线程"""
    
    finished = Signal(list, str)  # questions, error
    
    def __init__(self, ai_service: AIService, mode: str, data):
        super().__init__()
        self.ai_service = ai_service
        self.mode = mode
        self.data = data
    
    def run(self):
        try:
            if self.mode == 'parse_text':
                questions, error = self.ai_service.parse_questions_from_text(self.data)
            elif self.mode == 'parse_image':
                questions, error = self.ai_service.parse_questions_from_image(self.data)
            elif self.mode == 'parse_file':
                questions, error = self.ai_service.parse_questions_from_file(self.data)
            elif self.mode == 'generate':
                questions, error = self.ai_service.generate_questions(**self.data)
            else:
                questions, error = [], "未知的处理模式"
            
            self.finished.emit(questions, error)
        except Exception as e:
            self.finished.emit([], str(e))


class AIImportView(QWidget):
    """AI导入视图"""
    
    questions_generated = Signal(list)  # 生成的题目列表
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ai_service = AIService()
        self.worker = None
        self.generated_questions = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 标题
        title_label = QLabel("🤖 AI智能导入")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        layout.addWidget(title_label)
        
        # 选项卡
        tab_widget = QTabWidget()
        
        # 文件导入
        file_tab = self._create_file_tab()
        tab_widget.addTab(file_tab, "📁 文件导入")
        
        # 文字识别
        text_tab = self._create_text_tab()
        tab_widget.addTab(text_tab, "📝 文字解析")
        
        # 图片识别
        image_tab = self._create_image_tab()
        tab_widget.addTab(image_tab, "🖼️ 图片识别")
        
        # 智能生成
        generate_tab = self._create_generate_tab()
        tab_widget.addTab(generate_tab, "✨ 智能生成")
        
        layout.addWidget(tab_widget)
        
        # 结果区域
        result_group = QGroupBox("生成结果")
        result_layout = QVBoxLayout(result_group)
        
        self.result_scroll = QScrollArea()
        self.result_scroll.setWidgetResizable(True)
        self.result_scroll.setMinimumHeight(200)
        
        self.result_container = QWidget()
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setContentsMargins(10, 10, 10, 10)
        
        self.result_placeholder = QLabel("AI生成的题目将显示在这里")
        self.result_placeholder.setStyleSheet("color: #999; padding: 20px;")
        self.result_placeholder.setAlignment(Qt.AlignCenter)
        self.result_layout.addWidget(self.result_placeholder)
        
        self.result_scroll.setWidget(self.result_container)
        result_layout.addWidget(self.result_scroll)
        
        # 导入按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.import_btn = QPushButton("📥 导入到题库")
        self.import_btn.setObjectName("primaryButton")
        self.import_btn.setEnabled(False)
        self.import_btn.clicked.connect(self._import_questions)
        btn_layout.addWidget(self.import_btn)
        
        result_layout.addLayout(btn_layout)
        layout.addWidget(result_group)
    
    def _create_file_tab(self) -> QWidget:
        """创建文件导入标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 说明
        tip_label = QLabel("支持导入 Word(.docx)、Excel(.xlsx)、文本(.txt)、图片(.png/.jpg) 等格式的题目文件")
        tip_label.setStyleSheet("color: #666;")
        tip_label.setWordWrap(True)
        layout.addWidget(tip_label)
        
        # 文件选择区域
        self.file_frame = QFrame()
        self.file_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 2px dashed #ddd;
                border-radius: 8px;
                min-height: 150px;
            }
        """)
        
        file_layout = QVBoxLayout(self.file_frame)
        file_layout.setAlignment(Qt.AlignCenter)
        
        self.file_icon_label = QLabel("📂")
        self.file_icon_label.setStyleSheet("font-size: 48px;")
        self.file_icon_label.setAlignment(Qt.AlignCenter)
        file_layout.addWidget(self.file_icon_label)
        
        self.file_name_label = QLabel("点击下方按钮选择文件")
        self.file_name_label.setAlignment(Qt.AlignCenter)
        self.file_name_label.setStyleSheet("color: #999; font-size: 14px;")
        file_layout.addWidget(self.file_name_label)
        
        self.file_info_label = QLabel("")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        self.file_info_label.setStyleSheet("color: #666; font-size: 12px;")
        file_layout.addWidget(self.file_info_label)
        
        layout.addWidget(self.file_frame)
        
        # 支持的格式说明
        formats_label = QLabel("支持格式：Word(.doc, .docx) | Excel(.xls, .xlsx) | 文本(.txt) | 图片(.png, .jpg, .jpeg)")
        formats_label.setStyleSheet("color: #888; font-size: 12px; margin-top: 8px;")
        layout.addWidget(formats_label)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        select_file_btn = QPushButton("📁 选择文件")
        select_file_btn.setObjectName("secondaryButton")
        select_file_btn.clicked.connect(self._select_file)
        btn_layout.addWidget(select_file_btn)
        
        btn_layout.addStretch()
        
        self.file_parse_btn = QPushButton("🔍 解析题目")
        self.file_parse_btn.setObjectName("primaryButton")
        self.file_parse_btn.setEnabled(False)
        self.file_parse_btn.clicked.connect(self._parse_file)
        btn_layout.addWidget(self.file_parse_btn)
        
        layout.addLayout(btn_layout)
        
        self.selected_file_path = None
        
        return widget
    
    def _create_text_tab(self) -> QWidget:
        """创建文字解析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 说明
        tip_label = QLabel("粘贴包含题目的文本内容，AI将自动识别并转换为标准格式")
        tip_label.setStyleSheet("color: #666;")
        layout.addWidget(tip_label)
        
        # 文本输入框
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "请粘贴题目内容，例如：\n\n"
            "1. Python中哪个关键字用于定义函数？\n"
            "A. func\n"
            "B. def\n"
            "C. function\n"
            "D. define\n"
            "答案：B\n\n"
            "支持多道题目，AI会自动识别题目类型和答案..."
        )
        self.text_input.setMinimumHeight(250)
        self.text_input.setMinimumWidth(400)
        layout.addWidget(self.text_input, 1)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.text_parse_btn = QPushButton("🔍 解析题目")
        self.text_parse_btn.setObjectName("primaryButton")
        self.text_parse_btn.clicked.connect(self._parse_text)
        btn_layout.addWidget(self.text_parse_btn)
        
        layout.addLayout(btn_layout)
        
        return widget
    
    def _create_image_tab(self) -> QWidget:
        """创建图片识别标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 说明
        tip_label = QLabel("上传包含题目的图片（试卷照片、教材截图等），AI将识别并转换为标准格式")
        tip_label.setStyleSheet("color: #666;")
        layout.addWidget(tip_label)
        
        # 图片预览区
        self.image_frame = QFrame()
        self.image_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 2px dashed #ddd;
                border-radius: 8px;
                min-height: 200px;
            }
        """)
        
        image_layout = QVBoxLayout(self.image_frame)
        
        self.image_label = QLabel("点击下方按钮选择图片")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("color: #999;")
        image_layout.addWidget(self.image_label)
        
        layout.addWidget(self.image_frame)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        select_btn = QPushButton("📁 选择图片")
        select_btn.setObjectName("secondaryButton")
        select_btn.clicked.connect(self._select_image)
        btn_layout.addWidget(select_btn)
        
        btn_layout.addStretch()
        
        self.image_parse_btn = QPushButton("🔍 识别题目")
        self.image_parse_btn.setObjectName("primaryButton")
        self.image_parse_btn.setEnabled(False)
        self.image_parse_btn.clicked.connect(self._parse_image)
        btn_layout.addWidget(self.image_parse_btn)
        
        layout.addLayout(btn_layout)
        
        self.selected_image_path = None
        
        return widget
    
    def _create_generate_tab(self) -> QWidget:
        """创建智能生成标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 说明
        tip_label = QLabel("输入知识点或主题，AI将自动生成相关题目")
        tip_label.setStyleSheet("color: #666;")
        layout.addWidget(tip_label)
        
        # 主题输入
        self.topic_input = QTextEdit()
        self.topic_input.setPlaceholderText(
            "请输入知识点或主题，例如：\n\n"
            "Python基础语法：包括变量、数据类型、运算符、条件语句、循环语句等内容..."
        )
        self.topic_input.setMaximumHeight(100)
        layout.addWidget(self.topic_input)
        
        # 参数设置
        params_layout = QHBoxLayout()
        
        params_layout.addWidget(QLabel("生成数量:"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 50)
        self.count_spin.setValue(5)
        params_layout.addWidget(self.count_spin)
        
        params_layout.addWidget(QLabel("  难度范围:"))
        self.min_diff_spin = QSpinBox()
        self.min_diff_spin.setRange(1, 5)
        self.min_diff_spin.setValue(2)
        params_layout.addWidget(self.min_diff_spin)
        
        params_layout.addWidget(QLabel("-"))
        self.max_diff_spin = QSpinBox()
        self.max_diff_spin.setRange(1, 5)
        self.max_diff_spin.setValue(4)
        params_layout.addWidget(self.max_diff_spin)
        
        params_layout.addStretch()
        layout.addLayout(params_layout)
        
        # 题型选择
        types_layout = QHBoxLayout()
        types_layout.addWidget(QLabel("题目类型:"))
        
        # 复选框样式：使用对勾表示选中
        checkbox_style = """
            QCheckBox {
                spacing: 8px;
                font-size: 14px;
                color: #333;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #667eea;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #667eea;
                border-color: #667eea;
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjMiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlsaW5lIHBvaW50cz0iMjAgNiA5IDE3IDQgMTIiPjwvcG9seWxpbmU+PC9zdmc+);
            }
            QCheckBox::indicator:hover {
                border-color: #5a67d8;
            }
        """
        
        self.single_check = QCheckBox("单选题")
        self.single_check.setChecked(True)
        self.single_check.setStyleSheet(checkbox_style)
        types_layout.addWidget(self.single_check)
        
        self.multiple_check = QCheckBox("多选题")
        self.multiple_check.setChecked(True)
        self.multiple_check.setStyleSheet(checkbox_style)
        types_layout.addWidget(self.multiple_check)
        
        self.judge_check = QCheckBox("判断题")
        self.judge_check.setChecked(True)
        self.judge_check.setStyleSheet(checkbox_style)
        types_layout.addWidget(self.judge_check)
        
        types_layout.addStretch()
        layout.addLayout(types_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.generate_btn = QPushButton("✨ 生成题目")
        self.generate_btn.setObjectName("primaryButton")
        self.generate_btn.clicked.connect(self._generate_questions)
        btn_layout.addWidget(self.generate_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        return widget
    
    def _parse_text(self):
        """解析文本"""
        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "请输入题目内容")
            return
        
        self._start_ai_task('parse_text', text)
    
    def _select_file(self):
        """选择文件"""
        file_filter = self.ai_service.get_file_filter_string()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择题目文件", "",
            file_filter
        )
        
        if file_path:
            self.selected_file_path = file_path
            
            # 获取文件信息
            from pathlib import Path
            import os
            path = Path(file_path)
            file_size = os.path.getsize(file_path)
            
            # 格式化文件大小
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            # 根据文件类型显示不同图标
            suffix = path.suffix.lower()
            if suffix in ['.doc', '.docx']:
                icon = "📄"
            elif suffix in ['.xls', '.xlsx']:
                icon = "📊"
            elif suffix in ['.txt']:
                icon = "📝"
            elif suffix in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                icon = "🖼️"
            else:
                icon = "📁"
            
            self.file_icon_label.setText(icon)
            self.file_name_label.setText(path.name)
            self.file_name_label.setStyleSheet("color: #333; font-size: 14px; font-weight: bold;")
            self.file_info_label.setText(f"大小: {size_str}")
            
            self.file_parse_btn.setEnabled(True)
    
    def _parse_file(self):
        """解析文件"""
        if not self.selected_file_path:
            QMessageBox.warning(self, "提示", "请先选择文件")
            return
        
        self._start_ai_task('parse_file', self.selected_file_path)
    
    def _select_image(self):
        """选择图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.gif *.webp)"
        )
        
        if file_path:
            self.selected_image_path = file_path
            
            # 显示预览
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled)
            else:
                self.image_label.setText(file_path)
            
            self.image_parse_btn.setEnabled(True)
    
    def _parse_image(self):
        """解析图片"""
        if not self.selected_image_path:
            QMessageBox.warning(self, "提示", "请先选择图片")
            return
        
        self._start_ai_task('parse_image', self.selected_image_path)
    
    def _generate_questions(self):
        """生成题目"""
        topic = self.topic_input.toPlainText().strip()
        if not topic:
            QMessageBox.warning(self, "提示", "请输入知识点或主题")
            return
        
        # 收集题型
        types = []
        if self.single_check.isChecked():
            types.append('single')
        if self.multiple_check.isChecked():
            types.append('multiple')
        if self.judge_check.isChecked():
            types.append('judge')
        
        if not types:
            QMessageBox.warning(self, "提示", "请至少选择一种题目类型")
            return
        
        data = {
            'topic': topic,
            'count': self.count_spin.value(),
            'types': types,
            'min_difficulty': self.min_diff_spin.value(),
            'max_difficulty': self.max_diff_spin.value()
        }
        
        self._start_ai_task('generate', data)
    
    def _start_ai_task(self, mode: str, data):
        """启动AI任务"""
        # 检查API配置
        from config import config
        if not config.ai_config.api_key:
            QMessageBox.warning(
                self, "配置缺失", 
                "请先在系统设置中配置AI API密钥"
            )
            return
        
        # 禁用按钮
        self._set_buttons_enabled(False)
        
        # 清除旧结果
        self._clear_results()
        
        # 显示加载提示
        self.result_placeholder.setText("🔄 AI正在处理中，请稍候...")
        self.result_placeholder.show()
        
        # 启动工作线程
        self.worker = AIWorker(self.ai_service, mode, data)
        self.worker.finished.connect(self._on_ai_finished)
        self.worker.start()
    
    def _on_ai_finished(self, questions: list, error: str):
        """AI处理完成"""
        self._set_buttons_enabled(True)
        
        if error:
            self.result_placeholder.setText(f"❌ 处理失败: {error}")
            QMessageBox.warning(self, "处理失败", error)
            return
        
        if not questions:
            self.result_placeholder.setText("未能识别出任何题目")
            return
        
        self.generated_questions = questions
        self._display_results(questions)
        self.import_btn.setEnabled(True)
    
    def _display_results(self, questions: list):
        """显示结果"""
        # 隐藏占位符
        self.result_placeholder.hide()
        
        # 添加题目预览
        from models import QuestionType
        
        for i, q in enumerate(questions):
            q_frame = QFrame()
            q_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 10px;
                    margin: 5px;
                }
            """)
            q_layout = QVBoxLayout(q_frame)
            
            # 题号和类型
            header = QLabel(f"第{i+1}题 ({QuestionType.get_display_name(q.type)})")
            header.setStyleSheet("font-weight: bold; color: #1976D2;")
            q_layout.addWidget(header)
            
            # 题目内容
            q_text = QLabel(q.question)
            q_text.setWordWrap(True)
            q_layout.addWidget(q_text)
            
            # 选项
            if q.options:
                for opt in q.options:
                    opt_label = QLabel(f"  {opt}")
                    q_layout.addWidget(opt_label)
            
            # 答案
            answer_text = self._format_answer(q.answer)
            answer_label = QLabel(f"答案: {answer_text}")
            answer_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            q_layout.addWidget(answer_label)
            
            self.result_layout.addWidget(q_frame)
        
        # 添加统计
        stats_label = QLabel(f"✅ 共识别/生成 {len(questions)} 道题目")
        stats_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 10px;")
        self.result_layout.addWidget(stats_label)
    
    def _format_answer(self, answer) -> str:
        """格式化答案"""
        if isinstance(answer, bool):
            return "正确" if answer else "错误"
        if isinstance(answer, list):
            return ", ".join(answer)
        return str(answer)
    
    def _clear_results(self):
        """清除结果"""
        while self.result_layout.count() > 1:
            item = self.result_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
        
        self.result_placeholder.show()
        self.generated_questions = []
        self.import_btn.setEnabled(False)
    
    def _set_buttons_enabled(self, enabled: bool):
        """设置按钮状态"""
        self.text_parse_btn.setEnabled(enabled)
        self.image_parse_btn.setEnabled(enabled and self.selected_image_path is not None)
        self.file_parse_btn.setEnabled(enabled and self.selected_file_path is not None)
        self.generate_btn.setEnabled(enabled)
    
    def _import_questions(self):
        """导入题目到题库"""
        if not self.generated_questions:
            return
        
        # 弹出题库选择对话框
        dialog = BankSelectDialog(self, len(self.generated_questions))
        if dialog.exec() == QDialog.Accepted:
            bank_id = dialog.get_selected_bank_id()
            if bank_id:
                # 直接导入到选中的题库
                bank_service = BankService()
                count = 0
                for q in self.generated_questions:
                    q.source = 'ai_generated'
                    if bank_service.add_question_to_bank(bank_id, q):
                        count += 1
                
                bank = bank_service.get_bank(bank_id)
                bank_name = bank.name if bank else "题库"
                
                self._clear_results()
                QMessageBox.information(
                    self, "导入成功", 
                    f"成功将 {count} 道题目导入到「{bank_name}」！"
                )
                
                # 发送信号通知刷新题库视图
                self.questions_generated.emit([])


class BankSelectDialog(QDialog):
    """题库选择对话框"""
    
    def __init__(self, parent=None, question_count: int = 0):
        super().__init__(parent)
        self.bank_service = BankService()
        self.selected_bank_id = None
        self.question_count = question_count
        
        self.setWindowTitle("选择目标题库")
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 提示信息
        tip_label = QLabel(f"请选择要导入 {self.question_count} 道题目的目标题库：")
        tip_label.setStyleSheet("font-size: 14px; color: #333;")
        layout.addWidget(tip_label)
        
        # 题库选择下拉框
        self.bank_combo = QComboBox()
        self.bank_combo.setMinimumHeight(36)
        self.bank_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #1976D2;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
        """)
        
        # 加载题库列表
        banks = self.bank_service.get_banks_summary()
        if not banks:
            self.bank_combo.addItem("暂无题库，请先创建题库", None)
            self.bank_combo.setEnabled(False)
        else:
            for bank in banks:
                display_text = f"{bank['name']} ({bank.get('question_count', 0)}题)"
                self.bank_combo.addItem(display_text, bank['id'])
        
        layout.addWidget(self.bank_combo)
        
        # 创建新题库提示
        create_tip = QLabel("💡 如需创建新题库，请先前往「题库管理」")
        create_tip.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(create_tip)
        
        layout.addStretch()
        
        # 按钮
        button_box = QDialogButtonBox()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedHeight(36)
        button_box.addButton(cancel_btn, QDialogButtonBox.RejectRole)
        
        self.confirm_btn = QPushButton("确认导入")
        self.confirm_btn.setObjectName("primaryButton")
        self.confirm_btn.setFixedHeight(36)
        self.confirm_btn.setEnabled(len(banks) > 0)
        button_box.addButton(self.confirm_btn, QDialogButtonBox.AcceptRole)
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def get_selected_bank_id(self) -> str:
        """获取选中的题库ID"""
        return self.bank_combo.currentData()
