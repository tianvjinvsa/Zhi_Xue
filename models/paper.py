"""
试卷数据模型
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime
import uuid


@dataclass
class PaperQuestion:
    """试卷题目"""
    order: int = 0
    question_id: str = ""
    score: float = 5.0
    type: str = "single"


@dataclass
class Paper:
    """试卷数据模型"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    time_limit: int = 60  # 时间限制（分钟），0表示不限时
    total_score: float = 100.0
    questions: List[PaperQuestion] = field(default_factory=list)
    score_rules: Dict[str, float] = field(default_factory=lambda: {
        "single": 5.0,
        "multiple": 5.0,
        "judge": 2.0,
        "fill": 5.0,
        "essay": 10.0
    })
    source_banks: List[str] = field(default_factory=list)  # 来源题库ID列表
    
    def __post_init__(self):
        """初始化后处理"""
        if self.questions is None:
            self.questions = []
        if self.source_banks is None:
            self.source_banks = []
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at,
            'time_limit': self.time_limit,
            'total_score': self.total_score,
            'questions': [asdict(q) if isinstance(q, PaperQuestion) else q for q in self.questions],
            'score_rules': self.score_rules,
            'source_banks': self.source_banks
        }
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Paper':
        """从字典创建实例"""
        questions_data = data.pop('questions', [])
        
        # 过滤有效字段
        valid_fields = ['id', 'title', 'description', 'created_at', 'time_limit', 
                       'total_score', 'score_rules', 'source_banks']
        paper_data = {k: v for k, v in data.items() if k in valid_fields}
        
        paper = cls(**paper_data)
        paper.questions = [
            PaperQuestion(**q) if isinstance(q, dict) else q 
            for q in questions_data
        ]
        return paper
    
    def add_question(self, question_id: str, question_type: str, score: Optional[float] = None):
        """添加题目到试卷"""
        if score is None:
            score = self.score_rules.get(question_type, 5.0)
        
        order = len(self.questions) + 1
        pq = PaperQuestion(
            order=order,
            question_id=question_id,
            score=score,
            type=question_type
        )
        self.questions.append(pq)
        self._recalculate_total_score()
    
    def remove_question(self, question_id: str) -> bool:
        """从试卷移除题目"""
        for i, q in enumerate(self.questions):
            if q.question_id == question_id:
                self.questions.pop(i)
                self._reorder_questions()
                self._recalculate_total_score()
                return True
        return False
    
    def _reorder_questions(self):
        """重新排序题目"""
        for i, q in enumerate(self.questions):
            q.order = i + 1
    
    def _recalculate_total_score(self):
        """重新计算总分"""
        self.total_score = sum(q.score for q in self.questions)
    
    def get_question_count_by_type(self) -> Dict[str, int]:
        """获取各类型题目数量"""
        counts = {}
        for q in self.questions:
            counts[q.type] = counts.get(q.type, 0) + 1
        return counts
    
    def validate(self) -> tuple[bool, str]:
        """验证试卷数据"""
        if not self.title.strip():
            return False, "试卷标题不能为空"
        if len(self.questions) == 0:
            return False, "试卷至少需要一道题目"
        return True, ""
