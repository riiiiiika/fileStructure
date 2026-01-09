from datetime import datetime,timedelta

from flask import jsonify, make_response, url_for, current_app
from flask_jwt_extended import create_access_token
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

from app.extensions import bcrypt, db, jwt
from app.models import User
import secrets

def register_services(username, email, password):
    try:
        user = User.query.filter_by(email=email).first()
        if user:
            raise Exception('User already exists')

        hash_password = bcrypt.generate_password_hash(password).decode('utf-8')


        verification_token = secrets.token_urlsafe(16)
        
        user = User(username=username, email=email, password=hash_password, verification_token=verification_token)

        urlFor = url_for('auth_bp.verify_token', token=verification_token, _external=True)
        return urlFor
        # db.session.add(user)
        # db.session.commit()

        # return {
        # "url_for" : urlFor,
        # "verification_token" : verification_token,
        # "user": {"id": user.id, "username": user.username, "email": user.email, "is_verified": user.is_verified }
        # }

    except Exception as e:
        return {"register_error" : str(e)}

def verify_token_service(token):
    try:
        user = User.query.filter_by(verification_token=token).first()
        if user is None:
            raise Exception('Token does not exist')

        user.is_verified = True
        user.verification_token = None

        db.session.commit()
        return str(user.verification_token)
    except Exception as e:
        return {"verify_token_error" : str(e)}

def reset_token_service(user_id, is_verified):
    try:

        if is_verified == False:
            user = User.query.filter_by(id=user_id).first()
            new_token = secrets.token_urlsafe(16)
            user.verification_token = new_token
            db.session.commit()
            return {
                "email": user.email,
                "verification_token" : new_token,
            }


    except Exception as e:
        return {"reset_token_error" : str(e)}


def forget_password(email):
    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({'message': 'Email not found'}), 404

    s = URLSafeTimedSerializer(current_app.config['ITSDANGEROUS_SECRET_KEY'])
    token = s.dumps(user.id)
    expiry_time = datetime.utcnow() + timedelta(hours=1)

    user.reset_password_token = token
    user.reset_password_token_expiry = expiry_time

    db.session.commit()

    return token

def login_services(email, password):
    # User ရှိမရှိ စစ်မယ်
    user = User.query.filter_by(email=email).first()
    if user is None:
        raise Exception('User does not exist')

    if user.is_verified == False:
       return {
                    "id": user.id,
                   "is_verified": user.is_verified,
               }

    # Password စစ်မယ်
    if not bcrypt.check_password_hash(user.password, password):
        raise Exception('Incorrect password')

    # Token ထုတ်ပေးမယ်
    access_token = create_access_token(identity=str(user.id))

    # Data ပြန်ပို့မယ် (Response Object မဟုတ်ပါ, Dictionary ပါ)
    return {
        "access_token": access_token,
        "user": {"id": user.id, "username": user.username, "email": user.email, "is_verified": user.is_verified}
    }



def updated_password(token, new_password):

    if token is None or new_password is None:
        return jsonify({'message': 'Invalid token or password'}), 401

    s = URLSafeTimedSerializer(current_app.config['ITSDANGEROUS_SECRET_KEY'])

    try:
        user_id = s.loads(token)

    except SignatureExpired:
        return jsonify({'message': 'Your token has expired.'}), 401

    except BadTimeSignature:
        return jsonify({'message': 'Invalid token.'}), 401

    except Exception as e:
        current_app.logger.error(f"Password reset error: {e}")
        return jsonify({'message': 'An internal error occurred.'}), 500

    user = User.query.filter_by(id=user_id).first()

    if user is None:
        return jsonify({'message': 'User not found'}), 404

    if user.reset_password_token == token and user.reset_password_token_expiry > datetime.utcnow():
        print(user.password)
        password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        print(password)
        user.password = password
        print(user.password)
        user.reset_password_token = None
        user.reset_password_token_expiry = None
        db.session.commit()
        return jsonify({'message': 'Password updated'}), 200

    return jsonify({'message': 'error'}), 400