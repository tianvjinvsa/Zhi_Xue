"""
试卷服务 - 处理组卷和试卷管理
"""
import json
import random
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

from config import PAPERS_DIR, config as app_config
from models import Paper, PaperQuestion, Question, QuestionBank
from services.bank_service import BankService


@dataclass
class PaperGenerateConfig:
    """组卷配置"""
    title: str = "新试卷"
    description: str = ""
    time_limit: int = 60
    bank_ids: List[str] = None  # 来源题库
    single_count: int = 10      # 单选题数量
    multiple_count: int = 5     # 多选题数量
    judge_count: int = 5        # 判断题数量
    fill_count: int = 0         # 填空题数量
    min_difficulty: int = 1     # 最小难度
    max_difficulty: int = 5     # 最大难度
    tags: List[str] = None      # 标签筛选
    score_rules: Dict[str, float] = None  # 分值规则
    shuffle_questions: bool = False  # 是否打乱题目顺序
    
    def __post_init__(self):
        if self.bank_ids is None:
            self.bank_ids = []
        if self.tags is None:
            self.tags = []
        if self.score_rules is None:
            self.score_rules = {
                "single": 5.0,
                "multiple": 5.0,
                "judge": 2.0,
                "fill": 5.0,
                "essay": 10.0
            }


class PaperService:
    """试卷服务类"""
    
    def __init__(self):
        self.bank_service = BankService()
    
    def _get_papers_dir(self) -> Path:
        """获取试卷存储目录（动态读取配置）"""
        custom_dir = app_config.path_config.papers_dir
        if custom_dir:
            path = Path(custom_dir)
            path.mkdir(parents=True, exist_ok=True)
            return path
        return PAPERS_DIR
    
    def _get_paper_file(self, paper_id: str) -> Path:
        """获取试卷文件路径"""
        return self._get_papers_dir() / f"paper_{paper_id}.json"
    
    def _save_paper(self, paper: Paper):
        """保存试卷"""
        file_path = self._get_paper_file(paper.id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(paper.to_dict(), f, ensure_ascii=False, indent=2)
    
    def get_paper(self, paper_id: str) -> Optional[Paper]:
        """获取试卷"""
        file_path = self._get_paper_file(paper_id)
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Paper.from_dict(data)
        except Exception as e:
            print(f"加载试卷失败: {e}")
            return None
    
    def get_all_papers(self) -> List[Paper]:
        """获取所有试卷"""
        papers = []
        papers_dir = self._get_papers_dir()
        for file_path in papers_dir.glob("paper_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                papers.append(Paper.from_dict(data))
            except:
                continue
        return sorted(papers, key=lambda p: p.created_at, reverse=True)
    
    def delete_paper(self, paper_id: str) -> bool:
        """删除试卷"""
        file_path = self._get_paper_file(paper_id)
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def generate_paper(self, config: PaperGenerateConfig) -> tuple[Optional[Paper], str]:
        """
        根据配置生成试卷
        返回: (试卷对象, 错误消息)
        """
        # 收集所有候选题目
        all_questions: Dict[str, List[Question]] = {
            'single': [],
            'multiple': [],
            'judge': [],
            'fill': [],
            'essay': []
        }
        
        # 从指定题库收集题目
        for bank_id in config.bank_ids:
            bank = self.bank_service.get_bank(bank_id)
            if not bank:
                continue
            
            for q in bank.questions:
                # 难度筛选
                if not (config.min_difficulty <= q.difficulty <= config.max_difficulty):
                    continue
                # 标签筛选
                if config.tags and not any(t in q.tags for t in config.tags):
                    continue
                
                if q.type in all_questions:
                    all_questions[q.type].append(q)
        
        # 检查题目是否充足
        required = {
            'single': config.single_count,
            'multiple': config.multiple_count,
            'judge': config.judge_count,
            'fill': config.fill_count
        }
        
        for q_type, count in required.items():
            if count > 0 and len(all_questions[q_type]) < count:
                return None, f"{q_type}类型题目不足，需要{count}道，实际只有{len(all_questions[q_type])}道"
        
        # 随机抽题
        paper = Paper(
            title=config.title,
            description=config.description,
            time_limit=config.time_limit,
            score_rules=config.score_rules,
            source_banks=config.bank_ids,
            shuffle_questions=config.shuffle_questions
        )
        
        selected_ids = set()
        
        for q_type, count in required.items():
            if count <= 0:
                continue
            
            available = [q for q in all_questions[q_type] if q.id not in selected_ids]
            selected = random.sample(available, count)
            
            for q in selected:
                selected_ids.add(q.id)
                paper.add_question(
                    question_id=q.id,
                    question_type=q.type,
                    score=config.score_rules.get(q.type, 5.0)
                )
        
        # 保存试卷
        self._save_paper(paper)
        
        return paper, ""
    
    def create_manual_paper(self, title: str, description: str = "", 
                           time_limit: int = 60) -> Paper:
        """手动创建空试卷"""
        paper = Paper(
            title=title,
            description=description,
            time_limit=time_limit
        )
        self._save_paper(paper)
        return paper
    
    def add_question_to_paper(self, paper_id: str, question_id: str, 
                              question_type: str, score: float = None) -> bool:
        """向试卷添加题目"""
        paper = self.get_paper(paper_id)
        if not paper:
            return False
        
        paper.add_question(question_id, question_type, score)
        self._save_paper(paper)
        return True
    
    def remove_question_from_paper(self, paper_id: str, question_id: str) -> bool:
        """从试卷移除题目"""
        paper = self.get_paper(paper_id)
        if not paper:
            return False
        
        if paper.remove_question(question_id):
            self._save_paper(paper)
            return True
        return False
    
    def update_paper(self, paper: Paper) -> bool:
        """更新试卷"""
        self._save_paper(paper)
        return True
    
    def get_paper_questions(self, paper_id: str) -> List[Question]:
        """获取试卷的所有题目对象"""
        paper = self.get_paper(paper_id)
        if not paper:
            return []
        
        questions = []
        # 收集所有相关题库，记录题目和题库的映射关系
        banks_cache = {}  # {question_id: (question, bank_id)}
        for bank_id in paper.source_banks:
            bank = self.bank_service.get_bank(bank_id)
            if bank:
                for q in bank.questions:
                    banks_cache[q.id] = (q, bank_id)
        
        # 如果没有记录来源题库，遍历所有题库
        if not banks_cache:
            all_banks = self.bank_service.get_all_banks()
            for bank in all_banks:
                for q in bank.questions:
                    banks_cache[q.id] = (q, bank.id)
        
        # 按顺序获取题目，并添加bank_id属性
        for pq in paper.questions:
            if pq.question_id in banks_cache:
                q, bank_id = banks_cache[pq.question_id]
                # 给题目添加bank_id属性
                q.bank_id = bank_id
                questions.append(q)
        
        return questions
    
    def duplicate_paper(self, paper_id: str, new_title: str = None) -> Optional[Paper]:
        """复制试卷"""
        original = self.get_paper(paper_id)
        if not original:
            return None
        
        import uuid
        from datetime import datetime
        
        new_paper = Paper(
            id=str(uuid.uuid4()),
            title=new_title or f"{original.title} - 副本",
            description=original.description,
            time_limit=original.time_limit,
            score_rules=original.score_rules.copy(),
            source_banks=original.source_banks.copy()
        )
        
        for pq in original.questions:
            new_paper.questions.append(PaperQuestion(
                order=pq.order,
                question_id=pq.question_id,
                score=pq.score,
                type=pq.type
            ))
        
        new_paper._recalculate_total_score()
        self._save_paper(new_paper)
        return new_paper
