from flask import Flask, Blueprint
from config import Config
from app.profile import profile_bp
from app.extensions import db, bcrypt, jwt, mail
from app.auth import auth_bp
from app.interview import interview_bp
from app.video import video_bp
from app.facial import facial_bp
from app.analyze import analyze_bp
from app.history import history_bp
from flask_cors import CORS

def create_app():
    #flaskを使うという宣言
    app = Flask(__name__)

    #config.pyの設定を読み込む
    app.config.from_object(Config)

    # cross_origins = current_app.config["CROSS_ORIGINS"]
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": ["http://localhost:5173"]}})

    from app.models import User,Question

    #extensionsの初期化
    db.init_app(app)
    bcrypt.init_app(app)
    #jwtの初期化
    jwt.init_app(app)

    mail.init_app(app)
    
    #Blueprintの登録
    #profile_bpをappに登録
    app.register_blueprint(profile_bp)
    #auth_bpをappに登録、URLの接頭辞を/api/authに設定
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    #interview_bpをappに登録、URLの接頭辞を/api/interviewに設定
    app.register_blueprint(interview_bp, url_prefix='/api/interview')
    app.register_blueprint(video_bp, url_prefix='/api/video')
    app.register_blueprint(facial_bp, url_prefix='/api/facial')
    app.register_blueprint(analyze_bp, url_prefix='/api/analyze')
    app.register_blueprint(history_bp, url_prefix='/api/history')
    
    return app
