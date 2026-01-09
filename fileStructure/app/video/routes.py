from app.video import video_bp
from flask import request, jsonify
from app.extensions import gcs   # あなたがアプリ全体で使っている GCS クライアントを import
from app.video.service import create_video_service
from flask import request, jsonify
from app.models import Question,Video
from app import db   # あなたがアプリ全体で使っている GCS クライアントを import

# あなたの GCS バケット名（変更不要）
BUCKET_NAME = 'mimic_video'


@video_bp.route('/ai-upload', methods=['POST'])
def ai_upload():
    """
    フロントから受け取った filename と contentType を使って、
    Google Cloud Storage に動画をアップロードするための
    「署名付きURL（signed URL）」を発行するエンドポイント。

    フロント側は、この返却された signed_url を使って
    直接 GCS に PUT リクエストを送ることで、
    サーバーを経由せず安全に動画をアップロードできる。
    """

    # --- ① JSON の受け取り ---
    data = request.get_json()
    filename = data.get('filename')         # 保存するファイル名（例: "video_001.mp4"）
    contentType = data.get('contentType')   # MIMEタイプ（例: "video/mp4"）

    # filename と contentType の両方が無いとアップロードできない
    if not filename or not contentType:
        return {'error': 'ファイルを受け取れませんでした。'}, 400

    # --- ② GCS のバケットを取得 ---
    # app/extensions.py で初期化した gcs クライアントを使用
    bucket = gcs.bucket(BUCKET_NAME)

    # --- ③ GCS 上の保存先パスを準備 ---
    # videos/ の下にファイルを置く（例: videos/video_001.mp4）
    blob = bucket.blob(f"videos/{filename}")

    # --- ④ 署名付きURLを生成 ---
    # フロントエンドがこのURLに対して PUT することでアップロードできる
    signed_url = blob.generate_signed_url(
        version="v4",         # 署名バージョン（推奨は v4）
        expiration=900,       # 署名URLの有効期間（秒）→ 15分
        method="PUT",         # PUT でアップロードするための署名
        content_type=contentType  # Content-Type チェック（セキュリティ向上）
    )

    # --- ⑤ フロントへ返すデータ ---
    # フロントは:
    #   axios.put(signed_url, file, { headers: { "Content-Type": contentType } })
    # でアップロードできるようになる
    return jsonify({
        'signed_url': signed_url,            # このURLへPUTするとGCSに保存される
        'file_key': f"videos/{filename}"     # DB保存用のパス
    })

@video_bp.route("/video_save", methods=["POST"])
def create_video():
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    question_id = data.get("question_id")
    gcs_url = data.get("gcs_url")

    if not all([user_id, question_id, gcs_url]):
        return jsonify({"error": "required fields are missing"}), 400

    # ★ここでQuestionDBからcategoryを取得
    q = Question.query.get(question_id)
    if not q:
        return jsonify({"error": "question not found"}), 404

    video = Video(
        user_id=user_id,
        question_id=question_id,
        category=q.category,   # ★自動で入れる
        gcs_url=gcs_url
    )

    db.session.add(video)
    db.session.commit()

    return jsonify({"message": "video created", "video_id": video.id}), 201
