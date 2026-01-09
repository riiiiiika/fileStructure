# DB接続情報やJWT秘密鍵を.envファイルから読み込む設定クラス


import os
from dotenv import load_dotenv
# .env ファイルを読み込む
load_dotenv()

class Config:
    DATABASE_USER = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_HOST = os.getenv("DATABASE_HOST")
    DATABASE_NAME = os.getenv("DATABASE_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #jwtの秘密鍵
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    #GCSの認証情報ファイルのパス
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

