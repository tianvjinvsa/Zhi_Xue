"""
题目数据模型
"""
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Union
from datetime import datetime
import uuid


class QuestionType(Enum):
    """题目类型枚举"""
    SINGLE = "single"       # 单选题
    MULTIPLE = "multiple"   # 多选题
    JUDGE = "judge"         # 判断题
    FILL = "fill"           # 填空题
    ESSAY = "essay"         # 简答题
    
    @classmethod
    def get_display_name(cls, type_value: str) -> str:
        """获取题目类型的显示名称"""
        names = {
            "single": "单选题",
            "multiple": "多选题",
            "judge": "判断题",
            "fill": "填空题",
            "essay": "简答题"
        }
        return names.get(type_value, "未知类型")
    
    @classmethod
    def from_string(cls, value: str) -> 'QuestionType':
        """从字符串转换为枚举"""
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"未知的题目类型: {value}")


@dataclass
class Question:
    """题目数据模型"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = QuestionType.SINGLE.value
    question: str = ""
    options: List[str] = field(default_factory=list)
    answer: Union[str, List[str], bool] = ""
    explanation: str = ""
    difficulty: int = 3  # 1-5难度等级
    tags: List[str] = field(default_factory=list)
    chapter: str = ""  # 章节/分类
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    source: str = "manual"  # manual, ai_generated, imported
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保options是列表
        if self.options is None:
            self.options = []
        # 确保tags是列表
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        # 包含动态添加的bank_id属性（用于试卷中的题目）
        if hasattr(self, 'bank_id'):
            data['bank_id'] = self.bank_id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Question':
        """从字典创建实例"""
        # 处理可能缺失的字段
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def get_type_display(self) -> str:
        """获取题目类型显示名称"""
        return QuestionType.get_display_name(self.type)
    
    def validate(self) -> tuple[bool, str]:
        """验证题目数据完整性"""
        if not self.question.strip():
            return False, "题目内容不能为空"
        
        if self.type in [QuestionType.SINGLE.value, QuestionType.MULTIPLE.value]:
            if len(self.options) < 2:
                return False, "选择题至少需要2个选项"
            if not self.answer:
                return False, "请设置正确答案"
        
        if self.type == QuestionType.JUDGE.value:
            if not isinstance(self.answer, bool):
                return False, "判断题答案必须是布尔值"
        
        if self.difficulty < 1 or self.difficulty > 5:
            return False, "难度等级必须在1-5之间"
        
        return True, ""
    
    def check_answer(self, user_answer: Union[str, List[str], bool]) -> tuple[bool, float]:
        """
        检查答案是否正确
        返回: (是否完全正确, 得分比例0-1)
        """
        if self.type == QuestionType.SINGLE.value:
            is_correct = str(user_answer).upper() == str(self.answer).upper()
            return is_correct, 1.0 if is_correct else 0.0
        
        elif self.type == QuestionType.MULTIPLE.value:
            # 多选题
            correct_set = set(a.upper() for a in self.answer) if isinstance(self.answer, list) else {str(self.answer).upper()}
            user_set = set(a.upper() for a in user_answer) if isinstance(user_answer, list) else {str(user_answer).upper()}
            
            if user_set == correct_set:
                return True, 1.0
            elif user_set.issubset(correct_set) and len(user_set) > 0:
                # 部分正确，按比例得分
                return False, len(user_set) / len(correct_set) * 0.5
            else:
                return False, 0.0
        
        elif self.type == QuestionType.JUDGE.value:
            is_correct = bool(user_answer) == bool(self.answer)
            return is_correct, 1.0 if is_correct else 0.0
        
        elif self.type == QuestionType.FILL.value:
            # 填空题简单匹配
            is_correct = str(user_answer).strip().lower() == str(self.answer).strip().lower()
            return is_correct, 1.0 if is_correct else 0.0
        
        return False, 0.0
    
    def update(self):
        """更新修改时间"""
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
