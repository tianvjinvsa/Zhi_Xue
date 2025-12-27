"""
选项组组件
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, 
    QCheckBox, QButtonGroup, QLabel
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import List, Optional, Union


class OptionGroup(QWidget):
    """选项组组件 - 支持单选和多选"""
    
    selection_changed = Signal(object)  # 选中的答案
    
    def __init__(self, options: List[str], multiple: bool = False,
                 selected: Union[str, List[str], None] = None,
                 correct_answer: Union[str, List[str], None] = None,
                 readonly: bool = False, parent=None):
        super().__init__(parent)
        
        self.options = options
        self.multiple = multiple
        self.correct_answer = correct_answer
        self.readonly = readonly
        self._buttons: List[QRadioButton | QCheckBox] = []
        
        self._setup_ui()
        
        if selected:
            self.set_selection(selected)
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(10)
        
        if not self.multiple:
            self.button_group = QButtonGroup(self)
        
        for i, option in enumerate(self.options):
            option_layout = QHBoxLayout()
            option_layout.setContentsMargins(0, 0, 0, 0)
            
            # 创建按钮
            if self.multiple:
                btn = QCheckBox(option)
                btn.stateChanged.connect(self._on_selection_changed)
            else:
                btn = QRadioButton(option)
                self.button_group.addButton(btn, i)
                btn.toggled.connect(self._on_selection_changed)
            
            btn.setFont(QFont("Microsoft YaHei UI", 13))
            btn.setEnabled(not self.readonly)
            
            # 设置样式
            letter = self._get_option_letter(option)
            style = self._get_option_style(letter)
            btn.setStyleSheet(style)
            
            self._buttons.append(btn)
            option_layout.addWidget(btn)
            option_layout.addStretch()
            
            layout.addLayout(option_layout)
    
    def _get_option_letter(self, option: str) -> str:
        """获取选项字母"""
        if option and len(option) > 0:
            return option[0].upper()
        return ""
    
    def _get_option_style(self, letter: str) -> str:
        """获取选项样式"""
        base_style = """
            QRadioButton, QCheckBox {
                padding: 14px 18px;
                border-radius: 12px;
                background-color: #f8fafc;
                border: 2px solid transparent;
                color: #334155;
                min-width: 200px;
            }
            QRadioButton:hover, QCheckBox:hover {
                background-color: #f1f5f9;
                border-color: #e2e8f0;
            }
            QRadioButton:checked, QCheckBox:checked {
                background-color: #f5f3ff;
                border-color: #667eea;
                color: #5b21b6;
            }
            QRadioButton::indicator, QCheckBox::indicator {
                width: 20px;
                height: 20px;
                margin-right: 10px;
            }
            QRadioButton::indicator {
                border-radius: 10px;
                border: 2px solid #cbd5e1;
                background-color: white;
            }
            QRadioButton::indicator:checked {
                border: 6px solid #667eea;
                background-color: white;
            }
            QCheckBox::indicator {
                border-radius: 4px;
                border: 2px solid #cbd5e1;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #667eea;
                border-color: #667eea;
            }
        """
        
        if self.correct_answer is not None:
            # 显示答案模式
            is_correct = self._is_correct_option(letter)
            if is_correct:
                return """
                    QRadioButton, QCheckBox {
                        padding: 14px 18px;
                        border-radius: 12px;
                        background-color: #ecfdf5;
                        border: 2px solid #10b981;
                        color: #047857;
                        font-weight: 500;
                    }
                    QRadioButton::indicator, QCheckBox::indicator {
                        width: 20px;
                        height: 20px;
                        margin-right: 10px;
                    }
                    QRadioButton::indicator {
                        border-radius: 10px;
                        border: 2px solid #10b981;
                        background-color: white;
                    }
                    QRadioButton::indicator:checked {
                        border: 6px solid #10b981;
                        background-color: white;
                    }
                    QCheckBox::indicator {
                        border-radius: 4px;
                        border: 2px solid #10b981;
                        background-color: #10b981;
                    }
                """
        
        return base_style
    
    def _is_correct_option(self, letter: str) -> bool:
        """检查是否是正确选项"""
        if self.correct_answer is None:
            return False
        
        if isinstance(self.correct_answer, list):
            return letter in self.correct_answer
        return letter == str(self.correct_answer).upper()
    
    def _on_selection_changed(self):
        """选择变更回调"""
        selection = self.get_selection()
        self.selection_changed.emit(selection)
    
    def get_selection(self) -> Union[str, List[str], None]:
        """获取当前选择"""
        if self.multiple:
            selected = []
            for btn in self._buttons:
                if btn.isChecked():
                    letter = self._get_option_letter(btn.text())
                    selected.append(letter)
            return selected if selected else None
        else:
            for btn in self._buttons:
                if btn.isChecked():
                    return self._get_option_letter(btn.text())
            return None
    
    def set_selection(self, selection: Union[str, List[str], None]):
        """设置选择"""
        if selection is None:
            self.clear_selection()
            return
        
        if isinstance(selection, str):
            selection = [selection]
        
        selection_upper = [s.upper() for s in selection]
        
        for btn in self._buttons:
            letter = self._get_option_letter(btn.text())
            should_check = letter in selection_upper
            btn.blockSignals(True)
            btn.setChecked(should_check)
            btn.blockSignals(False)
    
    def clear_selection(self):
        """清除选择"""
        for btn in self._buttons:
            btn.blockSignals(True)
            btn.setChecked(False)
            btn.blockSignals(False)
    
    def set_readonly(self, readonly: bool):
        """设置只读状态"""
        self.readonly = readonly
        for btn in self._buttons:
            btn.setEnabled(not readonly)
