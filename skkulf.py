from flask import Flask, request, redirect, jsonify, session, url_for, app
from flask_cors import CORS
from dotenv import load_dotenv
from markupsafe import escape
import os
import pymysql
from datetime import timedelta
import datetime
import lfmodules
import secrets

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False
app.secret_key = os.environ.get('FLASK_SESSION_SECRETKEY')

#테스트를 위한 값임.. 배포 시에는 minutes=20이 적당해보임
#app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=20)

#이 값을 조정해서 세션 지속 시간 결정
session_duration_seconds = 86400


@app.route('/')
def index():
    if 'User_name' in session:
        print("why!!")
        return jsonify({"state": "already_login"})

    return lfmodules.template(lfmodules.getContents(), '<h2>Welcome to 2022 Learning Fair</h2>')



@app.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'User_name' in session:
            print("why!!")
            return jsonify({"state": "already_login"})
        return jsonify({"state" : "no_login"})
    
    elif request.method == 'POST':

        sql = "INSERT INTO user (user_name, user_student_number, user_major, user_login_time, user_type, user_token) VALUES (%s, %s, %s, %s, %s, %s)"

        user_json = request.get_json()
    
        Student_ID = user_json['studentId']
        User_name = user_json['name']
        User_major = user_json['major']
        User_login_time = datetime.datetime.now()
        User_type = user_json['userType']
        User_token = secrets.token_hex(nbytes=32)

        conn = pymysql.connect(host=os.environ.get('DB_URL'),
                       user=os.environ.get('DB_USER'),
                       password=os.environ.get('DB_PASSWORD'),
                       db=os.environ.get('DB_NAME'),
                       charset='utf8')

        with conn.cursor() as cur:
            cur.execute(sql, (User_name, Student_ID, User_major, User_login_time, User_type, User_token))
        conn.commit()
        
        sql2 = f"""SELECT user_id FROM user WHERE user_token = '{User_token}'"""

        with conn.cursor() as cur:
            cur.execute(sql2)
        user_id_db_result = cur.fetchall()


        if User_name in session:
            return jsonify({"state": "already_login"})

        return jsonify({"login":"success","token":User_token,"user_id":user_id_db_result[0][0], "user_name":User_name})



@app.route('/api/session-check', methods=['POST'])
def session_check():
    conn = pymysql.connect(host=os.environ.get('DB_URL'),
                       user=os.environ.get('DB_USER'),
                       password=os.environ.get('DB_PASSWORD'),
                       db=os.environ.get('DB_NAME'),
                       charset='utf8')

    session_check_json = request.get_json()

    #print(session_check_json)
    #print(session)
    #print(session_check_json['name'])

    sql = f"""SELECT user_login_time FROM user WHERE user_token = '{session_check_json['token']}'"""

    with conn.cursor() as cur:
        cur.execute(sql)
    session_check_db_result = cur.fetchall()

    if len(session_check_db_result) > 0:
        cal_time_delta = datetime.datetime.now() - session_check_db_result[0][0]
        #print(datetime.datetime.now())
        #print(session_check_db_result[0][0])
        #print(cal_time_delta.seconds)

    global session_duration_seconds
    if len(session_check_db_result) > 0:
        if cal_time_delta.seconds <= session_duration_seconds:
            return jsonify({"session":"active", "user_name":session_check_json['name']})
        else:
            return jsonify({"session":"deactive"})
    else:
        return jsonify({"session":"deactive"})

    '''
    if session_check_json['token'] in session:
        return jsonify({"session":"active", "user_name":session_check_json['name']})
    else:
        return jsonify({"session":"deactive"})
    '''



@app.route('/api/congrats-videos')
def congrats_vidoes():
    #영상 업데이트 되면 url 바꿔야 함
    congrats_vidoes_json = {
        "president":"https://2022-skku-learning-fair-bucket.s3.ap-northeast-2.amazonaws.com/congrats/president_congrats.mp4",
        "sw_dean":"https://2022-skku-learning-fair-bucket.s3.ap-northeast-2.amazonaws.com/congrats/sw_dean_congrats.mp4",
        "ds_dean":"https://2022-skku-learning-fair-bucket.s3.ap-northeast-2.amazonaws.com/congrats/ds_dean_congrats.mp4"
    }

    return jsonify(congrats_vidoes_json)

@app.route('/api/logout')
def logout():
    session.pop('User_name', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)