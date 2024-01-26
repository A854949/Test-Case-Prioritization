from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask import request
from werkzeug.utils import secure_filename
import os
import parser1
import parser2
import csv
import pymysql


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True  # 如果需要自动重载模板，可以添加这行
CORS(app, resources={r"/.*": {"origins": "http://15.34.25.120:8080"}})



# 添加以下行以允許 iframe 嵌入
app.config['X-Frame-Options'] = 'SAMEORIGIN'


# MySQL数据库连接配置，请替换成你的实际数据库连接信息
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '854949',
    'database': 'test',
}


@app.route('/health', methods=['GET'])
def health():
    return 'ok'


@app.route('/', methods=['GET'])
def front_end():
    return render_template("index.html")


@app.route('/execute_query', methods=['POST'])
def execute_query():
    '''
    改為動態欄位: https://hackmd.io/@JYU/rkANQ8XLL
    '''
    try:
        # 获取POST请求中的JSON数据
        data = request.get_json()
        # 获取SQL查询语句
        sql_query = data.get('query', '')
        # 输出查询语句，方便调试
        print('Received SQL Query:', sql_query)
        # 连接到MySQL数据库
        conn = pymysql.connect(**db_config)
        # 创建游标对象
        cursor = conn.cursor()
        # 执行SQL查询
        cursor.execute(sql_query)
        # 获取查询结果
        results = cursor.fetchall()
        # 输出查询结果，方便调试
        print('Query Results:', results)
        # 关闭游标和连接
        cursor.close()
        conn.close()
        # 将结果以JSON格式返回
        return jsonify({'result': results})

    except Exception as e:
        return jsonify({'error': str(e)})
   
    # from flask import Flask, send_file


# @app.route('/get-dropdown-data', methods=['GET'])
# def get_dropdown_data():
#     try:
#         conn = pymysql.connect(**db_config)
#         cursor = conn.cursor()

#         # 获取 Task ID 数据
#         cursor.execute('SELECT DISTINCT `Task ID` FROM abc ORDER BY `Task ID`')
#         task_id = [taskid[0] for taskid in cursor.fetchall()]

#         # 获取 Platform Name 数据
#         cursor.execute('SELECT DISTINCT `Platform Name` FROM abc ORDER BY `Platform Name`')
#         platform_names = [name[0] for name in cursor.fetchall()]

#         # 获取 HW Phase 数据
#         cursor.execute('SELECT DISTINCT `Hw Phase` FROM abc ORDER BY `Hw Phase`')
#         hw_phases = [phase[0] for phase in cursor.fetchall()]

#         # 获取 Category 数据
#         cursor.execute('SELECT DISTINCT `Category` FROM abc ORDER BY `Category`')
#         categories = [category[0] for category in cursor.fetchall()]

#         # 获取 Case Title 数据
#         cursor.execute('SELECT DISTINCT `Case Title` FROM abc ORDER BY `Case Title`')
#         case_titles = [title[0] for title in cursor.fetchall()]


#         cursor.close()
#         conn.close()

#         return jsonify({
#             'taskIds': task_id,
#             'platformNames': platform_names,
#             'hwPhases': hw_phases,
#             'categories': categories,
#             'caseTitles': case_titles
#         })

#     except Exception as e:
#         return jsonify({'error': str(e)})

@app.route('/task_report', methods=['GET', 'POST'])
def task_report():
    if request.method == 'GET':
        # 处理GET请求
        return render_template('task_report.html')
    elif request.method == 'POST':
        # 处理POST请求
        try:
            data = request.get_json()
            task_id = data.get('taskId')
            task_title = data.get('taskTitle')
            testing_site = data.get('testingSite')
            owner = data.get('owner')
            start_date = data.get('startDate')
            end_date = data.get('endDate')

            # 构建 SQL 插入语句
            insert_sql = """
            INSERT INTO taskReport (`Task ID`, `Task Title`, `Testing Site`, `Owner`, `Start Date`, `End Date`)
            VALUES (%s, %s, %s, %s, %s, %s)
            """

            # 执行插入操作
            conn = pymysql.connect(**db_config)
            with conn.cursor() as cursor:
                cursor.execute(insert_sql, (task_id, task_title, testing_site, owner, start_date, end_date))
                conn.commit()

            return jsonify({'message': 'Task report added successfully'})

        except Exception as e:
            # 在出错时返回错误信息
            return jsonify({'error': str(e)}), 500

@app.route('/get_task_reports', methods=['GET'])
def get_task_reports():
    try:
        # 連接到 MySQL 數據庫
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # 執行查詢以獲取所有任務報告
        cursor.execute('SELECT `Task ID`, `Task Title`, `Testing Site`, `Owner`, `Start Date`, `End Date` FROM taskReport')
        task_reports = cursor.fetchall()
        
        # 將查詢結果轉換為字典列表
        tasks = []
        for report in task_reports:
            tasks.append({
                'taskId': report[0],
                'taskTitle': report[1],
                'testingSite': report[2],
                'owner': report[3],
                'startDate': report[4],
                'endDate': report[5]
            })

        cursor.close()
        conn.close()

        return jsonify(tasks)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/edit_task', methods=['POST'])
def edit_task():
    try:
        # 从请求中获取 JSON 数据
        data = request.get_json()
        task_id = data.get('taskId')
        task_title = data.get('taskTitle')
        testing_site = data.get('testingSite')
        owner = data.get('owner')
        start_date = data.get('startDate')
        end_date = data.get('endDate')

        # 构建 SQL 更新语句
        update_sql = """
        UPDATE taskReport SET 
            `Task Title` = %s,
            `Testing Site` = %s,
            `Owner` = %s,
            `Start Date` = %s,
            `End Date` = %s
        WHERE `Task ID` = %s
        """

        # 执行更新操作
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            cursor.execute(update_sql, (task_title, testing_site, owner, start_date, end_date, task_id))
            conn.commit()

        return jsonify({'message': 'Task updated successfully'})


    except Exception as e:
        # 返回错误信息
        return jsonify({'error': str(e)}), 500


@app.route('/delete_task', methods=['POST'])
def delete_task():
    try:
        # 从请求中获取 JSON 数据
        data = request.get_json()
        task_id = data.get('taskId')

        # 构建 SQL 删除语句
        delete_task_report_sql = "DELETE FROM taskReport WHERE `Task ID` = %s"
        delete_abc_records_sql = "DELETE FROM abc WHERE `Task ID` = %s"


        # 执行删除操作
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            cursor.execute(delete_task_report_sql, (task_id,))
            cursor.execute(delete_abc_records_sql, (task_id,))

            conn.commit()

        return jsonify({'message': 'Task deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_task_data/<taskId>', methods=['GET'])
def get_task_data(taskId):
    try:
        # 连接到数据库
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # 执行查询以获取特定任务的数据
        cursor.execute('SELECT * FROM taskReport WHERE `Task ID` = %s', (taskId,))
        task = cursor.fetchone()

        if task is None:
            return jsonify({'error': 'Task not found'}), 404

        # 将任务数据转换成字典（或者其他您希望的格式）
        task_data = {
            'taskId': task[0],
            'taskTitle': task[1],
            'testingSite': task[2],
            'owner': task[3],
            'startDate': task[4],
            'endDate': task[5]
        }

        cursor.close()
        conn.close()

        return jsonify(task_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_and_process', methods=['POST'])
def upload_and_process():
    file = request.files.get('file')
    
    # 如果有文件被上传
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        save_directory = 'C:/Users/Mika Shih/Desktop/testcasedb/servers/uploads'
        filepath = os.path.join(save_directory, filename)
        file.save(filepath)

        # 使用 parser1 和 parser2 处理文件
        intermediate_output_path = 'C:/Users/Mika Shih/Desktop/testcasedb/servers/intermediate_output.xlsx'
        final_output_path = 'C:/Users/Mika Shih/Desktop/testcasedb/servers/final_output.csv'

        parser1.process_file(filepath, intermediate_output_path)
        parser2.parser2_process(intermediate_output_path, final_output_path)

        # 插入数据到 MySQL
        insert_data_into_mysql(final_output_path)

        return jsonify({'message': 'File processed and data inserted into MySQL'})
    else:
            # 如果没有文件被上传，返回一个错误消息
        return '', 204

def insert_data_into_mysql(csv_file_path):
    conn = pymysql.connect(**db_config)
    with conn.cursor() as cursor:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)  # 跳过标题行
            for row in csvreader:
                # 调整 SQL 语句和数据以匹配您的数据库表结构
                insert_sql = """
                INSERT INTO abc (
                    `UUID`, `Task ID`, `Case Title`, `Pass/Fail`, `Tester`, 
                    `Platform Name`, `SKU`, `Hw Phase`, `OBS`, `Block Type`, 
                    `File`, `KAT/KUT`, `RTA`, `ATT/UAT`, `Run Cycle`, 
                    `Fail Cycle/Total Cycle`, `Case Note`, `Comments`, `Component List`, 
                    `Comment`, `Category`
                ) VALUES (
                    UUID(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
                """
                cursor.execute(insert_sql, tuple(row))
        conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)