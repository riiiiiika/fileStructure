# 質問をランダム表示（ラウンドロビン方式）

from flask import Blueprint, jsonify, request,send_file, make_response
from app.interview import interview_bp
from app.models import Question
from flask_jwt_extended import jwt_required
from app.interview.services import arrange_round_robin
import random
from google.cloud import texttospeech
import io
from app.core.tts_service import tts_core



@interview_bp.route('/random-test', methods=['POST'])
#@jwt_required() をつけて認証が必要なルートにする
@jwt_required()
def interview():
    # DBからすべての質問を取得
    questions=Question.query.all()
    # Questionモデル → 辞書リストに変換(フロント側で扱いやすい形式にするため)
    question_dicts = [ {'id': q.id, 'category': q.category, 'data': q.data} for q in questions ]
    # ラウンドロビン方式で「一周単位」でカテゴリを回す
    arranged = arrange_round_robin(question_dicts)
    # 整理した質問リストを返す
    return jsonify(arranged)





# ------------------------------------
# Text-To-Speech（Google TTSで音声生成）

@interview_bp.route("/tts", methods=["POST"])
# @jwt_required()
def text_to_speech():
    # JSONデータを安全に取得（壊れたJSONでもエラーにならない）
    data = request.get_json(silent=True) or {}
    # 読み上げたい文字列
    text = data.get("text")

    # text が空 or None → エラーレスポンス
    if not text:
        return jsonify({"error": "text is required"}), 400
    # TTSのメイン処理は tts_core() に委譲
    return tts_core(text)

    

