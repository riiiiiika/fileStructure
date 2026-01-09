from flask import request, jsonify
from app.facial import service
from app.facial import facial_bp

@facial_bp.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}

    # ★追加：どの動画を分析するか（VideoDBのID）
    video_id = data.get("video_id")
    if not video_id:
        return jsonify({"error": "video_id is required"}), 400

    interval = int(data.get("interval", 5))
    BUCKET = "mimic_video"

    # ★変更：latest ではなく video_id 指定で分析
    result = service.analyze_video_by_id(video_id=int(video_id), bucket_name=BUCKET, interval_sec=interval)
    return jsonify(result)
