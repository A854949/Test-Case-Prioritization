import pandas as pd
import os
import re 
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def read_excel_sheets(file_path, sheets):
    all_data = pd.DataFrame()
    bios_version = os.path.splitext(os.path.basename(file_path))[0]
    bios_version = bios_version.replace('_', ' ')
    
    with pd.ExcelFile(file_path, engine='openpyxl') as xls:
        for sheet_name in sheets:
            if sheet_name in xls.sheet_names:
                data = pd.read_excel(xls, sheet_name=sheet_name, header=None, na_filter=False)
                test_cases = data.iloc[34:, [4, 4, 6]]
                test_cases.columns = ['Test Case Number', 'Test Case Name', 'Result']
                test_cases['BIOS Version'] = bios_version
                test_cases['Comment'] = pd.NA
                test_cases = test_cases[['BIOS Version', 'Test Case Number', 'Test Case Name', 'Result', 'Comment']]
                all_data = pd.concat([all_data, test_cases], ignore_index=True)
    return all_data


def extract_test_case_number(test_case_name):
    if pd.isna(test_case_name):
        return None
    test_case_name = str(test_case_name).strip()
    test_case_name = test_case_name.strip()
    
    patterns = [
        r"([A-Za-z]+(?:\.\w+)+)",
        r"(\d+-\d+)"             
    ]
    
    for pattern in patterns:
        match = re.search(pattern, test_case_name)
        if match:
            return match.group(1)
    
    return None

def clean_test_case_name(test_case_name):
    if pd.isna(test_case_name):
        return None
    test_case_name = str(test_case_name).strip()
    
    patterns = [
        r"[A-Za-z]+(?:\.\w+)+", 
        r"\d+-\d+"              
    ]
    
    for pattern in patterns:
        test_case_name = re.sub(pattern, '', test_case_name)
    
    return test_case_name.strip()

def process_file(input_path, output_path):
    sheets = ['Release']
    result_data = read_excel_sheets(input_path, sheets)
    result_data['Test Case Name'] = result_data['Test Case Name'].apply(clean_test_case_name)
    
    result_data['Test Case Number'] = result_data['Test Case Number'].apply(extract_test_case_number)
    result_data.dropna(subset=['Test Case Number'], inplace=True)
    result_data.dropna(subset=['Result'], inplace=True)
    result_data = result_data[result_data['Result'].str.strip() != '']
    result_data['Result'] = result_data['Result'].replace({'P': 'Pass', 'F': 'Fail'})
    result_data.to_csv(output_path,  index=False, encoding='utf-8-sig')

