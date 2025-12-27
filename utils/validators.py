"""
数据验证工具
"""
import re
from typing import List, Any, Optional


class Validators:
    """数据验证工具类"""
    
    @staticmethod
    def is_not_empty(value: Any) -> bool:
        """检查值是否非空"""
        if value is None:
            return False
        if isinstance(value, str):
            return len(value.strip()) > 0
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """验证URL格式"""
        pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def is_valid_api_key(api_key: str, provider: str = "openai") -> bool:
        """验证API Key格式"""
        if not api_key or len(api_key) < 10:
            return False
        
        if provider == "openai":
            # OpenAI API Key 通常以 sk- 开头
            return api_key.startswith("sk-") and len(api_key) > 20
        
        return True  # 其他提供商暂不做格式验证
    
    @staticmethod
    def is_in_range(value: int | float, min_val: int | float, max_val: int | float) -> bool:
        """检查数值是否在范围内"""
        return min_val <= value <= max_val
    
    @staticmethod
    def is_valid_question_type(q_type: str) -> bool:
        """验证题目类型"""
        valid_types = ['single', 'multiple', 'judge', 'fill', 'essay']
        return q_type in valid_types
    
    @staticmethod
    def is_valid_answer(answer: Any, q_type: str, options: List[str] = None) -> tuple[bool, str]:
        """
        验证答案格式
        返回: (是否有效, 错误消息)
        """
        if q_type == 'single':
            if not isinstance(answer, str):
                return False, "单选题答案必须是字符串"
            if options and answer.upper() not in [opt[0].upper() for opt in options if opt]:
                return False, "答案必须是有效的选项字母"
            return True, ""
        
        elif q_type == 'multiple':
            if not isinstance(answer, (list, str)):
                return False, "多选题答案必须是列表或字符串"
            if isinstance(answer, str):
                answer = list(answer.upper())
            if options:
                valid_letters = [opt[0].upper() for opt in options if opt]
                for a in answer:
                    if a.upper() not in valid_letters:
                        return False, f"无效的选项: {a}"
            return True, ""
        
        elif q_type == 'judge':
            if not isinstance(answer, bool):
                return False, "判断题答案必须是布尔值"
            return True, ""
        
        elif q_type in ['fill', 'essay']:
            if not isinstance(answer, str):
                return False, "填空题/简答题答案必须是字符串"
            return True, ""
        
        return False, f"未知的题目类型: {q_type}"
    
    @staticmethod
    def is_valid_difficulty(difficulty: int) -> bool:
        """验证难度等级"""
        return isinstance(difficulty, int) and 1 <= difficulty <= 5
    
    @staticmethod
    def validate_question_data(data: dict) -> tuple[bool, str]:
        """
        验证题目数据完整性
        返回: (是否有效, 错误消息)
        """
        # 检查必填字段
        if not data.get('question'):
            return False, "题目内容不能为空"
        
        q_type = data.get('type', 'single')
        if not Validators.is_valid_question_type(q_type):
            return False, f"无效的题目类型: {q_type}"
        
        # 选择题需要选项
        if q_type in ['single', 'multiple']:
            options = data.get('options', [])
            if len(options) < 2:
                return False, "选择题至少需要2个选项"
        
        # 验证答案
        answer = data.get('answer')
        if answer is not None:
            valid, msg = Validators.is_valid_answer(
                answer, q_type, data.get('options', [])
            )
            if not valid:
                return False, msg
        
        # 验证难度
        difficulty = data.get('difficulty', 3)
        if not Validators.is_valid_difficulty(difficulty):
            return False, "难度等级必须在1-5之间"
        
        return True, ""
    
    @staticmethod
    def validate_bank_data(data: dict) -> tuple[bool, str]:
        """
        验证题库数据
        返回: (是否有效, 错误消息)
        """
        if not data.get('name', '').strip():
            return False, "题库名称不能为空"
        
        return True, ""
    
    @staticmethod
    def validate_paper_data(data: dict) -> tuple[bool, str]:
        """
        验证试卷数据
        返回: (是否有效, 错误消息)
        """
        if not data.get('title', '').strip():
            return False, "试卷标题不能为空"
        
        questions = data.get('questions', [])
        if len(questions) == 0:
            return False, "试卷至少需要一道题目"
        
        return True, ""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名，移除非法字符"""
        # 移除Windows和Unix文件名非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        cleaned = re.sub(illegal_chars, '_', filename)
        # 移除控制字符
        cleaned = re.sub(r'[\x00-\x1f\x7f]', '', cleaned)
        # 限制长度
        if len(cleaned) > 200:
            cleaned = cleaned[:200]
        return cleaned.strip() or 'unnamed'
