from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
import os
import parser1, parser2, parser3, parser4
import csv
import pymysql
import mysql.connector
import uuid
from pymysql import IntegrityError
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from datetime import datetime


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True 
CORS(app, resources={r"/.*": {"origins": "http://15.34.25.120:5010"}})

app.secret_key = '50cd37e7457bb6734b052414f4896dc8' 

app.config['X-Frame-Options'] = 'SAMEORIGIN'


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '854949',
    'database': 'test',
}

def get_db_connection():
    conn = pymysql.connect(**db_config)
    return conn

@app.route('/health', methods=['GET'])
def health():
    return 'ok'



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test_case_sit', methods=['GET', 'POST'], endpoint='test_case_sit')
def index_sit():
    return render_template('test_case_sit.html')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    def validate_email(self, field):
        if not field.data.endswith('@hp.com'):
            raise ValidationError('Please use your HP email address.')
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    
            
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit(): 
       
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s", (form.username.data,))
        if cursor.fetchone():
            form.username.errors.append('This username is already used. Please use a different username.')

        cursor.execute("SELECT * FROM users WHERE email = %s", (form.email.data,))
        if cursor.fetchone():
            form.email.errors.append('This email is already used. Please use a different email address.')

        if not form.errors:
            user_id = str(uuid.uuid4())
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            cursor.execute("INSERT INTO users (UUID, username, email, password) VALUES (%s, %s, %s, %s)",
                           (user_id, form.username.data, form.email.data, hashed_password))
            conn.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))

        cursor.close()
        conn.close()

    return render_template('register.html', form=form) 

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s", (form.username.data,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user[3], form.password.data): 
            session['username'] = form.username.data  
            return redirect(url_for('index')) 
        else:
            flash('Invalid username or password.', 'danger')

        cursor.close()
        conn.close()

    return render_template('login.html', form=form)


class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')

        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, form.email.data))
        conn.commit()

        flash('Your password has been updated successfully.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', form=form)



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

#SIT

@app.route('/execute_query', methods=['POST'])
def execute_query():
    '''
    改為動態欄位: https://hackmd.io/@JYU/rkANQ8XLL
    '''
    try:
        data = request.get_json()
        sql_query = data.get('query', '')
        print('Received SQL Query:', sql_query)
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        print('Query Results:', results)
        cursor.close()
        conn.close()
        return jsonify({'result': results})

    except Exception as e:
        return jsonify({'error': str(e)})
    
@app.route('/comparison_sit')
def comparison_sit():
    if not session.get('username'):
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT DISTINCT `Task ID` FROM taskReport')
    task_ids = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('comparison_sit.html', task_ids=task_ids)


@app.route('/get-sit-test-cases', methods=['POST'])
def get_sit_test_cases():
    task_ids = request.json.get('taskIds', [])
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    query = """
    SELECT `Task ID`, `Case Title`, `Pass/Fail`, `Tester`, `Platform Name`, `SKU`, 
    `Hw Phase`, `OBS`, `Block Type`, `File`, `KAT/KUT`, `RTA`, `ATT/UAT`, 
    `Run Cycle`, `Fail Cycle/Total Cycle`, `Case Note`, `Comments`, `Component List`, 
    `Comment`, `Category`
    FROM abc WHERE `Task ID` IN (%s)
    """
    format_strings = ','.join(['%s'] * len(task_ids))
    cursor.execute(query % format_strings, tuple(task_ids))

    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)


@app.route('/task_report_sit', methods=['GET', 'POST'])
def task_report_sit():
    if not session.get('username'):
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('task_report_sit.html')
    elif request.method == 'POST':
        try:
            data = request.get_json()
            task_id = data.get('taskId')
            task_title = data.get('taskTitle')
            testing_site = data.get('testingSite')
            start_date = data.get('startDate')
            end_date = data.get('endDate')
            creator = session.get('username')
            created_at = datetime.now().strftime('%Y/%m/%d %H:%M')
            insert_sql = """
            INSERT INTO taskReport (`Task ID`, `Task Title`, `Testing Site`, `Start Date`, `End Date`, `Creator`, `Created_at`)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            conn = pymysql.connect(**db_config)
            with conn.cursor() as cursor:
                cursor.execute(insert_sql, (task_id, task_title, testing_site, start_date, end_date, creator, created_at))
                conn.commit()

            return jsonify({'message': 'Task report added successfully'})

        except IntegrityError as e:

            if e.args[0] == 1062:
                return jsonify({'error': 'Task ID already exists.'}), 400
            else:
                return jsonify({'error': 'An unexpected database error occurred.'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/get_task_reports_sit', methods=['GET'])
def get_task_reports_sit():
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute('SELECT `Task ID`, `Task Title`, `Testing Site`, `Start Date`, `End Date`, `Creator`, `Created_at` FROM taskReport')
        task_reports = cursor.fetchall()
        
        tasks = []
        for report in task_reports:
            tasks.append({
                'taskId': report[0],
                'taskTitle': report[1],
                'testingSite': report[2],
                'startDate': report[3],
                'endDate': report[4],
                'creator': report[5],
                'createdAt': report[6].strftime('%Y/%m/%d %H:%M') if report[6] else None
            })

        cursor.close()
        conn.close()

        return jsonify(tasks)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/edit_task_sit', methods=['POST'])
def edit_task_sit():
    try:
        data = request.get_json()
        task_id = data.get('taskId')
        task_title = data.get('taskTitle')
        testing_site = data.get('testingSite')
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        creator = session.get('username')
        created_at = datetime.now().strftime('%Y/%m/%d %H:%M')       
        update_sql = """
        UPDATE taskReport SET 
            `Task Title` = %s,
            `Testing Site` = %s,
            `Start Date` = %s,
            `End Date` = %s,
            `Creator` = %s, 
            `Created_at` = %s   
        WHERE `Task ID` = %s
        """
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            cursor.execute(update_sql, (task_title, testing_site, start_date, end_date, creator, created_at, task_id))
            conn.commit()

        return jsonify({'message': 'Task updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/delete_task_sit', methods=['POST'])
def delete_task_sit():
    try:
        data = request.get_json()
        task_id = data.get('taskId')

        check_creator_sql = "SELECT `Creator` FROM taskReport WHERE `Task ID` = %s"
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            cursor.execute(check_creator_sql, (task_id,))
            creator = cursor.fetchone()
            if not creator or creator[0] != session.get('username'):
                return jsonify({'error': 'You are not authorized to delete this task report.'}), 403

        delete_task_report_sql = "DELETE FROM taskReport WHERE `Task ID` = %s"
        delete_abc_records_sql = "DELETE FROM abc WHERE `Task ID` = %s"

        with conn.cursor() as cursor:
            cursor.execute(delete_task_report_sql, (task_id,))
            cursor.execute(delete_abc_records_sql, (task_id,))
            conn.commit()

        return jsonify({'message': 'Task deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_task_unverified_sit', methods=['POST'])
def delete_task_unverified_sit():
    try:
        data = request.get_json()
        task_id = data.get('taskId')

        delete_abc_records_sql = "DELETE FROM abc WHERE `Task ID` = %s"

        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            cursor.execute(delete_abc_records_sql, (task_id,))
            conn.commit()

        return jsonify({'message': 'Task deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_and_process_sit', methods=['POST'])
def upload_and_process_sit():
    file = request.files.get('file')
    
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        save_directory = 'C:/Users/Mika Shih/Desktop/testcasedb_UAT/servers/uploads'
        filepath = os.path.join(save_directory, filename)
        file.save(filepath)

        intermediate_output_path = 'C:/Users/Mika Shih/Desktop/testcasedb_UAT/servers/intermediate_output.xlsx'
        final_output_path = 'C:/Users/Mika Shih/Desktop/testcasedb_UAT/servers/final_output.csv'

        parser1.process_file(filepath, intermediate_output_path)
        parser2.parser2_process(intermediate_output_path, final_output_path)

        insert_data_into_mysql_sit(final_output_path)

        return jsonify({'message': 'File processed and data inserted into database'})
    else:
        return '', 204

def insert_data_into_mysql_sit(csv_file_path):
    conn = pymysql.connect(**db_config)
    with conn.cursor() as cursor:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader) 
            for row in csvreader:
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

#BIOS       
@app.route('/test_case_bios', methods=['GET', 'POST'], endpoint='test_case_bios')
def index_bios():
    return render_template('/test_case_bios.html')
 
@app.route('/task_report_bios', methods=['GET', 'POST'])
def task_report_bios():
    if not session.get('username'):
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('task_report_bios.html')
    elif request.method == 'POST':
        try:
            data = request.get_json()
            raw_bios_version = data.get('biosVersion', '').replace('_', ' ') 
            creator = session.get('username')
            created_at = datetime.now().strftime('%Y/%m/%d %H:%M')
            insert_sql = """
            INSERT INTO biosTaskReport (`BIOS Version`, `Creator`, `Created_at`)
            VALUES (%s, %s, %s)
            """

            conn = pymysql.connect(**db_config)  
            with conn.cursor() as cursor:
                cursor.execute(insert_sql, (raw_bios_version, creator, created_at))
                conn.commit()

            return jsonify({'message': 'Task report added successfully'})

        except IntegrityError as e:
            if e.args[0] == 1062:
                return jsonify({'error': 'BIOS Version already exists.'}), 400
            else:
                return jsonify({'error': 'An unexpected database error occurred.'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/get_task_reports_bios', methods=['GET'])
def get_task_reports_bios():
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute('SELECT `BIOS Version`,`Creator`, `Created_at` FROM biosTaskReport')
        task_reports = cursor.fetchall()

        tasks = []
        for report in task_reports:
            tasks.append({
                'biosVersion': report[0],
                'creator': report[1],
                'createdAt': report[2].strftime('%Y/%m/%d %H:%M') if report[2] else None
            })

        cursor.close()
        conn.close()

        return jsonify(tasks)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/edit_task_bios', methods=['POST'])
def edit_task_bios():
    try:
        data = request.get_json()
        bios_version = data.get('biosVersion')
        creator = session.get('username')
        created_at = datetime.now().strftime('%Y/%m/%d %H:%M')       
        update_sql = """
        UPDATE biosTaskReport SET 
            `Creator` = %s, 
            `Created_at` = %s   
        WHERE `BIOS Version` = %s
        """
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            cursor.execute(update_sql, (creator, created_at, bios_version))
            conn.commit()

        return jsonify({'message': 'Task updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/delete_task_bios', methods=['POST'])
def delete_task_bios():
    try:
        data = request.get_json()
        bios_version = data.get('biosVersion')

        check_creator_sql = "SELECT `Creator` FROM biosTaskReport WHERE `BIOS Version` = %s"
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            cursor.execute(check_creator_sql, (bios_version,))
            creator = cursor.fetchone()
            if not creator or creator[0] != session.get('username'):
                return jsonify({'error': 'You are not authorized to delete this task report.'}), 403

        delete_task_report_sql = "DELETE FROM biosTaskReport WHERE `BIOS Version` = %s"
        delete_def_records_sql = "DELETE FROM def WHERE `BIOS Version` = %s"

        with conn.cursor() as cursor:
            cursor.execute(delete_task_report_sql, (bios_version,))
            cursor.execute(delete_def_records_sql, (bios_version,))
            conn.commit()

        return jsonify({'message': 'Task deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_task_unverified_bios', methods=['POST'])
def delete_task_unverified_bios():
    try:
        data = request.get_json()
        bios_version = data.get('biosVersion')

        delete_def_records_sql = "DELETE FROM def WHERE `BIOS Version` = %s"

        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            cursor.execute(delete_def_records_sql, (bios_version,))
            conn.commit()

        return jsonify({'message': 'Task deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload_and_process_bios', methods=['POST'])
def upload_and_process_bios():
    file = request.files.get('file')
    
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        save_directory = 'C:/Users/Mika Shih/Desktop/testcasedb_UAT/servers/uploads'
        filepath = os.path.join(save_directory, filename)
        file.save(filepath)

        final_output_path = 'C:/Users/Mika Shih/Desktop/testcasedb_UAT/servers/final_output.csv'
        
        # 根据文件名选择不同的解析器
        if 'PreRelease' in filename:
            parser4.process_file(filepath, final_output_path)
        else:
            parser3.process_file(filepath, final_output_path)

        insert_data_into_mysql_bios(final_output_path)

        return jsonify({'message': 'File processed and data inserted into database'})
    else:
        return '', 204

def insert_data_into_mysql_bios(csv_file_path):
    conn = pymysql.connect(**db_config)
    with conn.cursor() as cursor:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader) 
            for row in csvreader:
                insert_sql = """
                INSERT INTO def (
                    `UUID`, `BIOS Version`, `Test Case Number`, `Test Case Name`, `Result`, 
                    `Comment`
                ) VALUES (
                    UUID(), %s, %s, %s, %s, %s
                )
                """
                cursor.execute(insert_sql, tuple(row))
        conn.commit()
    cursor.close()
    conn.close()

@app.route('/comparison_bios')
def comparison_bios():
    if not session.get('username'):
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT DISTINCT `BIOS Version` FROM biosTaskReport')
    bios_versions = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('comparison_bios.html', bios_versions=bios_versions)


@app.route('/get-bios-test-cases', methods=['POST'])
def get_bios_test_cases():
    raw_bios_versions = request.json.get('biosVersions', [])
    bios_versions = [version.strip().replace('_', ' ') for version in raw_bios_versions]
    print("Processed BIOS versions:", bios_versions)

    if not bios_versions:
        return jsonify([])

    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    format_strings = ','.join(['%s'] * len(bios_versions))
    query = """
    SELECT `BIOS Version`, `Test Case Number`, `Test Case Name`, `Result`, `Comment`
    FROM def WHERE `BIOS Version` IN (%s)
    """
    cursor.execute(query % format_strings, tuple(bios_versions))

    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)

# @app.route('/get-dropdown-data', methods=['GET'])
# def get_dropdown_data():
#     try:
#         conn = pymysql.connect(**db_config)
#         cursor = conn.cursor()
            
#         cursor.execute('SELECT DISTINCT `Task ID` FROM abc ORDER BY `Task ID`')
#         task_id = [taskid[0] for taskid in cursor.fetchall()]

#         cursor.execute('SELECT DISTINCT `Platform Name` FROM abc ORDER BY `Platform Name`')
#         platform_names = [name[0] for name in cursor.fetchall()]

#         cursor.execute('SELECT DISTINCT `Hw Phase` FROM abc ORDER BY `Hw Phase`')
#         hw_phases = [phase[0] for phase in cursor.fetchall()]

#         cursor.execute('SELECT DISTINCT `Category` FROM abc ORDER BY `Category`')
#         categories = [category[0] for category in cursor.fetchall()]

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

# @app.route('/comparison')
# def comparison():
#     conn = get_db_connection()
#     cursor = conn.cursor(pymysql.cursors.DictCursor)
#     cursor.execute('SELECT * FROM taskReport')
#     rows = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return render_template('comparison.html', rows=rows)

# @app.route('/get-task-title/<task_id>')
# def get_task_title(task_id):
#     conn = get_db_connection()
#     cursor = conn.cursor(pymysql.cursors.DictCursor)
#     cursor.execute('SELECT `Case Title` FROM abc WHERE `Task ID` = %s', (task_id,))
#     rows = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     titles = [row['Case Title'] for row in rows]
#     return jsonify(titles)

# @app.route('/get-task-details/<taskId>')
# def get_task_details(taskId):
#     caseTitle = request.args.get('caseTitle', '')
#     conn = get_db_connection()
#     cursor = conn.cursor(pymysql.cursors.DictCursor)
#     query = 'SELECT `Pass/Fail`, `Tester`, `Platform Name`, `SKU`, `Hw Phase`, `OBS`, `Block Type`, `File`, `KAT/KUT`, `RTA`, `ATT/UAT`, `Run Cycle`, `Fail Cycle/Total Cycle`, `Case Note`, `Comments`, `Component List`, `Comment`, `Category` FROM abc WHERE `Task ID` = %s AND `Case Title` = %s'
#     cursor.execute(query, (taskId, caseTitle))
#     details = cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return jsonify(details)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)