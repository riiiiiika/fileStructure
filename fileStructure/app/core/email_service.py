from flask import current_app, jsonify
from flask_mail import Message

from app.extensions import mail


def email_verification(email, token):
    frontend_url = current_app.config['FRONTEND_ORIGIN']

    confirm_url = f'{frontend_url}/verify/{token}'

    sender = current_app.config['MAIL_USERNAME']

    print(sender)

    subject = 'メール確認!'

    body = f'''
               {confirm_url} 
            '''

    msg = Message(subject,sender=sender,recipients=[email],body=body)

    try:
        mail.send(msg)
    except Exception as e:
        return jsonify({"message":str(e)}), 500


def send_password_reset_email(email, token):

    frontend_url = current_app.config['FRONTEND_ORIGIN']

    reset_url = f'{frontend_url}/reset-password/{token}'

    sender = current_app.config['MAIL_USERNAME']
    print(sender)
    subject = '新しいパスワード変更のリンク'

    body = f'''
               {reset_url} 
            '''

    msg = Message(subject,sender=sender,recipients=[email],body=body)

    try:
        mail.send(msg)
        print( "1" + msg)
    except Exception as e:
        print ({"message 2":str(e)}), 500