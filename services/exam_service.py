"""
答题与评分服务
"""
import json
from pathlib import Path
from typing import List, Optional, Dict, Union
from datetime import datetime

from config import RESULTS_DIR, config as app_config
from models import Paper, Question, ExamResult, QuestionResult
from services.paper_service import PaperService


class ExamService:
    """答题与评分服务类"""
    
    def __init__(self):
        self.paper_service = PaperService()
        self._current_exam: Optional[ExamResult] = None
        self._current_paper: Optional[Paper] = None
        self._questions_cache: Dict[str, Question] = {}
    
    def _get_results_dir(self) -> Path:
        """获取成绩存储目录（动态读取配置）"""
        custom_dir = app_config.path_config.results_dir
        if custom_dir:
            path = Path(custom_dir)
            path.mkdir(parents=True, exist_ok=True)
            return path
        return RESULTS_DIR
    
    def _get_result_file(self, result_id: str) -> Path:
        """获取结果文件路径"""
        return self._get_results_dir() / f"result_{result_id}.json"
    
    def _save_result(self, result: ExamResult):
        """保存答题结果"""
        file_path = self._get_result_file(result.id)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
    
    def start_exam(self, paper_id: str) -> Optional[ExamResult]:
        """
        开始答题
        返回考试结果对象用于记录答题
        """
        paper = self.paper_service.get_paper(paper_id)
        if not paper:
            return None
        
        # 获取题目
        questions = self.paper_service.get_paper_questions(paper_id)
        if not questions:
            return None
        
        # 缓存题目
        self._questions_cache = {q.id: q for q in questions}
        self._current_paper = paper
        
        # 创建考试结果
        self._current_exam = ExamResult(
            paper_id=paper_id,
            paper_title=paper.title,
            total_score=paper.total_score,
            status="in_progress"
        )
        
        # 初始化每道题的结果记录
        for pq in paper.questions:
            if pq.question_id in self._questions_cache:
                q = self._questions_cache[pq.question_id]
                qr = QuestionResult(
                    question_id=pq.question_id,
                    question_type=pq.type,
                    correct_answer=q.answer,
                    max_score=pq.score
                )
                self._current_exam.details.append(qr)
        
        # 自动保存
        self._save_result(self._current_exam)
        
        return self._current_exam
    
    def get_current_exam(self) -> Optional[ExamResult]:
        """获取当前考试"""
        return self._current_exam
    
    def get_current_paper(self) -> Optional[Paper]:
        """获取当前试卷"""
        return self._current_paper
    
    def get_question(self, question_id: str) -> Optional[Question]:
        """获取题目"""
        return self._questions_cache.get(question_id)
    
    def get_all_questions(self) -> List[Question]:
        """获取所有题目（按顺序）"""
        if not self._current_paper:
            return []
        
        questions = []
        for pq in self._current_paper.questions:
            if pq.question_id in self._questions_cache:
                questions.append(self._questions_cache[pq.question_id])
        return questions
    
    def submit_answer(self, question_id: str, answer: Union[str, List[str], bool]):
        """
        提交单题答案
        """
        if not self._current_exam:
            return
        
        for qr in self._current_exam.details:
            if qr.question_id == question_id:
                qr.user_answer = answer
                break
        
        # 自动保存
        if app_config.app_config.auto_save:
            self._save_result(self._current_exam)
    
    def finish_exam(self, timeout: bool = False) -> ExamResult:
        """
        完成答题并评分
        """
        if not self._current_exam:
            return None
        
        # 评分
        for qr in self._current_exam.details:
            if qr.user_answer is None:
                qr.is_correct = False
                qr.score = 0
                continue
            
            q = self._questions_cache.get(qr.question_id)
            if q:
                is_correct, score_ratio = q.check_answer(qr.user_answer)
                qr.is_correct = is_correct
                
                # 多选题部分得分处理
                if q.type == 'multiple' and not app_config.app_config.multiple_partial_score:
                    qr.score = qr.max_score if is_correct else 0
                else:
                    qr.score = qr.max_score * score_ratio
        
        # 完成考试
        if timeout:
            self._current_exam.timeout()
        else:
            self._current_exam.complete()
        
        # 保存结果
        self._save_result(self._current_exam)
        
        result = self._current_exam
        
        # 清理状态
        self._current_exam = None
        self._current_paper = None
        self._questions_cache = {}
        
        return result
    
    def get_result(self, result_id: str) -> Optional[ExamResult]:
        """获取答题结果"""
        file_path = self._get_result_file(result_id)
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ExamResult.from_dict(data)
        except Exception as e:
            print(f"加载答题结果失败: {e}")
            return None
    
    def get_all_results(self) -> List[ExamResult]:
        """获取所有答题结果"""
        results = []
        results_dir = self._get_results_dir()
        for file_path in results_dir.glob("result_*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                results.append(ExamResult.from_dict(data))
            except:
                continue
        return sorted(results, key=lambda r: r.start_time, reverse=True)
    
    def delete_result(self, result_id: str) -> bool:
        """删除答题结果"""
        file_path = self._get_result_file(result_id)
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def get_result_with_questions(self, result_id: str) -> tuple[Optional[ExamResult], Dict[str, Question]]:
        """
        获取答题结果及对应的题目
        用于结果展示页面
        """
        result = self.get_result(result_id)
        if not result:
            return None, {}
        
        # 获取试卷和题目
        paper = self.paper_service.get_paper(result.paper_id)
        if not paper:
            return result, {}
        
        questions = self.paper_service.get_paper_questions(result.paper_id)
        questions_dict = {q.id: q for q in questions}
        
        return result, questions_dict
    
    def get_wrong_questions(self, result_id: str) -> List[tuple[Question, QuestionResult]]:
        """获取错题列表"""
        result, questions = self.get_result_with_questions(result_id)
        if not result:
            return []
        
        wrong_list = []
        for qr in result.details:
            if not qr.is_correct and qr.question_id in questions:
                wrong_list.append((questions[qr.question_id], qr))
        
        return wrong_list
    
    def get_statistics_summary(self) -> Dict:
        """获取答题统计摘要"""
        results = self.get_all_results()
        
        summary = {
            'total_exams': len(results),
            'completed_exams': 0,
            'total_questions': 0,
            'correct_questions': 0,
            'average_score_rate': 0.0,
            'recent_results': []
        }
        
        completed_results = [r for r in results if r.status == 'completed']
        summary['completed_exams'] = len(completed_results)
        
        if completed_results:
            total_rate = 0
            for r in completed_results:
                stats = r.get_statistics()
                summary['total_questions'] += stats['total_questions']
                summary['correct_questions'] += stats['correct_count']
                total_rate += stats['score_rate']
            
            summary['average_score_rate'] = total_rate / len(completed_results)
        
        # 最近5次结果
        summary['recent_results'] = results[:5]
        
        return summary
