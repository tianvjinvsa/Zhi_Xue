"""
收藏服务
"""
import os
import json
from typing import List, Optional, Tuple

from config import DATA_DIR, config as app_config
from models import FavoriteQuestion, FavoriteCollection, Question


class FavoriteService:
    """收藏服务"""
    
    DEFAULT_FAVORITES_FILE = os.path.join(DATA_DIR, 'favorites.json')
    
    def __init__(self):
        self._collection: Optional[FavoriteCollection] = None
        self._load_favorites()
    
    def _get_favorites_file(self) -> str:
        """获取收藏文件路径（动态读取配置）"""
        custom_file = app_config.path_config.favorites_file
        if custom_file:
            # 确保目录存在
            dir_path = os.path.dirname(custom_file)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            return custom_file
        return self.DEFAULT_FAVORITES_FILE
    
    def _load_favorites(self):
        """加载收藏数据"""
        favorites_file = self._get_favorites_file()
        if os.path.exists(favorites_file):
            try:
                with open(favorites_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._collection = FavoriteCollection.from_dict(data)
            except Exception as e:
                print(f"加载收藏数据失败: {e}")
                self._collection = FavoriteCollection()
        else:
            self._collection = FavoriteCollection()
    
    def _save_favorites(self):
        """保存收藏数据"""
        try:
            favorites_file = self._get_favorites_file()
            with open(favorites_file, 'w', encoding='utf-8') as f:
                json.dump(self._collection.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存收藏数据失败: {e}")
    
    def add_favorite(self, question: Question, bank_id: str, bank_name: str) -> Tuple[bool, str]:
        """
        添加收藏
        返回: (是否成功, 消息)
        """
        if self._collection.is_favorited(question.id):
            return False, "该题目已收藏"
        
        fav = FavoriteQuestion(
            question_id=question.id,
            bank_id=bank_id,
            bank_name=bank_name,
            question_type=question.type,
            question_content=question.question,
            options=question.options.copy() if question.options else [],
            answer=question.answer,
            explanation=question.explanation,
            difficulty=question.difficulty,
            tags=question.tags.copy() if question.tags else []
        )
        
        if self._collection.add_favorite(fav):
            self._save_favorites()
            return True, "收藏成功"
        return False, "收藏失败"
    
    def remove_favorite(self, question_id: str) -> bool:
        """移除收藏"""
        if self._collection.remove_favorite(question_id):
            self._save_favorites()
            return True
        return False
    
    def is_favorited(self, question_id: str) -> bool:
        """检查是否已收藏"""
        return self._collection.is_favorited(question_id)
    
    def get_all_favorites(self) -> List[FavoriteQuestion]:
        """获取所有收藏"""
        return self._collection.get_all()
    
    def get_favorites_by_bank(self, bank_id: str) -> List[FavoriteQuestion]:
        """按题库获取收藏"""
        return self._collection.get_by_bank(bank_id)
    
    def get_banks_with_favorites(self) -> List[dict]:
        """获取有收藏的题库列表"""
        return self._collection.get_banks()
    
    def get_favorites_count(self) -> int:
        """获取收藏总数"""
        return len(self._collection.get_all())
    
    def get_statistics(self) -> dict:
        """获取收藏统计"""
        favorites = self._collection.get_all()
        banks = self._collection.get_banks()
        
        # 按题型统计
        type_stats = {}
        for fav in favorites:
            q_type = fav.question_type
            type_stats[q_type] = type_stats.get(q_type, 0) + 1
        
        return {
            'total': len(favorites),
            'bank_count': len(banks),
            'type_stats': type_stats,
            'banks': banks
        }
    
    def clear_all(self) -> bool:
        """清空所有收藏"""
        self._collection = FavoriteCollection()
        self._save_favorites()
        return True
    
    def update_note(self, question_id: str, note: str) -> bool:
        """更新题目备注"""
        for fav in self._collection.favorites:
            if fav.question_id == question_id:
                fav.note = note
                self._save_favorites()
                return True
        return False
