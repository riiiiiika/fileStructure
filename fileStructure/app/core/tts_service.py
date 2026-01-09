#ランダム表示された質問を音声で読み上げる
from google.cloud import texttospeech
import io
from flask import send_file

 # クライアント初期化
client = texttospeech.TextToSpeechClient()
def tts_core(text):
    # 読み上げるテキスト
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # 声の設定（日本語）
    voice = texttospeech.VoiceSelectionParams(
        language_code="ja-JP",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    # 音声ファイル形式（mp3）
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # mp3 をそのまま返す（保存しない）
    audio_bytes = response.audio_content

    mp3_file = send_file(
        io.BytesIO(audio_bytes),
        mimetype="audio/mpeg",
        as_attachment=False,
        download_name= "question.mp3"
    )

    return mp3_file