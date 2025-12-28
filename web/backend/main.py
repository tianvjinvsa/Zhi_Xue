"""
智题坊 - Web API 服务
"""
import sys
import os
import tempfile
import httpx
import json
import shutil
import asyncio
from pathlib import Path
from datetime import datetime
from asyncio.proactor_events import _ProactorBasePipeTransport

# 修复 Windows 下 asyncio 的 ConnectionResetError [WinError 10054]
# 这通常发生在客户端强制关闭连接时，ProactorEventLoop 会抛出此异常
if sys.platform == 'win32':
    _backup_call_connection_lost = _ProactorBasePipeTransport._call_connection_lost
    def _patched_call_connection_lost(self, exc):
        if isinstance(exc, ConnectionResetError):
            return
        _backup_call_connection_lost(self, exc)
    _ProactorBasePipeTransport._call_connection_lost = _patched_call_connection_lost

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Union, Dict

from config import DATA_DIR, BANKS_DIR, PAPERS_DIR, RESULTS_DIR
from config import config as app_config
from services.bank_service import BankService
from services.paper_service import PaperService, PaperGenerateConfig
from services.exam_service import ExamService
from services.ai_service import AIService
from services.favorite_service import FavoriteService
from models import Question, QuestionBank

# 当前版本号
CURRENT_VERSION = "1.0.0"
GITHUB_RELEASES_API = "https://api.github.com/repos/K-zhaochao/AnswerSystem/releases/latest"

# 确保数据目录存在
for dir_path in [DATA_DIR, BANKS_DIR, PAPERS_DIR, RESULTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="智题坊 API",
    description="基于 Vue 3 + Element Plus + FastAPI 的智题坊",
    version=CURRENT_VERSION
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
bank_service = BankService()
paper_service = PaperService()
exam_service = ExamService()
ai_service = AIService()
favorite_service = FavoriteService()


# ============ Pydantic 模型 ============

class QuestionCreate(BaseModel):
    type: str = "single"
    question: str
    options: List[str] = []
    answer: Union[str, List[str], bool] = ""
    explanation: str = ""
    difficulty: int = 3
    tags: List[str] = []


class QuestionUpdate(BaseModel):
    type: Optional[str] = None
    question: Optional[str] = None
    options: Optional[List[str]] = None
    answer: Optional[Union[str, List[str], bool]] = None
    explanation: Optional[str] = None
    difficulty: Optional[int] = None
    tags: Optional[List[str]] = None


class BatchQuestionCreate(BaseModel):
    questions: List[QuestionCreate]


class BankCreate(BaseModel):
    name: str
    description: str = ""
    subject: str = ""


class BankUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None


class PaperGenerateRequest(BaseModel):
    title: str = "新试卷"
    description: str = ""
    time_limit: int = 60
    bank_ids: List[str] = []
    single_count: int = 10
    multiple_count: int = 5
    judge_count: int = 5
    fill_count: int = 0
    min_difficulty: int = 1
    max_difficulty: int = 5
    tags: List[str] = []
    score_rules: Optional[Dict[str, float]] = None


class AnswerSubmit(BaseModel):
    question_id: str
    answer: Union[str, List[str], bool]


class AIGenerateRequest(BaseModel):
    topic: str
    count: int = 5
    type_distribution: str = "单选题为主，适当加入多选题和判断题"
    difficulty_min: int = 1
    difficulty_max: int = 5


class AIParseRequest(BaseModel):
    content: str


class AIConfigUpdate(BaseModel):
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    vision_model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class PathConfigUpdate(BaseModel):
    banks_dir: Optional[str] = None
    papers_dir: Optional[str] = None
    results_dir: Optional[str] = None
    favorites_file: Optional[str] = None


class ExportRequest(BaseModel):
    export_path: str
    include_banks: bool = True
    include_papers: bool = True
    include_results: bool = True
    include_favorites: bool = True
    include_ai_config: bool = True


class ImportRequest(BaseModel):
    import_path: str
    include_banks: bool = True
    include_papers: bool = True
    include_results: bool = True
    include_favorites: bool = True
    include_ai_config: bool = True


# ============ 题库 API ============

@app.get("/api/banks")
def get_all_banks():
    """获取所有题库列表"""
    return bank_service.get_banks_summary()


@app.post("/api/banks")
def create_bank(data: BankCreate):
    """创建新题库"""
    bank = bank_service.create_bank(
        name=data.name,
        description=data.description,
        subject=data.subject
    )
    return {"id": bank.id, "message": "创建成功"}


@app.get("/api/banks/{bank_id}")
def get_bank(bank_id: str):
    """获取题库详情"""
    bank = bank_service.get_bank(bank_id)
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    return bank.to_dict()


@app.put("/api/banks/{bank_id}")
def update_bank(bank_id: str, data: BankUpdate):
    """更新题库信息"""
    bank = bank_service.get_bank(bank_id)
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    if data.name is not None:
        bank.name = data.name
    if data.description is not None:
        bank.description = data.description
    if data.subject is not None:
        bank.subject = data.subject
    
    bank_service.update_bank(bank)
    return {"message": "更新成功"}


@app.delete("/api/banks/{bank_id}")
def delete_bank(bank_id: str):
    """删除题库"""
    if bank_service.delete_bank(bank_id):
        return {"message": "删除成功"}
    raise HTTPException(status_code=404, detail="题库不存在")


# ============ 题目 API ============

@app.get("/api/banks/{bank_id}/questions")
def get_bank_questions(bank_id: str):
    """获取题库中的所有题目"""
    bank = bank_service.get_bank(bank_id)
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    return [q.to_dict() for q in bank.questions]


@app.post("/api/banks/{bank_id}/questions")
def add_question(bank_id: str, data: QuestionCreate):
    """向题库添加题目"""
    question = Question(
        type=data.type,
        question=data.question,
        options=data.options,
        answer=data.answer,
        explanation=data.explanation,
        difficulty=data.difficulty,
        tags=data.tags
    )
    
    if bank_service.add_question_to_bank(bank_id, question):
        return {"id": question.id, "message": "添加成功"}
    raise HTTPException(status_code=400, detail="添加失败")


@app.post("/api/banks/{bank_id}/questions/batch")
def batch_add_questions(bank_id: str, data: BatchQuestionCreate):
    """批量向题库添加题目"""
    count = 0
    for q_data in data.questions:
        question = Question(
            type=q_data.type,
            question=q_data.question,
            options=q_data.options,
            answer=q_data.answer,
            explanation=q_data.explanation,
            difficulty=q_data.difficulty,
            tags=q_data.tags
        )
        if bank_service.add_question_to_bank(bank_id, question):
            count += 1
    
    return {"count": count, "message": f"成功添加 {count} 道题目"}


@app.put("/api/banks/{bank_id}/questions/{question_id}")
def update_question(bank_id: str, question_id: str, data: QuestionUpdate):
    """更新题目"""
    bank = bank_service.get_bank(bank_id)
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在")
    
    question = bank.get_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    if data.type is not None:
        question.type = data.type
    if data.question is not None:
        question.question = data.question
    if data.options is not None:
        question.options = data.options
    if data.answer is not None:
        question.answer = data.answer
    if data.explanation is not None:
        question.explanation = data.explanation
    if data.difficulty is not None:
        question.difficulty = data.difficulty
    if data.tags is not None:
        question.tags = data.tags
    
    bank_service.update_bank(bank)
    return {"message": "更新成功"}


@app.delete("/api/banks/{bank_id}/questions/{question_id}")
def delete_question(bank_id: str, question_id: str):
    """删除题目"""
    if bank_service.remove_question_from_bank(bank_id, question_id):
        return {"message": "删除成功"}
    raise HTTPException(status_code=404, detail="删除失败")


# ============ 试卷 API ============

@app.get("/api/papers")
def get_all_papers():
    """获取所有试卷"""
    papers = paper_service.get_all_papers()
    return [{
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "created_at": p.created_at,
        "time_limit": p.time_limit,
        "total_score": p.total_score,
        "question_count": len(p.questions)
    } for p in papers]


@app.get("/api/papers/{paper_id}")
def get_paper(paper_id: str):
    """获取试卷详情"""
    paper = paper_service.get_paper(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    return paper.to_dict()


@app.get("/api/papers/{paper_id}/questions")
def get_paper_questions(paper_id: str):
    """获取试卷的所有题目"""
    questions = paper_service.get_paper_questions(paper_id)
    if questions is None:
        raise HTTPException(status_code=404, detail="试卷不存在")
    return [q.to_dict() for q in questions]


@app.post("/api/papers/generate")
def generate_paper(data: PaperGenerateRequest):
    """生成试卷"""
    config = PaperGenerateConfig(
        title=data.title,
        description=data.description,
        time_limit=data.time_limit,
        bank_ids=data.bank_ids,
        single_count=data.single_count,
        multiple_count=data.multiple_count,
        judge_count=data.judge_count,
        fill_count=data.fill_count,
        min_difficulty=data.min_difficulty,
        max_difficulty=data.max_difficulty,
        tags=data.tags,
        score_rules=data.score_rules
    )
    
    paper, error = paper_service.generate_paper(config)
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return {"id": paper.id, "message": "生成成功", "paper": paper.to_dict()}


@app.delete("/api/papers/{paper_id}")
def delete_paper(paper_id: str):
    """删除试卷"""
    if paper_service.delete_paper(paper_id):
        return {"message": "删除成功"}
    raise HTTPException(status_code=404, detail="试卷不存在")


# ============ 考试 API ============

@app.post("/api/exam/start/{paper_id}")
def start_exam(paper_id: str):
    """开始考试"""
    result = exam_service.start_exam(paper_id)
    if not result:
        raise HTTPException(status_code=400, detail="无法开始考试")
    return {
        "exam_id": result.id,
        "paper_title": result.paper_title,
        "total_score": result.total_score
    }


@app.post("/api/exam/{exam_id}/answer")
def submit_answer(exam_id: str, data: AnswerSubmit):
    """提交答案"""
    exam_service.submit_answer(data.question_id, data.answer)
    return {"message": "提交成功"}


@app.post("/api/exam/{exam_id}/submit")
def finish_exam(exam_id: str):
    """完成考试"""
    result = exam_service.finish_exam()
    if not result:
        raise HTTPException(status_code=400, detail="无法完成考试")
    return result.to_dict()


@app.get("/api/results")
def get_all_results():
    """获取所有考试记录"""
    results = exam_service.get_all_results()
    return [{
        "id": r.id,
        "paper_title": r.paper_title,
        "user_score": r.user_score,
        "total_score": r.total_score,
        "start_time": r.start_time,
        "end_time": r.end_time,
        "status": r.status
    } for r in results]


@app.get("/api/results/{result_id}")
def get_result(result_id: str):
    """获取考试结果详情"""
    result = exam_service.get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="记录不存在")
    return result.to_dict()


@app.delete("/api/results/{result_id}")
def delete_result(result_id: str):
    """删除考试记录"""
    if exam_service.delete_result(result_id):
        return {"message": "删除成功"}
    raise HTTPException(status_code=404, detail="记录不存在")


# ============ AI API ============

@app.post("/api/ai/parse")
def ai_parse_questions(data: AIParseRequest):
    """AI解析题目"""
    questions, error = ai_service.parse_questions_from_text(data.content)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"questions": [q.to_dict() for q in questions]}


@app.post("/api/ai/parse-file")
async def ai_parse_file(file: UploadFile = File(...)):
    """AI解析文件中的题目（支持 Word、Excel、TXT、图片）"""
    # 检查文件类型
    allowed_extensions = ['.txt', '.doc', '.docx', '.xls', '.xlsx', '.png', '.jpg', '.jpeg', '.gif', '.webp']
    
    # 获取文件扩展名
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()
    
    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件格式: {suffix}。支持的格式: {', '.join(allowed_extensions)}"
        )
    
    # 保存临时文件
    temp_file = None
    try:
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        # 解析文件
        questions, error = ai_service.parse_questions_from_file(temp_file.name)
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        return {"questions": [q.to_dict() for q in questions]}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")
    finally:
        # 清理临时文件
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass


@app.get("/api/ai/supported-types")
def get_supported_file_types():
    """获取支持的文件类型"""
    types = ai_service.get_supported_file_types()
    return {
        "types": types,
        "all_extensions": [ext for exts in types.values() for ext in exts]
    }


@app.post("/api/ai/generate")
def ai_generate_questions(data: AIGenerateRequest):
    """AI生成题目"""
    questions, error = ai_service.generate_questions(
        topic=data.topic,
        count=data.count,
        type_distribution=data.type_distribution,
        difficulty_range=(data.difficulty_min, data.difficulty_max)
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"questions": [q.to_dict() for q in questions]}


@app.get("/api/ai/check")
def check_ai_connection(
    api_base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
):
    """检查AI连接，支持使用临时配置测试"""
    temp_config = None
    if api_base_url or api_key or model:
        temp_config = {
            "api_base_url": api_base_url,
            "api_key": api_key,
            "model": model
        }
    success, message = ai_service.check_connection(temp_config)
    return {"success": success, "message": message}


@app.get("/api/system/select-folder")
def select_folder():
    """打开文件夹选择对话框"""
    try:
        import subprocess
        
        # 使用 PowerShell 脚本打开文件夹选择对话框，避免打包后 tkinter 失效的问题
        ps_script = """
        Add-Type -AssemblyName System.Windows.Forms
        $f = New-Object System.Windows.Forms.FolderBrowserDialog
        $f.Description = "选择文件夹"
        $f.ShowNewFolderButton = $true
        if ($f.ShowDialog() -eq "OK") {
            Write-Host "__RESULT__:$($f.SelectedPath)"
        }
        """
        
        # Windows下隐藏控制台窗口
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script], 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            startupinfo=startupinfo,
            timeout=60
        )
        
        # 从输出中提取路径
        path = ""
        for line in result.stdout.splitlines():
            if line.startswith("__RESULT__:"):
                path = line.replace("__RESULT__:", "").strip()
                break
            
        return {"path": path}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="文件夹选择超时")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"无法打开文件夹选择框: {str(e)}")


@app.get("/api/system/select-file")
def select_file(title: str = "选择文件", filetypes: str = "所有文件 (*.*)|*.*"):
    """打开文件选择对话框"""
    try:
        import subprocess
        
        # 使用 PowerShell 脚本打开文件选择对话框
        # filetypes 格式: "JSON文件 (*.json)|*.json|所有文件 (*.*)|*.*"
        ps_script = f"""
        Add-Type -AssemblyName System.Windows.Forms
        $f = New-Object System.Windows.Forms.OpenFileDialog
        $f.Title = "{title}"
        $f.Filter = "{filetypes}"
        if ($f.ShowDialog() -eq "OK") {{
            Write-Host "__RESULT__:$($f.FileName)"
        }}
        """
        
        # Windows下隐藏控制台窗口
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script], 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            startupinfo=startupinfo,
            timeout=60
        )
        
        # 从输出中提取路径
        path = ""
        for line in result.stdout.splitlines():
            if line.startswith("__RESULT__:"):
                path = line.replace("__RESULT__:", "").strip()
                break
            
        return {"path": path}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="文件选择超时")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"无法打开文件选择框: {str(e)}")


# ============ 收藏 API ============

@app.get("/api/favorites")
def get_all_favorites():
    """获取所有收藏"""
    favorites = favorite_service.get_all_favorites()
    return [fav.to_dict() for fav in favorites]


@app.get("/api/favorites/statistics")
def get_favorites_statistics():
    """获取收藏统计"""
    return favorite_service.get_statistics()


@app.get("/api/favorites/banks")
def get_banks_with_favorites():
    """获取有收藏的题库列表"""
    return favorite_service.get_banks_with_favorites()


@app.post("/api/favorites/{bank_id}/{question_id}")
def add_favorite(bank_id: str, question_id: str):
    """添加收藏"""
    # 如果 bank_id 是 unknown，尝试从所有题库中查找该题目
    if bank_id == "unknown":
        all_banks = bank_service.get_all_banks()
        for b in all_banks:
            q = b.get_question(question_id)
            if q:
                bank_id = b.id
                break
    
    bank = bank_service.get_bank(bank_id)
    if not bank:
        raise HTTPException(status_code=404, detail="题库不存在，请先将题目添加到题库中")
    
    question = bank.get_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    success, message = favorite_service.add_favorite(question, bank_id, bank.name)
    if success:
        return {"message": message}
    raise HTTPException(status_code=400, detail=message)


@app.delete("/api/favorites/{question_id}")
def remove_favorite(question_id: str):
    """移除收藏"""
    if favorite_service.remove_favorite(question_id):
        return {"message": "已取消收藏"}
    raise HTTPException(status_code=404, detail="收藏不存在")


@app.get("/api/favorites/check/{question_id}")
def check_favorite(question_id: str):
    """检查是否已收藏"""
    return {"favorited": favorite_service.is_favorited(question_id)}


@app.put("/api/favorites/{question_id}/note")
def update_favorite_note(question_id: str, note: str = ""):
    """更新收藏备注"""
    if favorite_service.update_note(question_id, note):
        return {"message": "备注已更新"}
    raise HTTPException(status_code=404, detail="收藏不存在")


@app.delete("/api/favorites")
def clear_all_favorites():
    """清空所有收藏"""
    if favorite_service.clear_all():
        return {"message": "已清空所有收藏"}
    raise HTTPException(status_code=500, detail="清空失败")


# ============ 配置 API ============

@app.get("/api/config/ai")
def get_ai_config():
    """获取AI配置（不返回完整密钥）"""
    ai_config = app_config.ai_config
    return {
        "api_base_url": ai_config.api_base_url,
        "api_key": ai_config.api_key[:8] + "..." if ai_config.api_key else "",  # 只返回部分密钥
        "api_key_set": bool(ai_config.api_key),
        "model": ai_config.model,
        "vision_model": ai_config.vision_model,
        "temperature": ai_config.temperature,
        "max_tokens": ai_config.max_tokens
    }


@app.put("/api/config/ai")
def update_ai_config(data: AIConfigUpdate):
    """更新AI配置"""
    if data.api_base_url is not None:
        app_config.ai_config.api_base_url = data.api_base_url
    if data.api_key is not None and data.api_key.strip():
        app_config.ai_config.api_key = data.api_key.strip()
    if data.model is not None:
        app_config.ai_config.model = data.model
    if data.vision_model is not None:
        app_config.ai_config.vision_model = data.vision_model
    if data.temperature is not None:
        app_config.ai_config.temperature = data.temperature
    if data.max_tokens is not None:
        app_config.ai_config.max_tokens = data.max_tokens
    
    # 保存配置
    app_config.save()
    
    # 重置AI客户端
    ai_service._reset_client()
    
    return {"message": "配置已更新"}


@app.get("/api/config/paths")
def get_path_config():
    """获取路径配置"""
    return {
        "banks_dir": app_config.path_config.banks_dir,
        "papers_dir": app_config.path_config.papers_dir,
        "results_dir": app_config.path_config.results_dir,
        "favorites_file": app_config.path_config.favorites_file
    }


@app.put("/api/config/paths")
def update_path_config(data: PathConfigUpdate):
    """更新路径配置"""
    if data.banks_dir is not None:
        app_config.path_config.banks_dir = data.banks_dir
    if data.papers_dir is not None:
        app_config.path_config.papers_dir = data.papers_dir
    if data.results_dir is not None:
        app_config.path_config.results_dir = data.results_dir
    if data.favorites_file is not None:
        app_config.path_config.favorites_file = data.favorites_file
    
    # 保存配置
    app_config.save()
    
    return {"message": "路径配置已更新"}


# ============ 数据导出导入 API ============

@app.post("/api/data/export")
def export_data(data: ExportRequest):
    """导出数据到指定文件夹"""
    export_path = Path(data.export_path)
    
    # 创建导出目录
    try:
        export_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"无法创建导出目录: {str(e)}")
    
    exported = []
    
    # 导出题库数据
    if data.include_banks:
        banks_dir = export_path / "banks"
        banks_dir.mkdir(exist_ok=True)
        banks = bank_service.get_all_banks()
        for bank in banks:
            bank_file = banks_dir / f"bank_{bank.id}.json"
            with open(bank_file, 'w', encoding='utf-8') as f:
                json.dump(bank.to_dict(), f, ensure_ascii=False, indent=2)
        exported.append(f"题库 ({len(banks)} 个)")
    
    # 导出试卷数据
    if data.include_papers:
        papers_dir = export_path / "papers"
        papers_dir.mkdir(exist_ok=True)
        papers = paper_service.get_all_papers()
        for paper in papers:
            paper_file = papers_dir / f"paper_{paper.id}.json"
            with open(paper_file, 'w', encoding='utf-8') as f:
                json.dump(paper.to_dict(), f, ensure_ascii=False, indent=2)
        exported.append(f"试卷 ({len(papers)} 份)")
    
    # 导出成绩数据
    if data.include_results:
        results_dir = export_path / "results"
        results_dir.mkdir(exist_ok=True)
        results = exam_service.get_all_results()
        for result in results:
            result_file = results_dir / f"result_{result.id}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        exported.append(f"成绩 ({len(results)} 条)")
    
    # 导出收藏数据
    if data.include_favorites:
        favorites = favorite_service.get_all_favorites()
        if favorites:
            fav_file = export_path / "favorites.json"
            with open(fav_file, 'w', encoding='utf-8') as f_out:
                json.dump([fav.to_dict() for fav in favorites], f_out, ensure_ascii=False, indent=2)
            exported.append(f"收藏 ({len(favorites)} 条)")

    # 导出AI配置
    if data.include_ai_config:
        ai_config_dir = export_path / "config"
        ai_config_dir.mkdir(exist_ok=True)
        ai_config_file = ai_config_dir / "ai_config.json"
        ai_config_data = {
            "api_base_url": app_config.ai_config.api_base_url,
            "api_key": app_config.ai_config.api_key,
            "model": app_config.ai_config.model,
            "vision_model": app_config.ai_config.vision_model,
            "temperature": app_config.ai_config.temperature,
            "max_tokens": app_config.ai_config.max_tokens
        }
        with open(ai_config_file, 'w', encoding='utf-8') as f:
            json.dump(ai_config_data, f, ensure_ascii=False, indent=2)
        exported.append("AI配置")
    
    # 写入导出信息文件
    info_file = export_path / "export_info.json"
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump({
            "export_time": datetime.now().isoformat(),
            "version": CURRENT_VERSION,
            "exported": exported
        }, f, ensure_ascii=False, indent=2)
    
    return {
        "message": "导出成功",
        "path": str(export_path),
        "exported": exported
    }


@app.get("/api/data/scan-import")
def scan_import_folder(path: str):
    """扫描导入文件夹，返回可导入的数据类型"""
    import_path = Path(path)
    
    if not import_path.exists():
        raise HTTPException(status_code=404, detail="文件夹不存在")
    
    available = {
        "banks": False,
        "papers": False,
        "results": False,
        "favorites": False,
        "ai_config": False,
        "banks_count": 0,
        "papers_count": 0,
        "results_count": 0,
        "favorites_count": 0
    }
    
    # 检查题库
    banks_dir = import_path / "banks"
    if banks_dir.exists():
        bank_files = list(banks_dir.glob("bank_*.json"))
        available["banks"] = len(bank_files) > 0
        available["banks_count"] = len(bank_files)
    
    # 检查试卷
    papers_dir = import_path / "papers"
    if papers_dir.exists():
        paper_files = list(papers_dir.glob("paper_*.json"))
        available["papers"] = len(paper_files) > 0
        available["papers_count"] = len(paper_files)
    
    # 检查成绩
    results_dir = import_path / "results"
    if results_dir.exists():
        result_files = list(results_dir.glob("result_*.json"))
        available["results"] = len(result_files) > 0
        available["results_count"] = len(result_files)
    
    # 检查收藏
    favorites_file = import_path / "favorites.json"
    if favorites_file.exists():
        try:
            with open(favorites_file, 'r', encoding='utf-8') as f:
                fav_data = json.load(f)
            available["favorites"] = len(fav_data) > 0
            available["favorites_count"] = len(fav_data)
        except:
            pass
    
    # 检查AI配置
    ai_config_file = import_path / "config" / "ai_config.json"
    available["ai_config"] = ai_config_file.exists()
    
    # 读取导出信息
    info_file = import_path / "export_info.json"
    if info_file.exists():
        with open(info_file, 'r', encoding='utf-8') as f:
            available["export_info"] = json.load(f)
    
    return available


@app.post("/api/data/import")
def import_data(data: ImportRequest):
    """从指定文件夹导入数据"""
    import_path = Path(data.import_path)
    
    if not import_path.exists():
        raise HTTPException(status_code=404, detail="文件夹不存在")
    
    imported = []
    errors = []
    
    # 导入题库
    if data.include_banks:
        banks_dir = import_path / "banks"
        if banks_dir.exists():
            count = 0
            for bank_file in banks_dir.glob("bank_*.json"):
                try:
                    with open(bank_file, 'r', encoding='utf-8') as f:
                        bank_data = json.load(f)
                    
                    # 尝试保留原始 ID 以维持试卷关联
                    bank = QuestionBank.from_dict(bank_data)
                    bank_service._save_bank(bank)
                    
                    # 更新元数据
                    meta = bank_service._load_meta()
                    meta[bank.id] = {
                        'name': bank.name,
                        'description': bank.description,
                        'subject': bank.subject,
                        'question_count': len(bank.questions),
                        'created_at': bank.created_at,
                        'updated_at': bank.updated_at
                    }
                    bank_service._save_meta(meta)
                    count += 1
                except Exception as e:
                    errors.append(f"导入题库失败 ({bank_file.name}): {str(e)}")
            if count > 0:
                imported.append(f"题库 ({count} 个)")
    
    # 导入试卷
    if data.include_papers:
        papers_dir = import_path / "papers"
        if papers_dir.exists():
            count = 0
            for paper_file in papers_dir.glob("paper_*.json"):
                try:
                    with open(paper_file, 'r', encoding='utf-8') as f:
                        paper_data = json.load(f)
                    # 直接复制到试卷目录
                    target_dir = Path(app_config.path_config.papers_dir)
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(paper_file, target_dir / paper_file.name)
                    count += 1
                except Exception as e:
                    errors.append(f"导入试卷失败 ({paper_file.name}): {str(e)}")
            if count > 0:
                imported.append(f"试卷 ({count} 份)")
    
    # 导入成绩
    if data.include_results:
        results_dir = import_path / "results"
        if results_dir.exists():
            count = 0
            for result_file in results_dir.glob("result_*.json"):
                try:
                    # 直接复制到成绩目录
                    target_dir = Path(app_config.path_config.results_dir)
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(result_file, target_dir / result_file.name)
                    count += 1
                except Exception as e:
                    errors.append(f"导入成绩失败 ({result_file.name}): {str(e)}")
            if count > 0:
                imported.append(f"成绩 ({count} 条)")
    
    # 导入收藏
    if data.include_favorites:
        fav_file = import_path / "favorites.json"
        if fav_file.exists():
            try:
                with open(fav_file, 'r', encoding='utf-8') as f:
                    fav_data = json.load(f)
                
                # 获取当前收藏列表
                current_favs = favorite_service.get_all_favorites()
                current_ids = {f.question_id for f in current_favs}
                
                count = 0
                for fav_dict in fav_data:
                    q_id = fav_dict.get('question_id')
                    if q_id and q_id not in current_ids:
                        # 构造 Question 对象
                        q = Question(
                            id=q_id,
                            type=fav_dict.get('question_type', 'single'),
                            question=fav_dict.get('question_content', ''),
                            options=fav_dict.get('options', []),
                            answer=fav_dict.get('answer', ''),
                            explanation=fav_dict.get('explanation', ''),
                            difficulty=fav_dict.get('difficulty', 3),
                            tags=fav_dict.get('tags', [])
                        )
                        favorite_service.add_favorite(
                            question=q,
                            bank_id=fav_dict.get('bank_id', 'unknown'),
                            bank_name=fav_dict.get('bank_name', '未知题库'),
                            note=fav_dict.get('note', '')
                        )
                        count += 1
                
                if count > 0:
                    imported.append(f"收藏 ({count} 条)")
            except Exception as e:
                errors.append(f"导入收藏失败: {str(e)}")

    # 导入AI配置
    if data.include_ai_config:
        ai_config_file = import_path / "config" / "ai_config.json"
        if ai_config_file.exists():
            try:
                with open(ai_config_file, 'r', encoding='utf-8') as f:
                    ai_config_data = json.load(f)
                app_config.ai_config.api_base_url = ai_config_data.get("api_base_url", "")
                app_config.ai_config.api_key = ai_config_data.get("api_key", "")
                app_config.ai_config.model = ai_config_data.get("model", "")
                app_config.ai_config.vision_model = ai_config_data.get("vision_model", "")
                app_config.ai_config.temperature = ai_config_data.get("temperature", 0.3)
                app_config.ai_config.max_tokens = ai_config_data.get("max_tokens", 4096)
                app_config.save()
                ai_service._reset_client()
                imported.append("AI配置")
            except Exception as e:
                errors.append(f"导入AI配置失败: {str(e)}")
    
    return {
        "message": "导入完成",
        "imported": imported,
        "errors": errors
    }


# ============ 更新检测 API ============

def parse_version(version_str: str) -> tuple:
    """解析版本号为元组，用于比较"""
    # 移除 'v' 前缀（如 v1.0.0 -> 1.0.0）
    if version_str.startswith('v'):
        version_str = version_str[1:]
    
    # 处理预发布版本（如 1.0.0-beta.1）
    version_str = version_str.split('-')[0]
    
    parts = version_str.split('.')
    result = []
    for part in parts:
        try:
            result.append(int(part))
        except ValueError:
            result.append(0)
    return tuple(result)


@app.get("/api/system/version")
def get_current_version():
    """获取当前系统版本"""
    return {
        "version": CURRENT_VERSION,
        "name": "智题坊"
    }


@app.get("/api/system/check-update")
async def check_update():
    """检测是否有新版本更新"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                GITHUB_RELEASES_API,
                headers={"Accept": "application/vnd.github.v3+json"}
            )
            
            if response.status_code == 404:
                return {
                    "has_update": False,
                    "current_version": CURRENT_VERSION,
                    "message": "暂无发布版本"
                }
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"GitHub API 请求失败: {response.status_code}")
            
            release_data = response.json()
            latest_version = release_data.get("tag_name", "")
            
            # 比较版本号
            current_parts = parse_version(CURRENT_VERSION)
            latest_parts = parse_version(latest_version)
            
            has_update = latest_parts > current_parts
            
            # 获取下载资源
            assets = release_data.get("assets", [])
            download_url = None
            download_size = 0
            
            for asset in assets:
                name = asset.get("name", "").lower()
                if name.endswith('.exe') or name.endswith('.zip'):
                    download_url = asset.get("browser_download_url")
                    download_size = asset.get("size", 0)
                    break
            
            return {
                "has_update": has_update,
                "current_version": CURRENT_VERSION,
                "latest_version": latest_version,
                "release_name": release_data.get("name", ""),
                "release_notes": release_data.get("body", ""),
                "release_date": release_data.get("published_at", ""),
                "download_url": download_url or release_data.get("html_url"),
                "download_size": download_size,
                "html_url": release_data.get("html_url")
            }
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="检测更新超时，请稍后再试")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"网络请求失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测更新失败: {str(e)}")


# ============ 启动服务器 ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
