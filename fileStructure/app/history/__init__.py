#面接結果・分析ログを保存＆取得するAPIfrom flask import Blueprint
from flask import Blueprint

history_bp = Blueprint("history", __name__, url_prefix="/api/history")

from . import routes  
