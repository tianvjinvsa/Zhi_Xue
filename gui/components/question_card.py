"""
题目卡片组件
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from models import Question, QuestionType
from .option_group import OptionGroup


class QuestionCard(QWidget):
    """题目卡片组件"""
    
    answer_changed = Signal(str, object)  # question_id, answer
    
    def __init__(self, question: Question, index: int = 1, 
                 show_answer: bool = False, user_answer=None, parent=None):
        super().__init__(parent)
        self.question = question
        self.index = index
        self.show_answer = show_answer
        self.user_answer = user_answer
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 题目框架
        self.frame = QFrame()
        self.frame.setObjectName("questionCard")
        self.frame.setStyleSheet("""
            QFrame#questionCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
            }
        """)
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(24, 20, 24, 20)
        frame_layout.setSpacing(16)
        
        # 题目头部
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # 题号标签
        index_label = QLabel(f"{self.index}")
        index_label.setFixedSize(36, 36)
        index_label.setAlignment(Qt.AlignCenter)
        index_label.setFont(QFont("Microsoft YaHei UI", 14, QFont.Bold))
        index_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667eea, stop:1 #764ba2);
            color: white;
            border-radius: 18px;
        """)
        header_layout.addWidget(index_label)
        
        # 类型标签
        type_display = QuestionType.get_display_name(self.question.type)
        type_label = QLabel(type_display)
        type_label.setFont(QFont("Microsoft YaHei UI", 12))
        type_label.setStyleSheet("""
            color: #667eea;
            background-color: #f5f3ff;
            padding: 6px 14px;
            border-radius: 12px;
            font-weight: 500;
        """)
        header_layout.addWidget(type_label)
        
        header_layout.addStretch()
        
        # 难度显示
        difficulty_text = "★" * self.question.difficulty + "☆" * (5 - self.question.difficulty)
        difficulty_label = QLabel(f"难度 {difficulty_text}")
        difficulty_label.setStyleSheet("""
            color: #f59e0b;
            background-color: #fef3c7;
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 12px;
        """)
        header_layout.addWidget(difficulty_label)
        
        frame_layout.addLayout(header_layout)
        
        # 题目内容
        question_label = QLabel(self.question.question)
        question_label.setFont(QFont("Microsoft YaHei UI", 14))
        question_label.setWordWrap(True)
        question_label.setStyleSheet("""
            color: #1e293b; 
            line-height: 1.8;
            padding: 12px 0;
        """)
        frame_layout.addWidget(question_label)
        
        # 选项区域
        if self.question.type in [QuestionType.SINGLE.value, QuestionType.MULTIPLE.value]:
            self.option_group = OptionGroup(
                options=self.question.options,
                multiple=(self.question.type == QuestionType.MULTIPLE.value),
                selected=self.user_answer,
                correct_answer=self.question.answer if self.show_answer else None,
                readonly=self.show_answer
            )
            self.option_group.selection_changed.connect(self._on_answer_changed)
            frame_layout.addWidget(self.option_group)
        
        elif self.question.type == QuestionType.JUDGE.value:
            self.option_group = OptionGroup(
                options=["A. 正确", "B. 错误"],
                multiple=False,
                selected=self._judge_answer_to_option(self.user_answer),
                correct_answer=self._judge_answer_to_option(self.question.answer) if self.show_answer else None,
                readonly=self.show_answer
            )
            self.option_group.selection_changed.connect(self._on_judge_answer_changed)
            frame_layout.addWidget(self.option_group)
        
        # 显示答案区域
        if self.show_answer:
            self._add_answer_section(frame_layout)
        
        layout.addWidget(self.frame)
    
    def _judge_answer_to_option(self, answer) -> str:
        """将判断题答案转换为选项"""
        if answer is None:
            return ""
        if isinstance(answer, bool):
            return "A" if answer else "B"
        if isinstance(answer, str):
            return "A" if answer.upper() in ['A', 'TRUE', '对', '正确'] else "B"
        return ""
    
    def _option_to_judge_answer(self, option: str) -> bool:
        """将选项转换为判断题答案"""
        return option == "A"
    
    def _on_answer_changed(self, answer):
        """选项变更回调"""
        self.user_answer = answer
        self.answer_changed.emit(self.question.id, answer)
    
    def _on_judge_answer_changed(self, answer):
        """判断题答案变更回调"""
        judge_answer = self._option_to_judge_answer(answer)
        self.user_answer = judge_answer
        self.answer_changed.emit(self.question.id, judge_answer)
    
    def _add_answer_section(self, layout: QVBoxLayout):
        """添加答案展示区域"""
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #e2e8f0; margin: 8px 0;")
        layout.addWidget(line)
        
        # 答案容器
        answer_container = QFrame()
        answer_container.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        answer_layout = QVBoxLayout(answer_container)
        answer_layout.setContentsMargins(16, 12, 16, 12)
        answer_layout.setSpacing(10)
        
        # 正确答案
        answer_text = self._format_answer(self.question.answer)
        answer_label = QLabel(f"✅ 正确答案: {answer_text}")
        answer_label.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        answer_label.setStyleSheet("color: #059669;")
        answer_layout.addWidget(answer_label)
        
        # 用户答案
        if self.user_answer is not None:
            user_text = self._format_answer(self.user_answer)
            is_correct = self._check_correct()
            color = "#059669" if is_correct else "#dc2626"
            icon = "✅" if is_correct else "❌"
            bg_color = "#ecfdf5" if is_correct else "#fef2f2"
            user_label = QLabel(f"{icon} 你的答案: {user_text}")
            user_label.setFont(QFont("Microsoft YaHei UI", 12))
            user_label.setStyleSheet(f"color: {color}; background-color: {bg_color}; padding: 8px 12px; border-radius: 8px;")
            answer_layout.addWidget(user_label)
        
        # 答案解析
        if self.question.explanation:
            exp_frame = QFrame()
            exp_frame.setStyleSheet("""
                QFrame {
                    background-color: #f0f9ff;
                    border-left: 4px solid #0ea5e9;
                    border-radius: 8px;
                }
            """)
            exp_frame_layout = QVBoxLayout(exp_frame)
            exp_frame_layout.setContentsMargins(12, 10, 12, 10)
            
            exp_title = QLabel("💡 答案解析")
            exp_title.setFont(QFont("Microsoft YaHei UI", 11, QFont.Bold))
            exp_title.setStyleSheet("color: #0369a1;")
            exp_frame_layout.addWidget(exp_title)
            
            exp_label = QLabel(self.question.explanation)
            exp_label.setWordWrap(True)
            exp_label.setFont(QFont("Microsoft YaHei UI", 12))
            exp_label.setStyleSheet("color: #475569; line-height: 1.6;")
            exp_frame_layout.addWidget(exp_label)
            
            answer_layout.addWidget(exp_frame)
        
        layout.addWidget(answer_container)
    
    def _format_answer(self, answer) -> str:
        """格式化答案显示"""
        if isinstance(answer, bool):
            return "正确" if answer else "错误"
        if isinstance(answer, list):
            return ", ".join(answer)
        return str(answer)
    
    def _check_correct(self) -> bool:
        """检查答案是否正确"""
        if self.user_answer is None:
            return False
        
        correct = self.question.answer
        user = self.user_answer
        
        if self.question.type == QuestionType.JUDGE.value:
            return bool(user) == bool(correct)
        
        if self.question.type == QuestionType.MULTIPLE.value:
            correct_set = set(correct) if isinstance(correct, list) else {correct}
            user_set = set(user) if isinstance(user, list) else {user}
            return correct_set == user_set
        
        return str(user).upper() == str(correct).upper()
    
    def get_answer(self):
        """获取当前答案"""
        return self.user_answer
    
    def set_answer(self, answer):
        """设置答案"""
        self.user_answer = answer
        if hasattr(self, 'option_group'):
            if self.question.type == QuestionType.JUDGE.value:
                self.option_group.set_selection(self._judge_answer_to_option(answer))
            else:
                self.option_group.set_selection(answer)
    
    def clear_answer(self):
        """清除答案"""
        self.user_answer = None
        if hasattr(self, 'option_group'):
            self.option_group.clear_selection()
