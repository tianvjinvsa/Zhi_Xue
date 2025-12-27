"""
智题坊 - 配置管理模块
"""
import os
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import base64
import hashlib


import sys

# 应用根目录
if getattr(sys, 'frozen', False):
    # 打包后运行，使用可执行文件所在目录作为根目录
    APP_ROOT = Path(sys.executable).parent.absolute()
else:
    # 开发模式，使用当前文件所在目录
    APP_ROOT = Path(__file__).parent.absolute()

# 数据目录
DATA_DIR = APP_ROOT / "data"
BANKS_DIR = DATA_DIR / "banks"
PAPERS_DIR = DATA_DIR / "papers"
RESULTS_DIR = DATA_DIR / "results"
CONFIG_FILE = DATA_DIR / "config.json"

# 资源目录
RESOURCES_DIR = APP_ROOT / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"
STYLES_DIR = RESOURCES_DIR / "styles"


@dataclass
class AIConfig:
    """AI服务配置"""
    api_provider: str = "openai"  # openai, azure, zhipu, qwen
    api_key: str = ""
    api_base_url: str = ""
    model: str = "gpt-4o-mini"
    vision_model: str = "gpt-4o"
    max_tokens: int = 4096
    temperature: float = 0.3


@dataclass
class PathConfig:
    """数据路径配置"""
    banks_dir: str = ""      # 题库数据目录
    papers_dir: str = ""     # 试卷数据目录
    results_dir: str = ""    # 成绩数据目录
    favorites_file: str = "" # 收藏数据文件
    
    def __post_init__(self):
        """初始化默认路径"""
        if not self.banks_dir:
            self.banks_dir = str(BANKS_DIR)
        if not self.papers_dir:
            self.papers_dir = str(PAPERS_DIR)
        if not self.results_dir:
            self.results_dir = str(RESULTS_DIR)
        if not self.favorites_file:
            self.favorites_file = str(DATA_DIR / "favorites.json")


@dataclass
class AppConfig:
    """应用配置"""
    theme: str = "light"  # light, dark
    language: str = "zh_CN"
    auto_save: bool = True
    show_answer_immediately: bool = False
    default_time_limit: int = 60  # 默认答题时间（分钟）
    multiple_partial_score: bool = True  # 多选题部分得分


class ConfigManager:
    """配置管理器"""
    
    _instance: Optional['ConfigManager'] = None
    _encryption_key: Optional[bytes] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.ai_config = AIConfig()
        self.app_config = AppConfig()
        self.path_config = PathConfig()
        self._ensure_directories()
        self._load_config()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        for dir_path in [DATA_DIR, BANKS_DIR, PAPERS_DIR, RESULTS_DIR, 
                         RESOURCES_DIR, ICONS_DIR, STYLES_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _get_encryption_key(self) -> bytes:
        """获取加密密钥"""
        if self._encryption_key is None:
            # 使用机器特征生成密钥
            # 移除 APP_ROOT 以避免路径变化导致解密失败
            machine_id = f"{os.getlogin()}_{os.name}"
            key_hash = hashlib.sha256(machine_id.encode()).digest()
            self._encryption_key = base64.urlsafe_b64encode(key_hash)
        return self._encryption_key
    
    def _encrypt(self, data: str) -> str:
        """加密数据"""
        if not data:
            return ""
        fernet = Fernet(self._get_encryption_key())
        return fernet.encrypt(data.encode()).decode()
    
    def _decrypt(self, data: str) -> str:
        """解密数据"""
        if not data:
            return ""
        try:
            fernet = Fernet(self._get_encryption_key())
            return fernet.decrypt(data.encode()).decode()
        except Exception:
            return ""
    
    def _load_config(self):
        """加载配置"""
        if not CONFIG_FILE.exists():
            self._save_config()
            return
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载AI配置
            ai_data = data.get('ai', {})
            if 'api_key' in ai_data and ai_data['api_key']:
                ai_data['api_key'] = self._decrypt(ai_data['api_key'])
            self.ai_config = AIConfig(**ai_data)
            
            # 加载应用配置
            app_data = data.get('app', {})
            self.app_config = AppConfig(**app_data)
            
            # 加载路径配置
            path_data = data.get('paths', {})
            self.path_config = PathConfig(**path_data)
            
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def _save_config(self):
        """保存配置"""
        try:
            ai_data = asdict(self.ai_config)
            if ai_data['api_key']:
                ai_data['api_key'] = self._encrypt(ai_data['api_key'])
            
            data = {
                'ai': ai_data,
                'app': asdict(self.app_config),
                'paths': asdict(self.path_config)
            }
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def save(self):
        """保存配置"""
        self._save_config()
    
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.ai_config.api_key = api_key
        self._save_config()
    
    def get_api_key(self) -> str:
        """获取API密钥"""
        return self.ai_config.api_key


# 全局配置实例
config = ConfigManager()
