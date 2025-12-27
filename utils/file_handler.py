"""
文件处理工具
"""
import json
import shutil
from pathlib import Path
from typing import Any, Optional
from datetime import datetime


class FileHandler:
    """文件处理工具类"""
    
    @staticmethod
    def read_json(file_path: str | Path) -> Optional[dict]:
        """读取JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取JSON文件失败: {e}")
            return None
    
    @staticmethod
    def write_json(file_path: str | Path, data: Any, indent: int = 2) -> bool:
        """写入JSON文件"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            return True
        except Exception as e:
            print(f"写入JSON文件失败: {e}")
            return False
    
    @staticmethod
    def read_text(file_path: str | Path, encoding: str = 'utf-8') -> Optional[str]:
        """读取文本文件"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            for enc in ['gbk', 'gb2312', 'latin1']:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        return f.read()
                except:
                    continue
        except Exception as e:
            print(f"读取文本文件失败: {e}")
        return None
    
    @staticmethod
    def write_text(file_path: str | Path, content: str, encoding: str = 'utf-8') -> bool:
        """写入文本文件"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入文本文件失败: {e}")
            return False
    
    @staticmethod
    def copy_file(src: str | Path, dst: str | Path) -> bool:
        """复制文件"""
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            print(f"复制文件失败: {e}")
            return False
    
    @staticmethod
    def move_file(src: str | Path, dst: str | Path) -> bool:
        """移动文件"""
        try:
            shutil.move(src, dst)
            return True
        except Exception as e:
            print(f"移动文件失败: {e}")
            return False
    
    @staticmethod
    def delete_file(file_path: str | Path) -> bool:
        """删除文件"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
            return True
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False
    
    @staticmethod
    def ensure_dir(dir_path: str | Path) -> bool:
        """确保目录存在"""
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建目录失败: {e}")
            return False
    
    @staticmethod
    def list_files(dir_path: str | Path, pattern: str = "*") -> list[Path]:
        """列出目录下的文件"""
        try:
            return list(Path(dir_path).glob(pattern))
        except Exception as e:
            print(f"列出文件失败: {e}")
            return []
    
    @staticmethod
    def get_file_info(file_path: str | Path) -> Optional[dict]:
        """获取文件信息"""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                'name': path.name,
                'path': str(path.absolute()),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
                'extension': path.suffix
            }
        except Exception as e:
            print(f"获取文件信息失败: {e}")
            return None
    
    @staticmethod
    def backup_file(file_path: str | Path, backup_suffix: str = ".bak") -> Optional[Path]:
        """备份文件"""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = path.with_suffix(f"{path.suffix}.{timestamp}{backup_suffix}")
            shutil.copy2(path, backup_path)
            return backup_path
        except Exception as e:
            print(f"备份文件失败: {e}")
            return None
