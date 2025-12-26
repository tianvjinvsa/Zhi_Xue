# 新增：将项目根目录加入模块搜索路径（解决utils导入失败）
import sys
import os
# 获取当前文件（bank_manager.py）的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（AnswerSystem/，即current_dir的上层目录）
root_dir = os.path.dirname(current_dir)
# 将根目录加入sys.path
sys.path.append(root_dir)

# 原有import代码（现在能正常导入了）
from utils.file_handler import (
    read_excel_csv, read_txt, read_json, save_data,
    QUESTION_BANK_DIR
)
from utils.data_validator import validate_question_format

# 后续原有代码不变...

import os
from utils.file_handler import (
    read_excel_csv, read_txt, read_json, save_data,
    QUESTION_BANK_DIR
)
from utils.data_validator import validate_question_format

# 全局变量：存储当前加载的题库（分类后）
current_bank = {
    "单选题": [],
    "多选题": [],
    "判断题": []
}

def upload_question_bank(file_path, save_name=None):
    """
    上传题库文件，自动识别格式并处理
    参数：
    - file_path: 上传文件的绝对路径
    - save_name: 保存到题库目录的文件名（不传则用原文件名）
    返回：
    - 分类后的题库字典 + 保存路径
    """
    global current_bank
    try:
        # 1. 识别文件格式，调用对应解析函数
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in [".xlsx", ".csv"]:
            questions = read_excel_csv(file_path)
        elif file_ext == ".txt":
            # TXT文件先解析，再统一保存为JSON（不额外转JSON，仅解析）
            questions = read_txt(file_path, to_json=False)
        elif file_ext == ".json":
            questions = read_json(file_path)
        else:
            raise ValueError(f"不支持的文件格式：{file_ext}！仅支持xlsx/csv/txt/json")
        
        # 2. 验证题目格式合法性
        validate_question_format(questions)
        
        # 3. 按题型分类
        classified_bank = {
            "单选题": [],
            "多选题": [],
            "判断题": []
        }
        for q in questions:
            q_type = q["题型"]
            if q_type in classified_bank:
                classified_bank[q_type].append(q)
        
        # 4. 持久化保存（统一为JSON格式）
        if not save_name:
            save_name = os.path.basename(file_path).replace(file_ext, ".json")
        save_path = save_data(questions, "bank", save_name)
        
        # 5. 更新全局当前题库
        current_bank = classified_bank
        
        print(f"✅ 题库上传成功！共{len(questions)}道题，保存路径：{save_path}")
        return classified_bank, save_path
    except Exception as e:
        raise Exception(f"题库上传失败：{str(e)}")

def get_question_bank():
    """获取当前加载的分类题库（全局变量）"""
    return current_bank.copy()  # 返回副本，避免外部修改全局变量

def get_bank_info():
    """获取题库统计信息（各题型数量）"""
    bank = get_question_bank()
    info = {
        "单选题数量": len(bank["单选题"]),
        "多选题数量": len(bank["多选题"]),
        "判断题数量": len(bank["判断题"]),
        "总题数": len(bank["单选题"]) + len(bank["多选题"]) + len(bank["判断题"])
    }
    return info

def load_saved_bank(json_file_name):
    """
    加载已保存的JSON格式题库（从data/question_bank/目录）
    参数：
    - json_file_name: 题库JSON文件名（如test_questions.json）
    """
    global current_bank
    try:
        file_path = os.path.join(QUESTION_BANK_DIR, json_file_name)
        if not os.path.exists(file_path):
            raise ValueError(f"题库文件不存在：{file_path}")
        
        # 读取JSON并分类
        questions = read_json(file_path)
        validate_question_format(questions)
        
        classified_bank = {
            "单选题": [],
            "多选题": [],
            "判断题": []
        }
        for q in questions:
            q_type = q["题型"]
            if q_type in classified_bank:
                classified_bank[q_type].append(q)
        
        current_bank = classified_bank
        print(f"✅ 加载已保存题库成功！{get_bank_info()}")
        return classified_bank
    except Exception as e:
        raise Exception(f"加载已保存题库失败：{str(e)}")

# 测试用例（基于第二步的test_questions.txt）
if __name__ == "__main__":
    # 1. 测试上传TXT题库（替换为你的test_questions.txt绝对路径）
    test_txt_path = os.path.join(QUESTION_BANK_DIR, "test_questions.txt")
    try:
        bank, save_path = upload_question_bank(test_txt_path)
        print("📊 分类后的题库：")
        print(f"单选题：{len(bank['单选题'])}道")
        print(f"多选题：{len(bank['多选题'])}道")
        print(f"判断题：{len(bank['判断题'])}道")
        
        # 2. 测试获取题库信息
        info = get_bank_info()
        print("\n📈 题库统计信息：", info)
        
        # 3. 测试加载已保存的JSON题库
        saved_json_name = "test_questions.json"
        load_saved_bank(saved_json_name)
        print("\n🔄 加载后题库信息：", get_bank_info())
    except Exception as e:
        print(f"❌ 测试失败：{e}")