import pandas as pd
from openpyxl import load_workbook
import os 
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
                test_cases = data.iloc[6:, [0, 1, 7, 8]]
                test_cases.columns = ['Test Case Number', 'Test Case Name', 'Result', 'Comment']
                test_cases['BIOS Version'] = bios_version
                test_cases = test_cases[['BIOS Version', 'Test Case Number', 'Test Case Name', 'Result', 'Comment']]
                all_data = pd.concat([all_data, test_cases], ignore_index=True)
    return all_data

def to_excel_text_format(df):
    return df

def process_file(input_path, output_path):
    sheets = ['CoreTestCase', 'EpSCTestCase']
    result_data = read_excel_sheets(input_path, sheets)
    result_data = to_excel_text_format(result_data)
    result_data.to_csv(output_path, index=False, encoding='utf-8-sig')
