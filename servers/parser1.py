import pandas as pd

def read_excel(file_path):
    """ 讀取 Excel 檔案 """
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading file: {e}")
        return pd.DataFrame()


def process_dataframe(df, task_id=None):
    
    """ 處理 DataFrame：重命名、過濾和清理數據 """
    try:
        if task_id:
            original_header = df.columns[0]
            df.rename(columns={original_header: 'Task ID'}, inplace=True)
            print("DataFrame after renaming:\n", df.head())  

            df = df[df['Task ID'] == task_id]
            print("DataFrame after filtering by task_id:\n", df.head()) 
            df.loc[:, 'Task ID'] = original_header
            df = df.drop(columns=['Unnamed: 2'])

        df.iloc[:, 2:] = df.iloc[:, 2:].applymap(lambda x: x.strip().replace('\r', '').replace('\n', '') if isinstance(x, str) else x)
        df = df[~df.iloc[:, 2:].applymap(lambda x: x in ['NP_x000D_', 'NP', 'NS', 'NS_x000D_', 'NA', 'NA_x000D_']).all(axis=1)]
        return df
    except Exception as e:
        print(f"Error processing DataFrame: {e}")
        return pd.DataFrame()


def process_and_ignore_np(df):
    """ 遍歷每一行，合併非 'NP' 值到 C 欄 """
    try:
        new_rows = []
        for index, row in df.iterrows():
            non_np_values = [str(row[col]).strip() for col in df.columns[2:] if 'NP_x000D_' not in str(row[col]).strip()]

            if len(non_np_values) > 1:
                for val in non_np_values:
                    new_row = row.copy()
                    new_row[df.columns[2]] = val
                    for col in df.columns[3:]:
                        new_row[col] = 'NP_x000D_'
                    new_rows.append(new_row)
            else:
                df.at[index, df.columns[2]] = non_np_values[0] if non_np_values else 'NP_x000D_'

        for new_row in new_rows:
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        return df.iloc[:, :3]
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

def save_to_excel(df, output_path):
    """ 儲存 DataFrame 到 Excel 檔案 """
    try:
        df.to_excel(output_path, index=False)
    except Exception as e:
        print(f"Error saving file: {e}")



def process_file(file_path, output_path):
    """处理上传的文件并保存为 XLSX"""
    task_id = 'SC'
    df = read_excel(file_path)
    result_df = process_dataframe(df, task_id)

    if not result_df.empty:
        result_df = process_and_ignore_np(result_df)
        save_to_excel(result_df, output_path)
        return output_path
    else:
        print("No matching data found.")
        return None
