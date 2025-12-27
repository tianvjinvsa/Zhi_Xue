"""
收藏模型
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import uuid


@dataclass
class FavoriteQuestion:
    """收藏的题目"""
    question_id: str          # 原题目ID
    bank_id: str              # 所属题库ID
    bank_name: str            # 题库名称
    question_type: str        # 题目类型
    question_content: str     # 题目内容
    options: List[str]        # 选项
    answer: any               # 答案
    explanation: str = ""     # 解析
    difficulty: int = 3       # 难度
    tags: List[str] = field(default_factory=list)
    favorite_time: str = ""   # 收藏时间
    note: str = ""            # 用户备注
    id: str = ""              # 收藏记录ID
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.favorite_time:
            self.favorite_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'question_id': self.question_id,
            'bank_id': self.bank_id,
            'bank_name': self.bank_name,
            'question_type': self.question_type,
            'question_content': self.question_content,
            'options': self.options,
            'answer': self.answer,
            'explanation': self.explanation,
            'difficulty': self.difficulty,
            'tags': self.tags,
            'favorite_time': self.favorite_time,
            'note': self.note
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FavoriteQuestion':
        return cls(
            id=data.get('id', ''),
            question_id=data.get('question_id', ''),
            bank_id=data.get('bank_id', ''),
            bank_name=data.get('bank_name', ''),
            question_type=data.get('question_type', ''),
            question_content=data.get('question_content', ''),
            options=data.get('options', []),
            answer=data.get('answer'),
            explanation=data.get('explanation', ''),
            difficulty=data.get('difficulty', 3),
            tags=data.get('tags', []),
            favorite_time=data.get('favorite_time', ''),
            note=data.get('note', '')
        )


@dataclass
class FavoriteCollection:
    """收藏集合"""
    favorites: List[FavoriteQuestion] = field(default_factory=list)
    
    def add_favorite(self, fav: FavoriteQuestion) -> bool:
        """添加收藏，如果已存在则返回False"""
        # 检查是否已经收藏（通过原题目ID判断）
        if self.is_favorited(fav.question_id):
            return False
        self.favorites.append(fav)
        return True
    
    def remove_favorite(self, question_id: str) -> bool:
        """移除收藏"""
        for i, fav in enumerate(self.favorites):
            if fav.question_id == question_id:
                del self.favorites[i]
                return True
        return False
    
    def is_favorited(self, question_id: str) -> bool:
        """检查是否已收藏"""
        return any(f.question_id == question_id for f in self.favorites)
    
    def get_by_bank(self, bank_id: str) -> List[FavoriteQuestion]:
        """按题库获取收藏"""
        return [f for f in self.favorites if f.bank_id == bank_id]
    
    def get_banks(self) -> List[dict]:
        """获取所有有收藏的题库列表"""
        banks = {}
        for fav in self.favorites:
            if fav.bank_id not in banks:
                banks[fav.bank_id] = {
                    'id': fav.bank_id,
                    'name': fav.bank_name,
                    'count': 0
                }
            banks[fav.bank_id]['count'] += 1
        return list(banks.values())
    
    def get_all(self) -> List[FavoriteQuestion]:
        """获取所有收藏"""
        return self.favorites
    
    def to_dict(self) -> dict:
        return {
            'favorites': [f.to_dict() for f in self.favorites]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FavoriteCollection':
        favorites = [FavoriteQuestion.from_dict(f) for f in data.get('favorites', [])]
        return cls(favorites=favorites)
