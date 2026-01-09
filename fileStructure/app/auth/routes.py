# from app.auth import auth_bp
# from flask import request, jsonify
# from app.models import User
# from app.extensions import db, bcrypt
# from flask_jwt_extended import create_access_token


# @auth_bp.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()#クライアントから送信されたJSONデータを取得
#     #各項目を分ける
#     username = data.get('username')
#     email = data.get('email')
#     password = data.get('password')
#     # DBにユーザーが存在するか確認
#     user = User.query.filter_by(email=email).first()
#     if user:
#         return jsonify({'message': 'ユーザーが登録されています'}), 400
#     # パスワードをハッシュ化して保存
#     password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
#     # 新しいユーザーを作成してDBに保存
#     user = User(username=username, email=email, password=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({'message': 'ユーザー登録成功'}), 201

# # ログイン用のルート
# @auth_bp.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')
# # データベースの User テーブルから、入力された email と一致するユーザーを1件だけ取り出す。
#     user = User.query.filter_by(email=email).first()
#     #ユーザーがいない or パスワードが一致しなければエラーにする
#     if not user or not bcrypt.check_password_hash(user.password, password):
#         return jsonify({'message': '無効なメールまたはパスワード'}), 401
#     #ログイン成功したユーザーIDを使って JWT アクセストークンを作成する。
#     jwt_token = create_access_token(identity=str(user.id))
#     # set_acssess_cookies(response, jwt_token)

#     return jsonify({'message': jwt_token}), 200


#################################################

from flask import request, jsonify
from flask_jwt_extended import set_access_cookies, unset_access_cookies, jwt_required, get_jwt_identity

from app.auth import auth_bp
from app.auth.services import register_services, login_services, verify_token_service, reset_token_service, \
    forget_password, updated_password
from app.core.email_service import email_verification, send_password_reset_email
from app.models import User


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    allowed_keys = ["username", "email", "password"]
    if set(data.keys()) != set(allowed_keys):
        return jsonify({"error": "Invalid data"}), 400
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    # try:
    result = register_services(username, email, password)
    # url_for = result.get("url_for")
    print(result)
    return "hello"
    # verification_token = result.get("verification_token")
    # user = result.get("user")


    # email_verification(user.get("email"), verification_token)

    # response = jsonify({
    #     "url_for" : url_for,
    #     "status": "success",
    #     "is_verified": {
    #         "id": user.get("id"),
    #         "is_verified" : user.get("is_verified"),
    #     },
    # }), 201

    # return response
    # except Exception as e:
    #     return jsonify({"RegisterError": str(e)}), 400

@auth_bp.route("/verify/<token>", methods=["GET"])
def verify_token(token):
    try:
        token = token.strip()
        result = verify_token_service(token)
        return jsonify({"Verified": result}), 200
    except Exception as e:
        return jsonify({"error": "Invalid verified token" + str(e)}), 400

@auth_bp.route("/reset-token", methods=["POST"])
def reset_token():
    try:
        data = request.get_json()
        user_id = data.get("isVerified").get("id")
        is_verified = data.get("isVerified").get("is_verified")
        result = reset_token_service(user_id, is_verified)
        print(result)
        email_verification(result.get("email"), result.get("verification_token"))
        response = jsonify({
            "status": "reset_token success",
        })
        return response, 200
    except Exception as e:
        print(str(e))
        return jsonify({"reset-token error": str(e)}), 400

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    token = forget_password(email)
    # print(email)
    # print(token)
    if token:
        send_password_reset_email(email, token)
        return jsonify({"message": "Password reset link sent to your email."}), 200

    return jsonify({"message": "email not exist"}), 400

@auth_bp.route("/reset-password/<token>", methods=['POST'])
def reset_password_token(token):
    data = request.get_json()
    token = token.strip()
    password = data.get('password')

    return updated_password(token, password)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    # Key စစ်ဆေးခြင်း
    allowed_keys = ["email", "password"]
    if not data or set(data.keys()) != set(allowed_keys):
        return jsonify({"error": "Invalid data"}), 400

    email = data.get("email")
    password = data.get("password")

    try:
        # Service ကနေ Token String ပဲ ယူမယ်
        result = login_services(email, password)

        if result.get("is_verified") is False:
            return jsonify({"id": result.get("id"),
                            "is_verified": result.get("is_verified"),}), 200

        access_token = result.get("access_token")
        user_data = result.get("user")

        # Response တည်ဆောက်မယ်
        response = jsonify({
            "Login": "Success",
            "user": user_data,
            "authenticated": True
        })

        # Cookie ထည့်မယ် (Manual Set Cookie)
        # Config ထဲက set_access_cookies() ထက် ဒါက ပိုသေချာပါတယ်
        response.set_cookie(
            key="token",  # Config name နဲ့ တူရမယ်
            value=access_token,  # Token string အစစ်
            httponly=True,  # JavaScript ဖတ်မရအောင် (Security)
            samesite="Lax",  # Localhost အတွက် "Lax" သုံးမှရမယ် (IMPORTANT!)
            secure=False,  # Localhost မို့လို့ False
            max_age=3600          # သက်တမ်း ၁ နာရီ (လိုရင်ထည့်ပါ)
        )

        return response, 200

    except Exception as e:
        return jsonify({"LoginError": str(e)}), 401

@auth_bp.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"Logout": "Success"})
    unset_access_cookies(response)
    return response

@auth_bp.route("/check-auth", methods=["GET"])
@jwt_required()
def check_auth():
    try:
        # (၂) Token ထဲမှာ ဝှက်ထည့်ပေးလိုက်တဲ့ identity (User ID) ကို ပြန်ဆွဲထုတ်တာပါ
        current_user_id = get_jwt_identity()

        # (၃) DB ထဲမှာ အဲ့ဒီ ID ရှိတဲ့ User ကို ရှာမယ်
        user = User.query.get(current_user_id)

        # User DB မှာမရှိတော့ရင် (ဥပမာ - အကောင့်ဖျက်လိုက်တာမျိုး)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # (၄) Frontend ကို ပြန်ပို့မယ့် Data (Password မထည့်ရ)
        return jsonify({
            "status": "success",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_verified": user.is_verified
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500