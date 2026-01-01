"""
题库数据模型
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict
from datetime import datetime
import uuid

from .question import Question


@dataclass
class QuestionBank:
    """题库数据模型"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    subject: str = ""  # 所属科目/课程
    chapters: List[str] = field(default_factory=list)  # 章节列表
    questions: List[Question] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def __post_init__(self):
        """初始化后处理"""
        if self.questions is None:
            self.questions = []
    
    def to_dict(self) -> dict:
        """转换为字典"""
        data = asdict(self)
        # 题目列表转换
        data['questions'] = [q.to_dict() if isinstance(q, Question) else q for q in self.questions]
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'QuestionBank':
        """从字典创建实例"""
        questions_data = data.pop('questions', [])
        bank = cls(**{k: v for k, v in data.items() if k in ['id', 'name', 'description', 'subject', 'chapters', 'created_at', 'updated_at']})
        bank.questions = [Question.from_dict(q) if isinstance(q, dict) else q for q in questions_data]
        return bank
    
    def add_question(self, question: Question) -> bool:
        """添加题目（支持去重检查）"""
        # 检查ID重复
        if any(q.id == question.id for q in self.questions):
            return False
        # 检查内容重复（基于题目内容）
        if any(q.question.strip() == question.question.strip() for q in self.questions):
            return False
        self.questions.append(question)
        self.update()
        return True
    
    def is_duplicate(self, question_content: str) -> bool:
        """检查题目内容是否重复"""
        return any(q.question.strip() == question_content.strip() for q in self.questions)
    
    def remove_question(self, question_id: str) -> bool:
        """删除题目"""
        for i, q in enumerate(self.questions):
            if q.id == question_id:
                self.questions.pop(i)
                self.update()
                return True
        return False
    
    def get_question(self, question_id: str) -> Optional[Question]:
        """获取题目"""
        for q in self.questions:
            if q.id == question_id:
                return q
        return None
    
    def update_question(self, question: Question) -> bool:
        """更新题目"""
        for i, q in enumerate(self.questions):
            if q.id == question.id:
                question.update()
                self.questions[i] = question
                self.update()
                return True
        return False
    
    def get_questions_by_type(self, question_type: str) -> List[Question]:
        """按类型获取题目"""
        return [q for q in self.questions if q.type == question_type]
    
    def get_questions_by_difficulty(self, min_diff: int = 1, max_diff: int = 5) -> List[Question]:
        """按难度范围获取题目"""
        return [q for q in self.questions if min_diff <= q.difficulty <= max_diff]
    
    def get_questions_by_tags(self, tags: List[str]) -> List[Question]:
        """按标签获取题目"""
        return [q for q in self.questions if any(t in q.tags for t in tags)]
    
    def get_questions_by_chapter(self, chapter: str) -> List[Question]:
        """按章节获取题目"""
        if not chapter:
            return self.questions
        return [q for q in self.questions if q.chapter == chapter]
    
    def get_all_chapters(self) -> List[str]:
        """获取所有章节（包含预定义章节和题目中的章节）"""
        chapters = set(self.chapters) if self.chapters else set()
        for q in self.questions:
            if q.chapter:
                chapters.add(q.chapter)
        return sorted(list(chapters))
    
    def add_chapter(self, chapter: str) -> bool:
        """添加章节"""
        if not chapter or chapter in self.chapters:
            return False
        self.chapters.append(chapter)
        self.update()
        return True
    
    def remove_chapter(self, chapter: str) -> bool:
        """删除章节"""
        if chapter in self.chapters:
            self.chapters.remove(chapter)
            self.update()
            return True
        return False
    
    def get_statistics(self) -> Dict:
        """获取题库统计信息"""
        stats = {
            'total': len(self.questions),
            'by_type': {},
            'by_difficulty': {},
            'by_source': {},
            'by_chapter': {}
        }
        
        for q in self.questions:
            # 按类型统计
            stats['by_type'][q.type] = stats['by_type'].get(q.type, 0) + 1
            # 按难度统计
            stats['by_difficulty'][q.difficulty] = stats['by_difficulty'].get(q.difficulty, 0) + 1
            # 按来源统计
            stats['by_source'][q.source] = stats['by_source'].get(q.source, 0) + 1
            # 按章节统计
            chapter = q.chapter if q.chapter else "未分类"
            stats['by_chapter'][chapter] = stats['by_chapter'].get(chapter, 0) + 1
        
        return stats
    
    def update(self):
        """更新修改时间"""
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def validate(self) -> tuple[bool, str]:
        """验证题库数据"""
        if not self.name.strip():
            return False, "题库名称不能为空"
        return True, ""
