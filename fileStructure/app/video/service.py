from flask import Blueprint, request, jsonify
from app.models import Video
from app.models import Question
from app import db

def create_video_service(user_id, question_id, category, gcs_url):
    video = Video(
        user_id=user_id,
        question_id=question_id,
        category=category,
        gcs_url=gcs_url
    )
    db.session.add(video)
    db.session.commit()
    return video