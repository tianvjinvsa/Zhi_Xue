"""
题库服务 - 处理题库的增删改查
"""
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from functools import lru_cache
import hashlib
import os

# 使用高性能 JSON 库（比标准库快 10-50 倍）
try:
    import orjson
    def json_loads(s): return orjson.loads(s)
    def json_dumps(obj): return orjson.dumps(obj, option=orjson.OPT_INDENT_2).decode('utf-8')
except ImportError:
    import json
    def json_loads(s): return json.loads(s)
    def json_dumps(obj): return json.dumps(obj, ensure_ascii=False, indent=2)

from config import BANKS_DIR, DATA_DIR, APP_ROOT, config as app_config
from models import QuestionBank, Question


class BankService:
    """题库服务类"""
    
    META_FILE = DATA_DIR / "banks_meta.json"
    
    # 题库缓存：{bank_id: (mtime, QuestionBank)}
    _cache: Dict[str, tuple] = {}
    
    def __init__(self):
        self._ensure_meta_file()
    
    def _get_banks_dir(self) -> Path:
        """获取题库存储目录（动态读取配置）"""
        custom_dir = app_config.path_config.banks_dir
        if custom_dir:
            try:
                path = Path(custom_dir)
                # 确保是绝对路径
                if not path.is_absolute():
                    path = APP_ROOT / path
                
                path.mkdir(parents=True, exist_ok=True)
                return path
            except Exception as e:
                print(f"使用自定义题库目录失败: {e}，将使用默认目录")
                return BANKS_DIR
        return BANKS_DIR
    
    def _ensure_meta_file(self):
        """确保元数据文件存在"""
        if not self.META_FILE.exists():
            self._save_meta({})
    
    def _load_meta(self) -> Dict:
        """加载题库元数据"""
        try:
            with open(self.META_FILE, 'rb') as f:
                return json_loads(f.read())
        except:
            return {}
    
    def _save_meta(self, meta: Dict):
        """保存题库元数据"""
        with open(self.META_FILE, 'w', encoding='utf-8') as f:
            f.write(json_dumps(meta))
    
    def _get_bank_file(self, bank_id: str) -> Path:
        """获取题库文件路径"""
        return self._get_banks_dir() / f"bank_{bank_id}.json"
    
    def create_bank(self, name: str, description: str = "", subject: str = "") -> QuestionBank:
        """创建新题库"""
        bank = QuestionBank(
            name=name,
            description=description,
            subject=subject
        )
        
        # 保存题库文件
        self._save_bank(bank)
        
        # 更新元数据
        meta = self._load_meta()
        meta[bank.id] = {
            'name': bank.name,
            'description': bank.description,
            'subject': bank.subject,
            'question_count': 0,
            'created_at': bank.created_at,
            'updated_at': bank.updated_at
        }
        self._save_meta(meta)
        
        return bank
    
    def _save_bank(self, bank: QuestionBank):
        """保存题库到文件"""
        file_path = self._get_bank_file(bank.id)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json_dumps(bank.to_dict()))
        # 清除缓存
        if bank.id in self._cache:
            del self._cache[bank.id]
    
    def get_bank(self, bank_id: str) -> Optional[QuestionBank]:
        """获取题库（带缓存）"""
        file_path = self._get_bank_file(bank_id)
        if not file_path.exists():
            return None
        
        try:
            # 检查缓存是否有效（基于文件修改时间）
            mtime = os.path.getmtime(file_path)
            if bank_id in self._cache:
                cached_mtime, cached_bank = self._cache[bank_id]
                if cached_mtime == mtime:
                    return cached_bank
            
            # 使用高性能 JSON 解析
            with open(file_path, 'rb') as f:
                data = json_loads(f.read())
            bank = QuestionBank.from_dict(data)
            
            # 更新缓存
            self._cache[bank_id] = (mtime, bank)
            return bank
        except Exception as e:
            print(f"加载题库失败: {e}")
            return None
    
    def invalidate_cache(self, bank_id: str = None):
        """清除缓存"""
        if bank_id:
            self._cache.pop(bank_id, None)
        else:
            self._cache.clear()
    
    def get_all_banks(self) -> List[QuestionBank]:
        """获取所有题库"""
        meta = self._load_meta()
        banks = []
        for bank_id in meta.keys():
            bank = self.get_bank(bank_id)
            if bank:
                banks.append(bank)
        return banks
    
    def get_banks_summary(self) -> List[Dict]:
        """获取题库摘要列表（不加载题目）"""
        meta = self._load_meta()
        summaries = []
        for bank_id, info in meta.items():
            summaries.append({
                'id': bank_id,
                **info
            })
        return summaries
    
    def update_bank(self, bank: QuestionBank) -> bool:
        """更新题库"""
        if not self._get_bank_file(bank.id).exists():
            return False
        
        bank.update()
        self._save_bank(bank)
        
        # 更新元数据
        meta = self._load_meta()
        if bank.id in meta:
            meta[bank.id].update({
                'name': bank.name,
                'description': bank.description,
                'subject': bank.subject,
                'question_count': len(bank.questions),
                'updated_at': bank.updated_at
            })
            self._save_meta(meta)
        
        return True
    
    def delete_bank(self, bank_id: str) -> bool:
        """删除题库"""
        file_path = self._get_bank_file(bank_id)
        if file_path.exists():
            file_path.unlink()
        
        meta = self._load_meta()
        if bank_id in meta:
            del meta[bank_id]
            self._save_meta(meta)
        
        return True
    
    def add_question_to_bank(self, bank_id: str, question: Question) -> bool:
        """向题库添加题目"""
        bank = self.get_bank(bank_id)
        if not bank:
            return False
        
        if bank.add_question(question):
            self._save_bank(bank)
            # 更新元数据
            meta = self._load_meta()
            if bank_id in meta:
                meta[bank_id]['question_count'] = len(bank.questions)
                meta[bank_id]['updated_at'] = bank.updated_at
                self._save_meta(meta)
            return True
        return False

    def batch_add_questions(self, bank_id: str, questions: List[Question]) -> int:
        """批量向题库添加题目"""
        bank = self.get_bank(bank_id)
        if not bank:
            return 0
        
        added_count = 0
        for question in questions:
            if bank.add_question(question):
                added_count += 1
        
        if added_count > 0:
            self._save_bank(bank)
            # 更新元数据
            meta = self._load_meta()
            if bank_id in meta:
                meta[bank_id]['question_count'] = len(bank.questions)
                meta[bank_id]['updated_at'] = bank.updated_at
                self._save_meta(meta)
        
        return added_count
    
    def update_question_in_bank(self, bank_id: str, question: Question) -> bool:
        """更新题库中的题目"""
        bank = self.get_bank(bank_id)
        if not bank:
            return False
        
        if bank.update_question(question):
            self._save_bank(bank)
            return True
        return False
    
    def delete_question_from_bank(self, bank_id: str, question_id: str) -> bool:
        """从题库删除题目"""
        bank = self.get_bank(bank_id)
        if not bank:
            return False
        
        if bank.remove_question(question_id):
            self._save_bank(bank)
            # 更新元数据
            meta = self._load_meta()
            if bank_id in meta:
                meta[bank_id]['question_count'] = len(bank.questions)
                meta[bank_id]['updated_at'] = bank.updated_at
                self._save_meta(meta)
            
            # 同时从收藏中删除
            try:
                from services.favorite_service import FavoriteService
                favorite_service = FavoriteService()
                favorite_service.remove_favorite(question_id)
            except Exception as e:
                print(f"从收藏中删除题目失败: {e}")

            return True
        return False
    
    def search_questions(self, bank_id: str, keyword: str = "", 
                        question_type: str = "", tags: List[str] = None) -> List[Question]:
        """搜索题目"""
        bank = self.get_bank(bank_id)
        if not bank:
            return []
        
        results = bank.questions
        
        # 按关键词筛选
        if keyword:
            keyword_lower = keyword.lower()
            results = [q for q in results if keyword_lower in q.question.lower()]
        
        # 按类型筛选
        if question_type:
            results = [q for q in results if q.type == question_type]
        
        # 按标签筛选
        if tags:
            results = [q for q in results if any(t in q.tags for t in tags)]
        
        return results
    
    def export_bank(self, bank_id: str, export_path: str) -> bool:
        """导出题库"""
        bank = self.get_bank(bank_id)
        if not bank:
            return False
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(bank.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出题库失败: {e}")
            return False
    
    def import_bank(self, import_path: str) -> Optional[QuestionBank]:
        """导入题库"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 创建新ID避免冲突
            import uuid
            data['id'] = str(uuid.uuid4())
            data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data['updated_at'] = data['created_at']
            
            bank = QuestionBank.from_dict(data)
            self._save_bank(bank)
            
            # 更新元数据
            meta = self._load_meta()
            meta[bank.id] = {
                'name': bank.name,
                'description': bank.description,
                'subject': bank.subject,
                'question_count': len(bank.questions),
                'created_at': bank.created_at,
                'updated_at': bank.updated_at
            }
            self._save_meta(meta)
            
            return bank
        except Exception as e:
            print(f"导入题库失败: {e}")
            return None
