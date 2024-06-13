import pandas as pd
import re


def transfer_min_to_hours(min_str):
    cleaned_str = min_str.replace('_x000D_', '')
    parts = cleaned_str.split('/')
    hours_list = []

    for part in parts:
        clean_min_str = re.sub(r'\D', '', part)  
        if clean_min_str:
            hours = int(clean_min_str) / 60
            hours_list.append(f"{hours:.2f}")
        else:
            hours_list.append("0.00")  

    return '/'.join(hours_list)



def parser2_process(input_file_path, output_file_path):
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
    special_headers = ["KAT/KUT", "ATT/UAT", "Pass/Fail", "OBS"]
    min_to_hours_headers = ["KAT/KUT", "ATT/UAT"]
    replace_str_headers = ["OBS"]
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

    df = pd.read_excel(input_file_path)
    new_df = pd.DataFrame()
    indexes_to_drop = []

    for index, cell_value in df["Unnamed: 3"].items():
        cell_value = cell_value.replace('_x000D_', '')

        pass_fail_match = re.search(r'^(pass|fail|Fail)', cell_value, re.IGNORECASE)
        if pass_fail_match:
            new_df.at[index, "Pass/Fail"] = pass_fail_match.group(1).lower()
        else:
            new_df.at[index, "Pass/Fail"] = ""  
            indexes_to_drop.append(index)

        for header in headers:
            if header == "Pass/Fail":
                continue  

            if header != "Component List":
                if "_x000D_" in cell_value:
                    pattern = re.escape(header) + r":(.*?)_x000D_"
                else:
                    pattern = re.escape(header) + r":(.*?)(?=" + '|'.join([re.escape(next_header) for next_header in headers if next_header != header]) + "|$)"
            else:
                pattern = re.escape(header) + r":(.*?)Comment:"

                parts = re.search(pattern, cell_value, re.DOTALL)
                if parts:
                    clean_value = parts[1].strip().replace('_x000D_', '') 
                    clean_value = clean_value.replace('\n', ' ').replace('\r', ' ')
                    new_df.at[index, header] = clean_value

            parts = re.search(pattern, cell_value, re.DOTALL)
            if parts:
                clean_value = parts[1].strip().replace('_x000D_', '')  
                new_df.at[index, header] = clean_value
           
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


    df.rename(columns={df.columns[1]: "Case Title"}, inplace=True)

   
    for index, cell_value in df["Case Title"].items():
        category_key_parts = cell_value.split(".")
        if len(category_key_parts) >= 2:
            category_key = category_key_parts[0]  
            if category_key == "16":
                category_key += "." + category_key_parts[1]  
            category = category_mapping.get(category_key, "Other") 
            header = "Category"
            new_df.at[index, header] = category

 
    df.drop(indexes_to_drop, inplace=True)


    new_df = new_df[new_df["Pass/Fail"] != ""]

    df = pd.concat([df, new_df], axis=1)

    df = df.drop(columns=["Unnamed: 3"])


    df.to_csv(output_file_path, index=False, encoding='utf-8-sig')

