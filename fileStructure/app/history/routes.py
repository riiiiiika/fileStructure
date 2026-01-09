from flask import jsonify, request
from app import db
from app.history import history_bp
from app.models import GeminiAnalysis, Video, Question

#長い文章を省略するための関数
def truncate(text: str, n: int = 40) -> str:
    if not text:
        return ""
    return text if len(text) <= n else text[:n] + "…"


@history_bp.route("", methods=["GET"])
def list_history():
    """
    履歴一覧
    /api/history?category=長所
    """
    category = request.args.get("category")
## GeminiAnalysis を起点に Video / Question を JOIN
    q = (
        db.session.query(GeminiAnalysis, Video, Question)
        .join(Video, GeminiAnalysis.video_id == Video.id)
        .join(Question, Video.question_id == Question.id)
    )

    if category:
        q = q.filter(Video.category == category)

    rows = q.order_by(Video.created_at.desc()).all()

    result = []
    for analysis, video, question in rows:
        result.append({
            "video_id": video.id,
            "created_at": video.created_at.isoformat(),
            "category": video.category,
            "question_preview": truncate(question.data, 40),
            "grade": analysis.grade,
            "total_score": analysis.total_score,
        })

    return jsonify(result), 200
