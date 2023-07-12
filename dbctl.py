import sqlite3

class ManageRemainderDB():
    def __init__(self,dbname:str) -> None:
        """データベース接続のセットアップ"""
        self.conn=sqlite3.connect(dbname)
        self.conn.row_factory=sqlite3.Row
        self.cur=self.conn.cursor()

    def query_1(self,sql):
        """1つクエリを実行
        戻り値はlist型(INSERT文などでは空list)
        SQLエラーでは'sqlite3.OperationalErrorが発生'"""
        self.cur.execute(sql)
        self.conn.commit()
        result= [dict(row) for row in self.cur.fetchall()]
        return result

    def close(self):
        self.conn.close()
