#認証に関するBlueprintの初期化
#ユーザー認証（ログイン・新規登録）
from flask import Blueprint

#authという名前でBlueprintを作成
auth_bp= Blueprint('auth', __name__)

from . import routes