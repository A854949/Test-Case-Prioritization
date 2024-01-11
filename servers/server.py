from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
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


@app.route('/get-dropdown-data', methods=['GET'])
def get_dropdown_data():
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # 获取 Task ID 数据
        cursor.execute('SELECT DISTINCT `Task ID` FROM abc ORDER BY `Task ID`')
        task_id = [taskid[0] for taskid in cursor.fetchall()]

        # 获取 Platform Name 数据
        cursor.execute('SELECT DISTINCT `Platform Name` FROM abc ORDER BY `Platform Name`')
        platform_names = [name[0] for name in cursor.fetchall()]

        # 获取 HW Phase 数据
        cursor.execute('SELECT DISTINCT `Hw Phase` FROM abc ORDER BY `Hw Phase`')
        hw_phases = [phase[0] for phase in cursor.fetchall()]

        # 获取 Category 数据
        cursor.execute('SELECT DISTINCT `Category` FROM abc ORDER BY `Category`')
        categories = [category[0] for category in cursor.fetchall()]

        # 获取 Case Title 数据
        cursor.execute('SELECT DISTINCT `Case Title` FROM abc ORDER BY `Case Title`')
        case_titles = [title[0] for title in cursor.fetchall()]


        cursor.close()
        conn.close()

        return jsonify({
            'taskIds': task_id,
            'platformNames': platform_names,
            'hwPhases': hw_phases,
            'categories': categories,
            'caseTitles': case_titles
        })

    except Exception as e:
        return jsonify({'error': str(e)})

    
@app.route('/task_report')  
def task_report():
    return render_template('task_report.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)