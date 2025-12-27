"""
辅助函数
"""
import uuid
import re
from datetime import datetime
from typing import Optional


def generate_id() -> str:
    """生成唯一ID"""
    return str(uuid.uuid4())


def format_time(seconds: int) -> str:
    """
    格式化时间显示
    将秒数转换为 mm:ss 或 hh:mm:ss 格式
    """
    if seconds < 0:
        return "00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_datetime(dt: Optional[datetime | str] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间"""
    if dt is None:
        dt = datetime.now()
    elif isinstance(dt, str):
        try:
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
        except:
            return dt
    return dt.strftime(fmt)


def parse_datetime(dt_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """解析日期时间字符串"""
    try:
        return datetime.strptime(dt_str, fmt)
    except:
        return None


def safe_filename(name: str, max_length: int = 100) -> str:
    """
    将字符串转换为安全的文件名
    """
    # 移除非法字符
    illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
    safe = re.sub(illegal_chars, '_', name)
    
    # 移除首尾空格和点
    safe = safe.strip(' .')
    
    # 限制长度
    if len(safe) > max_length:
        safe = safe[:max_length]
    
    return safe or 'unnamed'


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_file_extension(filename: str) -> str:
    """获取文件扩展名（小写，不含点）"""
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[-1].lower()


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def calculate_score_rate(score: float, total: float) -> float:
    """计算得分率（百分比）"""
    if total <= 0:
        return 0.0
    return round(score / total * 100, 1)


def format_score_rate(rate: float) -> str:
    """格式化得分率显示"""
    return f"{rate:.1f}%"


def is_chinese(text: str) -> bool:
    """检查文本是否包含中文"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def extract_option_letter(option: str) -> str:
    """从选项文本中提取选项字母"""
    match = re.match(r'^([A-E])[\.、\s]', option)
    if match:
        return match.group(1).upper()
    return ''


def format_options_display(options: list[str]) -> list[str]:
    """格式化选项显示"""
    formatted = []
    letters = 'ABCDE'
    
    for i, opt in enumerate(options):
        if i >= len(letters):
            break
        
        opt_text = opt.strip()
        # 检查是否已有前缀
        if re.match(r'^[A-E][\.、\s]', opt_text):
            formatted.append(opt_text)
        else:
            formatted.append(f"{letters[i]}. {opt_text}")
    
    return formatted


def normalize_answer(answer, q_type: str):
    """规范化答案格式"""
    if q_type == 'single':
        return str(answer).upper().strip() if answer else ''
    
    elif q_type == 'multiple':
        if isinstance(answer, str):
            # 移除分隔符并转为列表
            answer = re.sub(r'[,，、\s]', '', answer.upper())
            return sorted(list(set(answer)))
        elif isinstance(answer, list):
            return sorted([str(a).upper().strip() for a in answer])
        return []
    
    elif q_type == 'judge':
        if isinstance(answer, bool):
            return answer
        if isinstance(answer, str):
            return answer.strip().lower() in ['true', '对', '正确', 't', '√', '1', 'yes']
        return bool(answer)
    
    return answer


def compare_answers(user_answer, correct_answer, q_type: str) -> bool:
    """比较答案是否正确"""
    user = normalize_answer(user_answer, q_type)
    correct = normalize_answer(correct_answer, q_type)
    
    if q_type == 'multiple':
        return set(user) == set(correct)
    
    return user == correct
