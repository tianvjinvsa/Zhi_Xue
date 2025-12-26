import os
import json
import pandas as pd
from datetime import datetime

# 定义项目根目录（自动获取，无需手动修改）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 定义各数据目录路径
QUESTION_BANK_DIR = os.path.join(BASE_DIR, "data", "question_bank")
PAPERS_DIR = os.path.join(BASE_DIR, "data", "papers")
RECORDS_DIR = os.path.join(BASE_DIR, "data", "records")

# 确保目录存在（防止手动创建遗漏）
for dir_path in [QUESTION_BANK_DIR, PAPERS_DIR, RECORDS_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def read_excel_csv(file_path):
    """
    读取Excel(.xlsx)或CSV文件，返回标准化的题目列表
    要求文件列名必须包含：题型、题干、选项、正确答案、分值
    选项格式示例：A.选项1|B.选项2|C.选项3（用|分隔）
    """
    try:
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        elif file_path.endswith(".csv"):
            df = pd.read_csv(file_path, encoding="utf-8")
        else:
            raise ValueError("文件格式不是Excel或CSV！")
        
        # 检查必要列是否存在
        required_cols = ["题型", "题干", "选项", "正确答案", "分值"]
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"文件缺少必要列！必须包含：{required_cols}")
        
        # 转换为标准化题目列表（字典格式）
        questions = []
        for _, row in df.iterrows():
            question = {
                "题型": row["题型"].strip(),
                "题干": row["题干"].strip(),
                "选项": row["选项"].strip().split("|"),  # 拆分选项为列表
                "正确答案": row["正确答案"].strip(),
                "分值": int(row["分值"])
            }
            questions.append(question)
        return questions
    except Exception as e:
        raise Exception(f"读取Excel/CSV失败：{str(e)}")

def read_txt(file_path, to_json=False, json_save_path=None):
    """
    读取TXT格式题库，返回标准化题目列表
    TXT文件格式要求（每行对应一个字段，空行分隔题目）：
    题型：单选题
    题干：Python的创始人是？
    选项：A.吉多·范罗苏姆|B.扎克伯格|C.乔布斯
    正确答案：A
    分值：1
    
    参数：
    - to_json: 是否转换为JSON格式保存
    - json_save_path: JSON保存路径（不传则默认保存到题库目录）
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip().split("\n\n")  # 空行分隔题目
        
        questions = []
        for q_content in content:
            if not q_content:
                continue
            # 按行解析单个题目
            q_lines = [line.strip() for line in q_content.split("\n") if line.strip()]
            q_dict = {}
            for line in q_lines:
                key, value = line.split("：", 1)  # 中文冒号分隔键值
                q_dict[key] = value.strip()
            
            # 标准化处理
            question = {
                "题型": q_dict["题型"],
                "题干": q_dict["题干"],
                "选项": q_dict["选项"].split("|"),
                "正确答案": q_dict["正确答案"],
                "分值": int(q_dict["分值"])
            }
            questions.append(question)
        
        # 转换为JSON并保存（如果需要）
        if to_json:
            if not json_save_path:
                # 默认保存到题库目录，文件名与TXT一致
                txt_name = os.path.basename(file_path).replace(".txt", ".json")
                json_save_path = os.path.join(QUESTION_BANK_DIR, txt_name)
            with open(json_save_path, "w", encoding="utf-8") as f:
                json.dump(questions, f, ensure_ascii=False, indent=4)
        
        return questions
    except Exception as e:
        raise Exception(f"读取TXT失败：{str(e)}")

def read_json(file_path):
    """读取JSON格式题库，返回标准化题目列表"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            questions = json.load(f)
        # 简单验证格式（确保是列表且包含必要字段）
        if not isinstance(questions, list):
            raise ValueError("JSON文件内容不是列表格式！")
        required_keys = ["题型", "题干", "选项", "正确答案", "分值"]
        for q in questions:
            if not all(key in q for key in required_keys):
                raise ValueError("JSON中题目缺少必要字段！")
        return questions
    except Exception as e:
        raise Exception(f"读取JSON失败：{str(e)}")

def save_data(data, save_type, file_name=None):
    """
    通用保存函数：保存题库/试卷/记录到对应目录
    参数：
    - data: 要保存的数据（列表/字典）
    - save_type: 保存类型（"bank"=题库, "paper"=试卷, "record"=记录）
    - file_name: 自定义文件名（不传则按时间生成）
    返回：保存的文件路径
    """
    try:
        # 确定保存目录
        if save_type == "bank":
            save_dir = QUESTION_BANK_DIR
            suffix = ".json"  # 题库统一保存为JSON
        elif save_type == "paper":
            save_dir = PAPERS_DIR
            suffix = ".txt"  # 试卷保存为TXT（易查看）
        elif save_type == "record":
            save_dir = RECORDS_DIR
            suffix = ".json"  # 记录保存为JSON
        else:
            raise ValueError("save_type只能是bank/paper/record！")
        
        # 生成文件名（按时间戳，避免重复）
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{save_type}_{timestamp}{suffix}"
        else:
            file_name = file_name if file_name.endswith(suffix) else f"{file_name}{suffix}"
        
        save_path = os.path.join(save_dir, file_name)
        # 保存数据
        with open(save_path, "w", encoding="utf-8") as f:
            if suffix == ".json":
                json.dump(data, f, ensure_ascii=False, indent=4)
            elif suffix == ".txt":
                # 试卷TXT格式化（按题目逐条写入）
                txt_content = ""
                for idx, q in enumerate(data, 1):
                    txt_content += f"第{idx}题（{q['题型']}，{q['分值']}分）\n"
                    txt_content += f"题干：{q['题干']}\n"
                    txt_content += f"选项：{'|'.join(q['选项'])}\n"
                    txt_content += f"正确答案：{q['正确答案']}\n\n"
                f.write(txt_content)
        
        return save_path
    except Exception as e:
        raise Exception(f"保存数据失败：{str(e)}")

# 测试用例（修正路径问题，可直接运行）
if __name__ == "__main__":
    # 1. 构建测试TXT文件的绝对路径（自动定位到data/question_bank/）
    test_txt_path = os.path.join(QUESTION_BANK_DIR, "test_questions.txt")
    
    # 2. 测试读取TXT并转JSON（会自动保存到data/question_bank/）
    try:
        test_txt = read_txt(test_txt_path, to_json=True)
        print("✅ TXT读取成功！示例题目：")
        print(test_txt[0])  # 打印第一道题
    except Exception as e:
        print(f"❌ TXT读取失败：{e}")

    # 3. 测试读取转换后的JSON文件
    test_json_path = os.path.join(QUESTION_BANK_DIR, "test_questions.json")
    try:
        test_json = read_json(test_json_path)
        print("\n✅ JSON读取成功！示例题目：")
        print(test_json[0])
    except Exception as e:
        print(f"❌ JSON读取失败：{e}")

    # 4. 测试保存试卷数据
    test_data = [{"题型":"单选题","题干":"测试题","选项":["A.1","B.2"],"正确答案":"A","分值":1}]
    try:
        save_path = save_data(test_data, "paper")
        print(f"\n✅ 数据保存成功！路径：{save_path}")
    except Exception as e:
        print(f"❌ 数据保存失败：{e}")