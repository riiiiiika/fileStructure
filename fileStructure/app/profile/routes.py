from flask import Blueprint, current_app, jsonify
from app.profile import profile_bp
from flask_jwt_extended import jwt_required
import os
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()


@profile_bp.route('/profile', methods=['GET'])
# @jwt_required()
def index():
    client = texttospeech.TextToSpeechClient.from_service_account_file(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )
    return jsonify({"message": client})

# @profile_bp.route('/', methods=['GET'])
# # @jwt_required()
# def index():
#     return "This is the profile index page."