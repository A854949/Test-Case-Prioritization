import pandas as pd
import re


def transfer_min_to_hours(min_str):
    """將包含分鐘數的字串轉換成小時數。支持處理像 '600/10728' 這樣的字串，將其拆分並分別轉換。"""
    # 首先去除特殊字符 _x000D_
    cleaned_str = min_str.replace('_x000D_', '')
    parts = cleaned_str.split('/')
    hours_list = []

    for part in parts:
        clean_min_str = re.sub(r'\D', '', part)  # 移除非數字字符
        if clean_min_str:
            hours = int(clean_min_str) / 60
            hours_list.append(f"{hours:.2f}")
        else:
            hours_list.append("0.00")  # 如果部分沒有數字，則返回默認值 "0.00"

    return '/'.join(hours_list)




def parser2_process(input_file_path, output_file_path):
    """將Excel檔案中的'C'欄位內容轉換成DataFrame的欄位"""
    # 欄位名稱
    headers = [
        "Pass/Fail",
        "Tester",
        "Platform Name",
        "SKU",
        "Hw Phase",
        "OBS",
        "Block Type",
        "File",
        "KAT/KUT",
        "RTA",
        "ATT/UAT",
        "Run Cycle",
        "Fail Cycle/Total Cycle",
        "Case Note",
        "Comments",
        "Component List",
        "Comment",
    ]
    # 特殊處理的欄位名稱
    special_headers = ["KAT/KUT", "ATT/UAT", "Pass/Fail", "OBS"]
    # 將秒數轉換成時數的欄位名稱
    min_to_hours_headers = ["KAT/KUT", "ATT/UAT"]
    # 需要替換字串的欄位名稱
    replace_str_headers = ["OBS"]
    # 測試類別對照表
    category_mapping = {
        "1": "Inspection",
        "2": "Memory",
        "3": "Storage",
        "5": "Graphics",
        "6": "Power Cycle",
        "7": "Stress",
        "8": "USB",
        "9": "Connectivity",
        "10": "Expansion",
        "11": "Super I/O_EC",
        "12": "Audio",
        "13": "OS and Security",
        "14": "ACPI",
        "15": "Manageability",
        "16.1": "Fingerprint",
        "16.2": "Fingerprint",
        "16.3": "Fingerprint",
        "16.4": "SureView",
    }

    # 讀取Excel檔案
    df = pd.read_excel(input_file_path)

    # 新建一個DataFrame，用於存放處理後的數據
    new_df = pd.DataFrame()
    # 用于记录被设置为 "" 的行的索引
    indexes_to_drop = []

    # 迴圈處理每個值
    for index, cell_value in df["Unnamed: 3"].items():
        # 先处理 "Pass/Fail" 字段
        cell_value = cell_value.replace('_x000D_', '')

        pass_fail_match = re.search(r'^(pass|fail|Fail)', cell_value, re.IGNORECASE)
        if pass_fail_match:
            new_df.at[index, "Pass/Fail"] = pass_fail_match.group(1).lower()
        else:
            new_df.at[index, "Pass/Fail"] = ""  # 如果沒有匹配到 "pass" 或 "fail"
            indexes_to_drop.append(index)

        # 然後處理其他的欄位...
        for header in headers:
            if header == "Pass/Fail":
                continue  # 已经处理过了，所以跳过

            # 根据字段特性选择匹配逻辑
            if header != "Component List":
                # 如果字段以 '_x000D_' 结尾，则使用第一段代码的逻辑
                if "_x000D_" in cell_value:
                    pattern = re.escape(header) + r":(.*?)_x000D_"
                else:
                    # 否则使用第二段代码的复杂逻辑
                    pattern = re.escape(header) + r":(.*?)(?=" + '|'.join([re.escape(next_header) for next_header in headers if next_header != header]) + "|$)"
            else:
                # 专门处理 "Component List" 字段
                pattern = re.escape(header) + r":(.*?)Comment:"

                parts = re.search(pattern, cell_value, re.DOTALL)
                if parts:
                    clean_value = parts[1].strip().replace('_x000D_', '')  # 清除特殊字符
                    # 在這裡添加替換換行符的代碼
                    clean_value = clean_value.replace('\n', ' ').replace('\r', ' ')
                    new_df.at[index, header] = clean_value


            # 搜索并清除特殊字符
            parts = re.search(pattern, cell_value, re.DOTALL)
            if parts:
                clean_value = parts[1].strip().replace('_x000D_', '')  # 清除特殊字符
                new_df.at[index, header] = clean_value
            # # 尋找指定字串
            # parts = re.search(pattern, cell_value)

            # 將處理後的數據存入新的DataFrame
            if parts and header not in special_headers:
                new_df.at[index, header] = parts[1].strip()
            
            elif parts and header in min_to_hours_headers:
                minutes = parts[1].strip().split("/")
                if len(minutes) == 2:
                    new_df.at[
                        index, header
                    ] = f"{transfer_min_to_hours(minutes[0])}/{transfer_min_to_hours(minutes[1])}"
                else:
                    new_df.at[index, header] = parts[1].strip()
            elif parts and header in replace_str_headers:
                replaced_str = re.sub(r'Sudden Impact-|Other-|-', 'SIO', parts[1].strip())
                new_df.at[index, header] = replaced_str

    # # 將第一欄的欄位名稱改為'Task ID'
    # df.rename(columns={df.columns[0]: "Task ID"}, inplace=True)

    # 將第二欄的欄位名稱改為'Case Title'
    df.rename(columns={df.columns[1]: "Case Title"}, inplace=True)

    # # 將第一欄的'Task ID'欄位值都改為'ICQ-TASK0000012155'
    # df["Task ID"] = "ICQ-TASK0000012155"


    # 新增一個欄位'Category'，用於存放測試類別
    for index, cell_value in df["Case Title"].items():
        category_key_parts = cell_value.split(".")
        if len(category_key_parts) >= 2:
            category_key = category_key_parts[0]  # 取第一部分，即編號的部分
            if category_key == "16":
                category_key += "." + category_key_parts[1]  # 如果是以 "16" 開頭，則加上小數部分
            category = category_mapping.get(category_key, "Other")  # 如果找不到映射，設為 "Other"
            header = "Category"
            new_df.at[index, header] = category

 

    # 使用记录的索引删除 df 中相应的行
    df.drop(indexes_to_drop, inplace=True)

    # 刪除在 "Pass/Fail" 欄位為空的行
    # 使用布尔索引来筛选出 new_df 中 "Pass/Fail" 不为空的行
    new_df = new_df[new_df["Pass/Fail"] != ""]

    # 将处理后的 DataFrame 与原始 DataFrame 合并
    df = pd.concat([df, new_df], axis=1)

    # 删除原始 'C' 列
    df = df.drop(columns=["Unnamed: 3"])


    # 保存处理后的 DataFrame 到新的 Excel 文件
    df.to_csv(output_file_path, index=False, encoding='utf-8-sig')

