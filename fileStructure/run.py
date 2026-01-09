# アプリケーションのエントリーポイント これで起動
from app import create_app#initの中のcreate_appをimport
from app.extensions import db

app=create_app()
#initの中のcreate_appを実行してappに代入

#直接実行するなら__name__の中身mainになる。
if __name__=="__main__":
    with app.app_context():
        db.create_all()#DBのテーブルを作成
    app.run(debug=True)