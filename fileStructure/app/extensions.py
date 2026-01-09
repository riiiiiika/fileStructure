#これを create_app() で init_app() することでどこでも import して使えるようになる。
#インスタンス置き場
#拡張機能のインスタンスを作成しておく場所

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from google.cloud import storage
from flask_mail import Mail



db = SQLAlchemy()
bcrypt = Bcrypt()#パスワードのハッシュ化と検証を行うため
jwt = JWTManager()#ログインして各機能を使うためのカギを作る
gcs=storage.Client()#Google Cloud Storageを使うためのクライアントインスタンス
mail = Mail()


