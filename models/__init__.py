"""
数据模型模块
"""
from .question import Question, QuestionType
from .bank import QuestionBank
from .paper import Paper, PaperQuestion
from .result import ExamResult, QuestionResult
from .favorite import FavoriteQuestion, FavoriteCollection

__all__ = [
    'Question',
    'QuestionType', 
    'QuestionBank',
    'Paper',
    'PaperQuestion',
    'ExamResult',
    'QuestionResult',
    'FavoriteQuestion',
    'FavoriteCollection'
]
