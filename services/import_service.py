"""
导入服务 - 处理各种格式的题目导入
"""
import json
import re
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

from models import Question


class ImportService:
    """导入服务类"""
    
    def import_from_json(self, file_path: str) -> Tuple[List[Question], str]:
        """
        从JSON文件导入题目
        返回: (题目列表, 错误消息)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            questions = []
            
            # 支持多种JSON结构
            if isinstance(data, list):
                items = data
            elif 'questions' in data:
                items = data['questions']
            else:
                items = [data]
            
            for item in items:
                try:
                    q = Question.from_dict(item)
                    q.source = 'imported'
                    questions.append(q)
                except Exception as e:
                    print(f"解析题目失败: {e}")
                    continue
            
            if not questions:
                return [], "未能解析出任何题目"
            
            return questions, ""
            
        except json.JSONDecodeError as e:
            return [], f"JSON格式错误: {e}"
        except Exception as e:
            return [], f"导入失败: {e}"
    
    def import_from_excel(self, file_path: str) -> Tuple[List[Question], str]:
        """
        从Excel文件导入题目
        
        Excel格式要求:
        | 类型 | 题目内容 | 选项A | 选项B | 选项C | 选项D | 答案 | 解析 | 难度 | 标签 |
        
        返回: (题目列表, 错误消息)
        """
        try:
            import pandas as pd
            
            df = pd.read_excel(file_path)
            
            # 列名映射
            column_map = {
                '类型': 'type',
                '题目': 'question',
                '题目内容': 'question',
                '选项A': 'optionA',
                '选项B': 'optionB',
                '选项C': 'optionC',
                '选项D': 'optionD',
                '选项E': 'optionE',
                '答案': 'answer',
                '正确答案': 'answer',
                '解析': 'explanation',
                '答案解析': 'explanation',
                '难度': 'difficulty',
                '标签': 'tags'
            }
            
            df.rename(columns=column_map, inplace=True)
            
            questions = []
            
            for _, row in df.iterrows():
                try:
                    # 获取题目类型
                    q_type = str(row.get('type', 'single')).lower().strip()
                    type_map = {
                        '单选': 'single',
                        '单选题': 'single',
                        'single': 'single',
                        '多选': 'multiple',
                        '多选题': 'multiple',
                        'multiple': 'multiple',
                        '判断': 'judge',
                        '判断题': 'judge',
                        'judge': 'judge',
                        '填空': 'fill',
                        '填空题': 'fill',
                        'fill': 'fill'
                    }
                    q_type = type_map.get(q_type, 'single')
                    
                    # 获取题目内容
                    question_text = str(row.get('question', '')).strip()
                    if not question_text:
                        continue
                    
                    # 获取选项
                    options = []
                    for opt_key in ['optionA', 'optionB', 'optionC', 'optionD', 'optionE']:
                        opt = row.get(opt_key)
                        if pd.notna(opt) and str(opt).strip():
                            opt_text = str(opt).strip()
                            # 添加选项前缀（如果没有）
                            prefix = opt_key[-1]
                            if not opt_text.startswith(f'{prefix}.') and not opt_text.startswith(f'{prefix}、'):
                                opt_text = f'{prefix}. {opt_text}'
                            options.append(opt_text)
                    
                    # 获取答案
                    answer = row.get('answer', '')
                    if pd.notna(answer):
                        answer = str(answer).strip().upper()
                        # 处理多选答案
                        if q_type == 'multiple' and len(answer) > 1:
                            answer = list(answer.replace(',', '').replace('，', '').replace(' ', ''))
                        # 处理判断题答案
                        if q_type == 'judge':
                            answer = answer in ['对', '正确', 'TRUE', 'T', '√', '1', 'YES']
                    else:
                        answer = '' if q_type != 'judge' else False
                    
                    # 获取解析
                    explanation = ''
                    if 'explanation' in row and pd.notna(row['explanation']):
                        explanation = str(row['explanation']).strip()
                    
                    # 获取难度
                    difficulty = 3
                    if 'difficulty' in row and pd.notna(row['difficulty']):
                        try:
                            difficulty = int(row['difficulty'])
                            difficulty = max(1, min(5, difficulty))
                        except:
                            pass
                    
                    # 获取标签
                    tags = []
                    if 'tags' in row and pd.notna(row['tags']):
                        tags_str = str(row['tags']).strip()
                        tags = [t.strip() for t in re.split(r'[,，;；]', tags_str) if t.strip()]
                    
                    q = Question(
                        type=q_type,
                        question=question_text,
                        options=options if q_type in ['single', 'multiple'] else [],
                        answer=answer,
                        explanation=explanation,
                        difficulty=difficulty,
                        tags=tags,
                        source='imported'
                    )
                    questions.append(q)
                    
                except Exception as e:
                    print(f"解析Excel行失败: {e}")
                    continue
            
            if not questions:
                return [], "未能解析出任何题目，请检查Excel格式"
            
            return questions, ""
            
        except ImportError:
            return [], "请安装pandas和openpyxl库: pip install pandas openpyxl"
        except Exception as e:
            return [], f"导入Excel失败: {e}"
    
    def import_from_csv(self, file_path: str) -> Tuple[List[Question], str]:
        """从CSV文件导入题目"""
        try:
            import pandas as pd
            
            # 尝试不同编码
            for encoding in ['utf-8', 'gbk', 'gb2312']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except:
                    continue
            else:
                return [], "无法读取CSV文件，请检查文件编码"
            
            # 保存为临时Excel然后使用Excel导入逻辑
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
                df.to_excel(tmp.name, index=False)
                return self.import_from_excel(tmp.name)
                
        except ImportError:
            return [], "请安装pandas库: pip install pandas"
        except Exception as e:
            return [], f"导入CSV失败: {e}"
    
    def import_from_word(self, file_path: str) -> Tuple[List[Question], str]:
        """
        从Word文档导入题目
        
        支持的格式：
        1. 单选题
        题目内容
        A. 选项A
        B. 选项B
        C. 选项C
        D. 选项D
        答案：A
        
        返回: (题目列表, 错误消息)
        """
        try:
            from docx import Document
            
            doc = Document(file_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
            
            return self._parse_text_format(text)
            
        except ImportError:
            return [], "请安装python-docx库: pip install python-docx"
        except Exception as e:
            return [], f"导入Word失败: {e}"
    
    def import_from_text(self, text: str) -> Tuple[List[Question], str]:
        """从纯文本导入题目"""
        return self._parse_text_format(text)
    
    def _parse_text_format(self, text: str) -> Tuple[List[Question], str]:
        """
        解析文本格式的题目
        """
        questions = []
        
        # 按题目编号分割
        # 匹配: 1. 或 1、或 第1题 或 一、等
        pattern = r'(?:^|\n)(?:\d+[\.、]|第\d+题|[一二三四五六七八九十]+[\.、])'
        parts = re.split(pattern, text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            q = self._parse_single_question(part)
            if q:
                questions.append(q)
        
        # 如果按编号分割没有结果，尝试按空行分割
        if not questions:
            parts = re.split(r'\n\s*\n', text)
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                q = self._parse_single_question(part)
                if q:
                    questions.append(q)
        
        if not questions:
            return [], "未能解析出任何题目，请检查文本格式"
        
        return questions, ""
    
    def _parse_single_question(self, text: str) -> Optional[Question]:
        """解析单道题目"""
        lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
        
        if not lines:
            return None
        
        # 检测题目类型
        q_type = 'single'
        type_patterns = {
            'single': r'单选|单项选择',
            'multiple': r'多选|多项选择',
            'judge': r'判断',
            'fill': r'填空'
        }
        
        first_line = lines[0]
        for t, pattern in type_patterns.items():
            if re.search(pattern, first_line):
                q_type = t
                lines = lines[1:]  # 移除类型标识行
                break
        
        if not lines:
            return None
        
        # 提取题目内容和选项
        question_text = ""
        options = []
        answer = ""
        explanation = ""
        
        option_pattern = r'^([A-E])[\.、\s](.+)$'
        answer_pattern = r'^(?:答案|正确答案)[：:]\s*(.+)$'
        explanation_pattern = r'^(?:解析|答案解析)[：:]\s*(.+)$'
        
        i = 0
        # 获取题目内容（直到遇到选项或答案）
        while i < len(lines):
            line = lines[i]
            if re.match(option_pattern, line) or re.match(answer_pattern, line):
                break
            question_text += line + " "
            i += 1
        
        question_text = question_text.strip()
        
        # 获取选项
        while i < len(lines):
            line = lines[i]
            match = re.match(option_pattern, line)
            if match:
                opt_letter = match.group(1)
                opt_content = match.group(2).strip()
                options.append(f"{opt_letter}. {opt_content}")
                i += 1
            else:
                break
        
        # 获取答案和解析
        while i < len(lines):
            line = lines[i]
            
            ans_match = re.match(answer_pattern, line, re.IGNORECASE)
            if ans_match:
                answer = ans_match.group(1).strip().upper()
                i += 1
                continue
            
            exp_match = re.match(explanation_pattern, line, re.IGNORECASE)
            if exp_match:
                explanation = exp_match.group(1).strip()
                i += 1
                continue
            
            i += 1
        
        if not question_text:
            return None
        
        # 处理多选答案
        if q_type == 'multiple' and answer:
            answer = list(answer.replace(',', '').replace('，', '').replace(' ', ''))
        
        # 处理判断题
        if q_type == 'judge':
            answer = answer in ['对', '正确', 'TRUE', 'T', '√', '1', 'YES', 'A']
        
        return Question(
            type=q_type,
            question=question_text,
            options=options,
            answer=answer,
            explanation=explanation,
            difficulty=3,
            source='imported'
        )
    
    def get_import_template_excel(self, output_path: str) -> bool:
        """生成Excel导入模板"""
        try:
            import pandas as pd
            
            data = {
                '类型': ['单选', '多选', '判断'],
                '题目内容': [
                    'Python中哪个关键字用于定义函数？',
                    '以下哪些是Python的数据类型？',
                    'Python是一种解释型语言。'
                ],
                '选项A': ['def', 'int', ''],
                '选项B': ['func', 'str', ''],
                '选项C': ['function', 'list', ''],
                '选项D': ['define', 'dict', ''],
                '答案': ['A', 'ABCD', '对'],
                '解析': [
                    'Python使用def关键字定义函数',
                    'int、str、list、dict都是Python内置数据类型',
                    'Python代码在执行时由解释器逐行解释执行'
                ],
                '难度': [2, 3, 1],
                '标签': ['Python基础', 'Python基础,数据类型', 'Python基础']
            }
            
            df = pd.DataFrame(data)
            df.to_excel(output_path, index=False)
            return True
            
        except Exception as e:
            print(f"生成模板失败: {e}")
            return False
