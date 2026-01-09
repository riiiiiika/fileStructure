from flask import request, jsonify
from app.analyze import analyze_bp
from app import db
from app.models import GeminiAnalysis, Video
from app.analyze.service import run_gemini_and_save  # finalizeは呼ばない方針（後述）


@analyze_bp.route("/save", methods=["POST"])
def save_analysis():
    data = request.get_json(silent=True) or {}

    video_id = data.get("video_id")
    facial = data.get("facial") or {}

    if not video_id:
        return jsonify({"error": "video_id is required"}), 400

    video = Video.query.get(int(video_id))
    if not video:
        return jsonify({"error": "video not found"}), 404

    analysis = GeminiAnalysis.query.filter_by(video_id=int(video_id)).first()
    if analysis is None:
        analysis = GeminiAnalysis(video_id=int(video_id))

        # ✅ 新規作成時：未取得は None（DBはNULL）
        analysis.volume_score = None
        analysis.speech_rate_score = None
        analysis.grammar_score = None  # Geminiで後から入る
        # stt_text は別ルートで入れるので触らない

        db.session.add(analysis)

    # 表情
    analysis.emotion_score = facial.get("emotion_score")
    analysis.emotion_summary = facial.get("summary")
    analysis.emotion_feedback = facial.get("feedback")
    analysis.frames_extracted = facial.get("frames_extracted")
    analysis.interval_sec = facial.get("interval_sec")

    # 目線
    analysis.gaze_rate = facial.get("gaze_rate")
    analysis.gaze_score = facial.get("gaze_score")

    db.session.commit()

    return jsonify({
        "message": "analysis saved",
        "analysis_id": analysis.id,
        "video_id": analysis.video_id
    }), 200


@analyze_bp.route("/gemini", methods=["POST"])
def analyze_with_gemini():
    data = request.get_json(silent=True) or {}
    video_id = data.get("video_id")
    if not video_id:
        return jsonify({"error": "video_id is required"}), 400

    analysis = run_gemini_and_save(int(video_id))

    # run_gemini_and_save は失敗時 dict を返す
    if isinstance(analysis, dict) and analysis.get("error"):
        return jsonify(analysis), 400

    if analysis is None:
        return jsonify({"error": "gemini analysis failed (unknown)"}), 400

    # ✅ 重要：service.py 側で finalize_analysis_scores() を呼んでいるならここは不要
    return jsonify({
        "message": "finalized",
        "video_id": int(video_id),
        "total_score": analysis.total_score,
        "grade": analysis.grade
    }), 200


@analyze_bp.route("/stt_dummy", methods=["POST"])
def set_stt_dummy():
    data = request.get_json(silent=True) or {}
    video_id = data.get("video_id")
    stt_text = data.get("stt_text")

    if not video_id or not stt_text:
        return jsonify({"error": "video_id and stt_text are required"}), 400

    analysis = GeminiAnalysis.query.filter_by(video_id=int(video_id)).first()
    if analysis is None:
        analysis = GeminiAnalysis(video_id=int(video_id))

        # ✅ 新規作成時：未取得は None（DBはNULL）
        analysis.volume_score = None
        analysis.speech_rate_score = None
        analysis.grammar_score = None

        db.session.add(analysis)

    analysis.stt_text = stt_text
    db.session.commit()

    return jsonify({"message": "stt_text saved", "video_id": analysis.video_id}), 200
