from flask import *
from flask_cors import CORS
import os
import json
from pprint import pprint

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

#リマインダの登録
@app.route("/remind",methods=["POST"]) 
def add_remind():
    data = json.loads(request.data.decode('utf-8'))
    pprint(data)
    try:
        db=dbctl.ManageRemainderDB('remind.db')
        sql=f"""
            INSERT INTO tasks(name,since,until,music_id,latest)
            VALUES('{data["name"]}','{data["since"]}','{data["until"]}',{data["music"]},datetime('now','localtime'));
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

#データの取得
@app.route("/reference",methods=["POST"])
def get_remind():
    data=json.loads(request.data.decode('utf-8'))
    #pprint(data)
    #print(data["fake"] if "fake" in data else "NONE")#キーが存在するかをチェックする手段
    try:
        db=dbctl.ManageRemainderDB('remind.db')
        result=db.query_1(
            f"""SELECT * FROM tasks;"""
        )
    except Exception as err:
        print('\x1b[37m\x1b[41m',type(err),err,'\x1b[0m')
        return Response(status=400,response=json.dumps({"reason":str(type(err))+' '+str(err)}))
    else:
        return Response(status=200,response=json.dumps(result))

#以下、Flask外プログラム

if __name__=="__main__":
	port=int(os.getenv("PORT",5000))
	app.run(debug=True)
