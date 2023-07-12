from flask import *
from flask_cors import CORS
import os
import json
from pprint import pprint
import datetime

import dbctl

#以下、Flaskレスポンダ
app=Flask(__name__)
CORS(app)

#ブラウザでの来訪者への説明
@app.route("/")
def hello():
    return """
        <h1>Hello! This is Flask server!</h1>
        <h2>Notice:</h2>
        <p>This server is built for reminder software.</p>
        <p>It is not built for website display.</p>
        <br />
        <p>このサーバーは、リマインダーソフトのために構築されています。</p>
        <p>Webサイト表示のためには構築されていません。</p>
    """

#レコードの登録
@app.route("/create/remind",methods=["POST"]) 
def add_remind():
    data = json.loads(request.data.decode('utf-8'))
    now=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    pprint(data)
    try:
        db=dbctl.ManageRemainderDB('remind.db')
        sql=f"""
            INSERT INTO tasks(name,since,until,music,latest)
            VALUES('{data["name"]}','{data["since"]}','{data["until"]}',{data["music"]},'{now}');
        """
        result=db.query_1(sql)
    except Exception as err:
        print('\x1b[37m\x1b[41m',type(err),err,'\x1b[0m')
        return Response(status=400,response=json.dumps({"reason":str(type(err))+' '+str(err)}))
    else:
        if len(result)==0:
            return Response(status=200)
        else:
            return Response(status=500,response=json.dumps({"status":False,"reason":"Running SQLite responce has problem"}))

#レコードの取得
@app.route("/reference/<table>",methods=["POST"])
def get_remind(table):
    data=json.loads(request.data.decode('utf-8'))
    try:
        db=dbctl.ManageRemainderDB('remind.db')
        if table=="remind":
            result=db.query_1(f"""
                            SELECT * FROM tasks
                            WHERE 1=1 
                            {f"AND since>='{data['since_since']}'" if "since_since" in data else ""} 
                            {f"AND since<='{data['since_until']}'" if "since_until" in data else ""} 
                            {f"AND until<='{data['until_since']}'" if "until_since" in data else ""} 
                            {f"AND until<='{data['until_until']}'" if "until_until" in data else ""} 
                            ;
                            """)
        elif table=="music":
            result=db.query_1(f"""
                              SELECT * FROM musics 
                              WHERE 1=1 
                              ;
                              """)
        else:
            return Response(status=400,response=json.dumps({"reason":"Table name Not found"}))
    except Exception as err:
        print('\x1b[37m\x1b[41m',type(err),err,'\x1b[0m')
        return Response(status=400,response=json.dumps({"reason":str(type(err))+' '+str(err)}))
    else:
        return Response(status=200,response=json.dumps(result))

#参考 https://elsammit-beginnerblg.hatenablog.com/entry/2021/06/03/230222
# 音楽の追加
@app.route('/upload/music/<filename>', methods=["POST"])
def get_test(filename):
    print(request.files)
    if 'file' not in request.files: # ファイルがなかった場合
        print("NotFoundError happened")
        return Response(status=400,response=json.dumps({"reason":"File not found"}))
    file = request.files['file']    # データの取り出し
    if file.filename == '':         # ファイル名がなかった場合
        return Response(status=400,response=json.dumps({"reason":"File name is NULL"}))
    file.save(os.path.join("musics",filename))
    print(filename)
    return Response(status=200)

if __name__=="__main__":
	port=int(os.getenv("PORT",8000))
	app.run(host='0.0.0.0',port=port,debug=True)
