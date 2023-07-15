from flask import *
from flask_cors import CORS
import os,json,datetime,pathlib
from pprint import pprint

import dbctl

#以下、Flaskレスポンダ
app=Flask(__name__)
CORS(app)

#ブラウザでの来訪者への説明
@app.route("/")
def hello():
    return render_template("index.html")

#レコードの登録
@app.route("/remind",methods=["POST"]) 
def add_remind():
    data = json.loads(request.data.decode('utf-8'))
    now=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    pprint(data)
    try:
        if len(data["musics"])<=0:
            return Response(status=400,response=json.dumps({"reason":"Param `musics`'s length is 0."}))
        db=dbctl.ManageRemainderDB('remind.db')
        db.query_1(f"""
                   INSERT INTO tasks(name,since,until,latest)
                   VALUES('{data["name"]}','{data["since"]}','{data["until"]}','{now}');
                   """)
        result=db.query_1(f"""
                          SELECT id FROM tasks
                          WHERE latest='{now}';
                          """)
        if len(result)!=1:
            return Response(status=500,response=json.dumps({"reason":"Inserted task not found."}))
        for x in range(len(data["musics"])):
            db.query_1(f"""
                       INSERT INTO task_musics(task_id,music_id,play_order,latest)
                       VALUES({result[0]["id"]},{data["musics"][x]},{x},'{now}');
                       """)
    except Exception as err:
        print('\x1b[37m\x1b[41m',type(err),err,'\x1b[0m')
        return Response(status=400,response=json.dumps({"reason":str(type(err))+' '+str(err)}))
    else:
        return Response(status=200)

#レコードの削除
@app.route("/remind/<id>",methods=["DELETE"])
def del_remind(id):
    try:
        db=dbctl.ManageRemainderDB('remind.db')
        result=db.query_1(f"DELETE FROM tasks WHERE id={id};")
    except Exception as err:
        print('\x1b[37m\x1b[41m',type(err),err,'\x1b[0m')
        return Response(status=400,response=json.dumps({"reason":str(type(err))+' '+str(err)}))
    else:
        return Response(status=200,response=json.dumps(result))
        
#リマインドレコードの取得
@app.route("/remind",methods=["GET"])
def get_remind():
    try:
        db=dbctl.ManageRemainderDB('remind.db')
        result=db.query_1(f"""SELECT * FROM tasks ORDER BY until ASC;""")
    except Exception as err:
        print('\x1b[37m\x1b[41m',type(err),err,'\x1b[0m')
        return Response(status=400,response=json.dumps({"reason":str(type(err))+' '+str(err)}))
    else:
        return Response(status=200,response=json.dumps(result))

#音楽レコードの取得
@app.route("/music/list",methods=["GET"])
def get_music_list():
    try:
        db=dbctl.ManageRemainderDB('remind.db')
        result=db.query_1(f"""SELECT * FROM musics ORDER BY latest DESC;""")
        result.insert(0,{"id":-1,"file_name":"未選択"})
    except Exception as err:
        print('\x1b[37m\x1b[41m',type(err),err,'\x1b[0m')
        return Response(status=400,response=json.dumps({"reason":str(type(err))+' '+str(err)}))
    else:
        return Response(status=200,response=json.dumps(result))

#参考 https://elsammit-beginnerblg.hatenablog.com/entry/2021/06/03/230222
# 音楽の追加
@app.route('/music/<filename>', methods=["POST"])
def receive_music(filename):
    #ファイルアップロード
    allowed_extentions=[".mp3",".wav"]
    if not 'file' in request.files: # ファイルがなかった場合
        print("NotFoundError happened")
        return Response(status=400,response=json.dumps({"reason":"File not found"}))
    file = request.files['file']    # データの取り出し
    if file.filename == '':         # ファイル名がなかった場合
        return Response(status=400,response=json.dumps({"reason":"File name is NULL"}))

    suffix = pathlib.Path(file.filename).suffix
    if not suffix in allowed_extentions:
        return Response(status=400,response=json.dumps({"reason":"File extensions is wrong"}))
    file.save(os.path.join("musics",filename))

    now=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    try:
        db=dbctl.ManageRemainderDB('remind.db')
        result=db.query_1(f"INSERT INTO musics(file_name,latest) VALUES('{filename}','{now}');")
    except Exception as err:
        print('\x1b[37m\x1b[41m',type(err),err,'\x1b[0m')
        return Response(status=400,response=json.dumps({"reason":str(type(err))+' '+str(err)}))
    else:
        return Response(status=200,response=json.dumps(result))

#音楽の取得
@app.route("/music/<id>",methods=["GET"])
def send_music(id):
    db=dbctl.ManageRemainderDB('remind.db')
    result=db.query_1(f"SELECT music_name FROM musics WHERE id={id};")
    if len(result)>1:
        return Response(status=500,response=json.dumps({"reason":"Same id records has more than 2."}))
    else:
        return send_file('musics/'+result[0]["music_name"],as_attachment=True)

@app.route("/notification",methods=["GET"])
def calc_notice():
    db=dbctl.ManageRemainderDB('remind.db')
    result=db.query_1(f"""SELECT t.id,t.name,t.since,t.until,t.latest,tm.music_id,m.file_name,tm.play_order
                      FROM tasks t
                      INNER JOIN task_musics tm ON t.id=tm.task_id
                      INNER JOIN musics m ON m.id=tm.music_id
                      WHERE tm.music_id>0;
                      """)
    for x in result:
        x["latest"]=datetime.datetime.strptime(x["latest"],"%Y-%m-%dT%H:%M:%S")
        x["since"]=datetime.datetime.strptime(x["since"],"%Y-%m-%dT%H:%M:%S")
        x["until"]=datetime.datetime.strptime(x["until"],"%Y-%m-%dT%H:%M:%S")
        x["notice"]=((x["until"]-x["since"])*x["play_order"]/4)+x["since"]

    #MIN探索
    table=[]
    now=datetime.datetime.now()
    for x in result:
        if now<=x["notice"]:
            table.append(x)

    table=min(table,key=lambda y:y["notice"])
    table["latest"]=table["latest"].strftime("%Y-%m-%dT%H:%M:%S")
    table["since"] =table["since"].strftime("%Y-%m-%dT%H:%M:%S")
    table["until"] =table["until"].strftime("%Y-%m-%dT%H:%M:%S")
    table["notice"]=table["notice"].strftime("%Y-%m-%dT%H:%M:%S")
    
    return Response(status=200,response=json.dumps(table))

if __name__=="__main__":
    port=int(os.getenv("PORT",8000))
    app.run(host='0.0.0.0',port=port,debug=True)
