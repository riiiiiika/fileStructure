# app/facial/service.py
# ===============================
# 動画を取得して表情・目線分析を行うサービス層
# ===============================

from collections import Counter
import traceback

from app.facial.get_video import get_blob_name_from_video_id, generate_signed_url
from app.facial.ffmpeg import extract_frames_every_n_sec_via_pipe
from app.facial.face_extract import extract_faces_from_frames
from app.facial.emotion_predict import predict_emotion
from app.facial.state_logic import emotion_to_state, gaze_rate_to_score, emotion_summary_to_score
from app.facial.feedback import generate_feedback
from app.facial.gaze import calc_gaze_rate


def analyze_video_by_id(video_id: int, bucket_name: str, interval_sec: int = 5):
    """
    VideoDBのvideo_idからGCS動画を見つけて
    フレーム抽出→目線(正面率)→表情(状態割合)→スコア化して返す

    返却キーは /analyze/save が読む「英キー」に統一
    """
    try:
        # ① VideoDB から blob_name を取得
        blob_name = get_blob_name_from_video_id(video_id, bucket_name)
        if blob_name is None:
            return {"error": "VideoDBに該当動画が見つかりません", "frames_extracted": 0}

        # ② 署名付きURL生成（GET）
        signed_url = generate_signed_url(bucket_name, blob_name)

        # ③ フレーム抽出
        frames = extract_frames_every_n_sec_via_pipe(
            signed_url,
            interval_sec=interval_sec
        )

        # ④ 目線（正面率%）
        gaze_rate = calc_gaze_rate(frames)  # None or float を推奨（calc_gaze_rateをNone返し版に）
        gaze_score = None if gaze_rate is None else gaze_rate_to_score(gaze_rate)

        # ⑤ 顔抽出
        faces = extract_faces_from_frames(frames)

        # ⑥ 表情推論 → 状態判定
        results = []
        for face in faces:
            emotion, confidence = predict_emotion(face["tensor"])
            state = emotion_to_state(emotion, confidence)
            results.append({"state": state})

        # ⑦ summary 作成
        ALL_STATES = ["happiness", "neutral", "tension"]
        states = [r["state"] for r in results]
        total = len(states)
        counter = Counter(states)

        if total > 0:
            summary = {
                state: round(counter.get(state, 0) / total * 100, 1)
                for state in ALL_STATES
            }
        else:
            summary = {state: 0.0 for state in ALL_STATES}

        # ⑧ スコア化
        emotion_score = emotion_summary_to_score(summary)

        # ⑨ フィードバック
        feedback = generate_feedback(summary)

        # ✅ 返却は英キー（/analyze/save と一致させる）
        return {
            "video_name": blob_name,
            "interval_sec": interval_sec,
            "frames_extracted": len(frames),

            "summary": summary,
            "emotion_score": emotion_score,

            "gaze_rate": gaze_rate,
            "gaze_score": gaze_score,

            "feedback": feedback,
        }

    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc(),
            "frames_extracted": 0
        }


# もし最新動画を使う関数が必要なら「video_id」を受け取る形に直す
def analyze_latest_video(video_id: int, bucket_name: str, interval_sec: int = 5):
    """
    ※元コードは video_id が未定義でバグるため、
    引数に video_id を受け取る形に修正
    """
    return analyze_video_by_id(video_id=video_id, bucket_name=bucket_name, interval_sec=interval_sec)
