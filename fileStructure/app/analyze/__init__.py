from flask import Blueprint

#analyzeという名前でBlueprintを作成
analyze_bp= Blueprint('analyze', __name__)

from . import routes