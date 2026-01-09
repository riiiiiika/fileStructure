#DBのテーブル定義

from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)

    # role = db.Column(db.String(20), default="user")
    # is_active = db.Column(db.Boolean, default=True)

    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


##########################################


#QuestionDBの定義
class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), unique=False, nullable=False)
    data = db.Column(db.String(255), nullable=False)
class Video(db.Model):
    __tablename__ = "videos"

    id = db.Column(db.Integer, primary_key=True)

    # 紐づけ
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)

    # 冗長だが履歴一覧を高速にするため保持（卒論で説明可能）
    category = db.Column(db.String(50), nullable=False)

    # GCS
    gcs_url = db.Column(db.String(500), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.now)

    # リレーション
    gemini_analysis = db.relationship(
        "GeminiAnalysis",
        back_populates="video",
        uselist=False,
        cascade="all, delete-orphan"
    )
class GeminiAnalysis(db.Model):
    __tablename__ = "gemini_analyses"

    # ==========
    # 基本情報
    # ==========
    id = db.Column(db.Integer, primary_key=True)

    # 1つの動画に対して1つの分析結果
    video_id = db.Column(
        db.Integer,
        db.ForeignKey("videos.id"),
        nullable=False,
        unique=True
    )

    # ==========
    # 表情分析
    # ==========
    emotion_score = db.Column(db.Integer)        # 1〜5
    emotion_summary = db.Column(db.JSON)         # {"happiness":40.0, ...}
    emotion_feedback = db.Column(db.Text)        # コメント
    frames_extracted = db.Column(db.Integer)     # 抽出フレーム数
    interval_sec = db.Column(db.Integer)         # 何秒おきか

    # ==========
    # 目線分析
    # ==========
    gaze_rate = db.Column(db.Float)              # 正面率（%）
    gaze_score = db.Column(db.Integer)           # 1〜5

    # ==========
    # 音声分析（友人担当・後で埋まる）
    # ==========
    volume_score = db.Column(db.Integer, nullable=True)        # 声量 1〜5
    speech_rate_score = db.Column(db.Integer, nullable=True)  # 話速 1〜5

    # ==========
    # STT / 文法（Gemini担当・後で埋まる）
    # ==========
    stt_text = db.Column(db.Text, nullable=True)               # 音声→テキスト
    grammar_score = db.Column(db.Integer, nullable=True)       # 文法評価 1〜5
    grammar_feedback = db.Column(db.Text, nullable=True)       # 文法の短評

    # ==========
    # 総合評価（最後に計算）
    # ==========
    total_score = db.Column(db.Float, nullable=True)
    grade = db.Column(db.String(2), nullable=True)             # A / B / C など
    # 全体フィードバック（Geminiが返す）
    overall_feedback = db.Column(db.Text, nullable=True)
    # 欠損指標リスト
    missing_metrics = db.Column(db.JSON, nullable=True)  # 例: ["volume", "speech_rate"]
    



    # ==========
    # 時刻
    # ==========
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    # ==========
    # リレーション
    # ==========
    video = db.relationship(
        "Video",
        back_populates="gemini_analysis",
    )
