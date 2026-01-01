"""
答题结果数据模型
"""
from dataclasses import dataclass, field, asdict
from typing import List, Union, Optional, Dict
from datetime import datetime
import uuid


@dataclass
class QuestionResult:
    """单题答题结果"""
    question_id: str = ""
    question_type: str = "single"
    user_answer: Union[str, List[str], bool, None] = None
    correct_answer: Union[str, List[str], bool] = ""
    is_correct: bool = False
    score: float = 0.0
    max_score: float = 5.0
    time_spent: int = 0  # 答题用时（秒）


@dataclass
class ExamResult:
    """考试结果数据模型"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    paper_id: str = ""
    paper_title: str = ""
    user_id: str = ""  # 可选，预留用户系统
    start_time: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    end_time: str = ""
    total_score: float = 100.0
    user_score: float = 0.0
    details: List[QuestionResult] = field(default_factory=list)
    status: str = "in_progress"  # in_progress, completed, timeout
    source_banks: List[str] = field(default_factory=list)  # 来源题库ID列表
    
    def __post_init__(self):
        """初始化后处理"""
        if self.details is None:
            self.details = []
        if self.source_banks is None:
            self.source_banks = []
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = {
            'id': self.id,
            'paper_id': self.paper_id,
            'paper_title': self.paper_title,
            'user_id': self.user_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'total_score': self.total_score,
            'user_score': self.user_score,
            'details': [asdict(d) if isinstance(d, QuestionResult) else d for d in self.details],
            'status': self.status,
            'source_banks': self.source_banks
        }
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ExamResult':
        """从字典创建实例"""
        details_data = data.pop('details', [])
        
        valid_fields = ['id', 'paper_id', 'paper_title', 'user_id', 'start_time', 
                       'end_time', 'total_score', 'user_score', 'status', 'source_banks']
        result_data = {k: v for k, v in data.items() if k in valid_fields}
        
        result = cls(**result_data)
        result.details = [
            QuestionResult(**d) if isinstance(d, dict) else d 
            for d in details_data
        ]
        return result
    
    def add_answer(self, question_result: QuestionResult):
        """添加答题记录"""
        # 检查是否已存在该题的答案
        for i, d in enumerate(self.details):
            if d.question_id == question_result.question_id:
                self.details[i] = question_result
                return
        self.details.append(question_result)
    
    def get_answer(self, question_id: str) -> Optional[QuestionResult]:
        """获取某题的答题记录"""
        for d in self.details:
            if d.question_id == question_id:
                return d
        return None
    
    def calculate_score(self):
        """计算总得分"""
        self.user_score = sum(d.score for d in self.details)
    
    def complete(self):
        """完成答题"""
        self.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = "completed"
        self.calculate_score()
    
    def timeout(self):
        """超时结束"""
        self.end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = "timeout"
        self.calculate_score()
    
    def get_statistics(self) -> Dict:
        """获取答题统计"""
        stats = {
            'total_questions': len(self.details),
            'correct_count': sum(1 for d in self.details if d.is_correct),
            'wrong_count': sum(1 for d in self.details if not d.is_correct),
            'unanswered_count': sum(1 for d in self.details if d.user_answer is None),
            'accuracy': 0.0,
            'score_rate': 0.0,
            'by_type': {}
        }
        
        if stats['total_questions'] > 0:
            stats['accuracy'] = stats['correct_count'] / stats['total_questions'] * 100
        
        if self.total_score > 0:
            stats['score_rate'] = self.user_score / self.total_score * 100
        
        # 按题型统计
        for d in self.details:
            if d.question_type not in stats['by_type']:
                stats['by_type'][d.question_type] = {
                    'total': 0,
                    'correct': 0,
                    'score': 0.0,
                    'max_score': 0.0
                }
            type_stats = stats['by_type'][d.question_type]
            type_stats['total'] += 1
            type_stats['correct'] += 1 if d.is_correct else 0
            type_stats['score'] += d.score
            type_stats['max_score'] += d.max_score
        
        return stats
    
    def get_duration_seconds(self) -> int:
        """获取答题时长（秒）"""
        if not self.end_time:
            return 0
        try:
            start = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(self.end_time, "%Y-%m-%d %H:%M:%S")
            return int((end - start).total_seconds())
        except:
            return 0
    
    def get_duration_display(self) -> str:
        """获取答题时长显示"""
        seconds = self.get_duration_seconds()
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}分{secs}秒"
