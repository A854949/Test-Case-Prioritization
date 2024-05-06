import pandas as pd
import os
import re  # 引入正则表达式模块
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def read_excel_sheets(file_path, sheets):
    all_data = pd.DataFrame()
    bios_version = os.path.splitext(os.path.basename(file_path))[0]
    bios_version = bios_version.replace('_', ' ')
    
    with pd.ExcelFile(file_path, engine='openpyxl') as xls:
        for sheet_name in sheets:
            if sheet_name in xls.sheet_names:
                # 使用 na_filter=False 避免将 'NA' 自动转换为 NaN
                data = pd.read_excel(xls, sheet_name=sheet_name, header=None, na_filter=False)
                test_cases = data.iloc[34:, [4, 4, 6]]
                test_cases.columns = ['Test Case Number', 'Test Case Name', 'Result']
                test_cases['BIOS Version'] = bios_version
                test_cases['Comment'] = pd.NA
                test_cases = test_cases[['BIOS Version', 'Test Case Number', 'Test Case Name', 'Result', 'Comment']]
                all_data = pd.concat([all_data, test_cases], ignore_index=True)
    return all_data


def extract_test_case_number(test_case_name):
    # 确保输入是字符串
    if pd.isna(test_case_name):
        return None
    test_case_name = str(test_case_name).strip()
    # 移除前导空格
    test_case_name = test_case_name.strip()
    
    # 为每种格式定义一个正则表达式
    patterns = [
        r"([A-Za-z]+(?:\.\w+)+)",  # 带点的数字和字母序列
        r"(\d+-\d+)"               # 带短划线的数字序列
    ]
    
    # 遍历每个模式，尝试找到匹配项
    for pattern in patterns:
        match = re.search(pattern, test_case_name)
        if match:
            return match.group(1)
    
    return None

def clean_test_case_name(test_case_name):
    # 确保输入是字符串
    if pd.isna(test_case_name):
        return None
    test_case_name = str(test_case_name).strip()
    
    # 为每种格式定义一个正则表达式
    patterns = [
        r"[A-Za-z]+(?:\.\w+)+",  # 带点的数字和字母序列
        r"\d+-\d+"               # 带短划线的数字序列
    ]
    
    # 遍历每个模式，尝试找到匹配项并删除
    for pattern in patterns:
        test_case_name = re.sub(pattern, '', test_case_name)
    
    # 最后再次清理任何可能的空白字符
    return test_case_name.strip()

def process_file(input_path, output_path):
    sheets = ['Release']
    result_data = read_excel_sheets(input_path, sheets)
    # 清理测试用例名称
    result_data['Test Case Name'] = result_data['Test Case Name'].apply(clean_test_case_name)
    
    # 提取测试用例编号
    result_data['Test Case Number'] = result_data['Test Case Number'].apply(extract_test_case_number)
    # 删除 'Test Case Number' 为空的行
    result_data.dropna(subset=['Test Case Number'], inplace=True)
    # 删除 'Result' 列中的 NaN 值
    result_data.dropna(subset=['Result'], inplace=True)

    # 删除 'Result' 列中为空字符串或只包含空格的行
    result_data = result_data[result_data['Result'].str.strip() != '']
    
    # 替换 'Result' 列中的 'P' 为 'Pass' 和 'F' 为 'Fail'
    result_data['Result'] = result_data['Result'].replace({'P': 'Pass', 'F': 'Fail'})
    
    # 保存处理过的数据到 CSV 文件
    result_data.to_csv(output_path,  index=False, encoding='utf-8-sig')

