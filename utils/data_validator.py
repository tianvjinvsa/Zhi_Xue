def validate_question_format(questions):
    """
    验证题目列表的格式是否合法
    要求：
    1. 题型只能是「单选题」「多选题」「判断题」
    2. 分值必须是正整数
    3. 正确答案格式合法（单选/判断为单个字母，多选为多个字母拼接，如AB）
    """
    valid_types = ["单选题", "多选题", "判断题"]
    errors = []

    for idx, q in enumerate(questions, 1):
        # 检查题型
        if q["题型"] not in valid_types:
            errors.append(f"第{idx}题：题型必须是{valid_types}，当前为{q['题型']}")
        
        # 检查分值
        if not isinstance(q["分值"], int) or q["分值"] <= 0:
            errors.append(f"第{idx}题：分值必须是正整数，当前为{q['分值']}")
        
        # 检查正确答案格式
        if q["题型"] == "单选题":
            if len(q["正确答案"]) != 1 or not q["正确答案"].isalpha():
                errors.append(f"第{idx}题：单选题正确答案必须是单个字母（如A），当前为{q['正确答案']}")
        elif q["题型"] == "判断题":
            if q["正确答案"] not in ["对", "错"]:
                errors.append(f"第{idx}题：判断题正确答案必须是「对」或「错」，当前为{q['正确答案']}")
        elif q["题型"] == "多选题":
            if not all(c.isalpha() for c in q["正确答案"]):
                errors.append(f"第{idx}题：多选题正确答案必须是字母拼接（如AB），当前为{q['正确答案']}")
    
    if errors:
        raise ValueError("题目格式验证失败：\n" + "\n".join(errors))
    return True

def validate_question_count(question_bank, single_num, multi_num, judge_num):
    """
    验证用户指定的抽题数量是否合法（不超过题库存量）
    参数：
    - question_bank: 分类后的题库字典（如{"单选题":[...], "多选题":[...], "判断题":[...]}）
    - single_num: 要抽取的单选题数量
    - multi_num: 多选题数量
    - judge_num: 判断题数量
    """
    errors = []
    # 检查数量是否为非负整数
    if not isinstance(single_num, int) or single_num < 0:
        errors.append("单选题数量必须是非负整数！")
    if not isinstance(multi_num, int) or multi_num < 0:
        errors.append("多选题数量必须是非负整数！")
    if not isinstance(judge_num, int) or judge_num < 0:
        errors.append("判断题数量必须是非负整数！")
    
    # 检查数量是否超过库存
    single_count = len(question_bank.get("单选题", []))
    multi_count = len(question_bank.get("多选题", []))
    judge_count = len(question_bank.get("判断题", []))

    if single_num > single_count:
        errors.append(f"单选题库存仅{single_count}道，无法抽取{single_num}道！")
    if multi_num > multi_count:
        errors.append(f"多选题库存仅{multi_count}道，无法抽取{multi_num}道！")
    if judge_num > judge_count:
        errors.append(f"判断题库存仅{judge_count}道，无法抽取{judge_num}道！")
    
    # 检查是否至少抽1道题
    if single_num + multi_num + judge_num == 0:
        errors.append("至少要抽取1道题！")
    
    if errors:
        raise ValueError("抽题数量验证失败：\n" + "\n".join(errors))
    return True

# 测试用例（新手可取消注释运行）
# if __name__ == "__main__":
#     # 测试题目格式验证
#     test_questions = [
#         {"题型":"单选题","题干":"测试","选项":["A.1"],"正确答案":"A","分值":1},
#         {"题型":"判断题","题干":"测试","选项":["A.对|B.错"],"正确答案":"对","分值":2}
#     ]
#     print(validate_question_format(test_questions))

#     # 测试抽题数量验证
#     test_bank = {"单选题":[1,2], "多选题":[1], "判断题":[1]}
#     print(validate_question_count(test_bank, 2, 1, 1))  # 合法
#     # print(validate_question_count(test_bank, 3, 1, 1))  # 非法（单选超量）