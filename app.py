from apiflask import APIFlask
from dotenv import load_dotenv
from flask import request
import uuid
import os
import bcrypt
from datetime import datetime
from captcha.image import ImageCaptcha
import base64


from services.email_service import send_email
from services.database_connection_service import get_connection
from services.verify_service import verify_password_and_get_userdata, verify_captcha

from flask_cors import CORS

from schemas.index import ForgotPasswordSchema, VerifyPasswordTokenSchema, ResetPasswordSchema, GenerateCaptchaSchema


salt = bcrypt.gensalt()
load_dotenv()

app = APIFlask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("CLIENT_URL")}})


@app.get('/api/v1/hello')
@app.doc(description='Hello World!', tags=['Hello'])
def hello():
    return {'message': 'Hello World!'}


@app.get('/api/v1/auth/get-captcha')
@app.doc(description='Captcha', tags=['Captcha'])
@app.input(GenerateCaptchaSchema.Schema, location='query')
def get_captcha(data: GenerateCaptchaSchema):
    try:
        image = ImageCaptcha()
        captcha_value = uuid.uuid4().__str__()[:6]
        captcha_id = uuid.uuid4().__str__()
        dataImage = image.generate(captcha_value)
        base64_data = base64.b64encode(dataImage.getvalue()).decode('utf-8')
        hashed_captcha_value = bcrypt.hashpw(
            captcha_value.encode('utf-8'), salt).decode("utf-8")
        with get_connection() as con:
            with con.cursor() as cur:
                previous_captcha_id = data.previous_captcha_id
                if (previous_captcha_id is not None):
                    cur.execute(
                        "DELETE FROM captcha WHERE captcha_id = :captcha_id", captcha_id=data.previous_captcha_id)
                cur.execute("INSERT INTO captcha (captcha_id, captcha_value) VALUES (:captcha_id, :captcha_value)", {
                            'captcha_id': captcha_id, 'captcha_value': hashed_captcha_value})
                con.commit()
        return {'message': 'Captcha generated', 'captcha_id': captcha_id, 'captcha_image': base64_data}, 200
    except Exception as e:
        print(e)
        return {'message': 'Something went wront, please try again later'}, 500


@app.post('/api/v1/auth/forgot-password')
@app.doc(description='Authentication', tags=['Authentication'])
@app.input(ForgotPasswordSchema.Schema)
def forgot_password(data: ForgotPasswordSchema):
    try:
        with get_connection() as con:
            with con.cursor() as cur:
                verify_captcha_result = verify_captcha(data.captcha_id, data.captcha_value)
                if (verify_captcha_result is False):
                    return {'message': 'Invalid captcha', "isCaptchaVerified": False}, 400
                client_ip = request.remote_addr
                clien_browser = request.headers.get('User-Agent')
                client_time = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
                cur.execute("select * from users where email = :email",
                            email=data.email)
                dataUser = cur.fetchone()
                if dataUser is None:
                    return {'message': 'Email not found', "isCaptchaVerified": True}, 404
                userID = dataUser[0]
                userName = dataUser[6]
                cur.execute(
                    "select COUNT(*) from user_password_reset where user_id = :user_id", user_id=userID)
                dataUserPasswordReset = cur.fetchone()
                attemptsEmailPWReset = dataUserPasswordReset[0]
                if attemptsEmailPWReset >= 5:
                    return {'message': 'Too many attempts', "isCaptchaVerified": True}, 400
                token = uuid.uuid4().__str__()
                print("token: ", token)
                isSent = send_email(data.email, userName, userID, token,
                                    client_ip, clien_browser, client_time)
                if (isSent is False):
                    return {'message': 'Email not sent', "isCaptchaVerified": True}, 500
                hashed_token = bcrypt.hashpw(
                    token.encode("utf-8"), salt).decode("utf-8")
                print("hashed_token 1 : ", hashed_token)
                cur.execute("INSERT INTO user_password_reset (user_id, password_reset_hashed_token) VALUES (:user_id, :password_reset_hashed_token)",
                            {'user_id': userID, 'password_reset_hashed_token': hashed_token})
                con.commit()
                return {'message': 'Email sent', "isCaptchaVerified": True}, 200
    except Exception as e:
        print(e)
        return {'message': 'Something went wront, please try again later'}, 500


@app.get('/api/v1/auth/verify-reset-password-token')
@app.doc(description='Authentication', tags=['Authentication'])
@app.input(VerifyPasswordTokenSchema.Schema, location='query')
def verify_password(data: VerifyPasswordTokenSchema):
    try:
        with get_connection() as con:
            with con.cursor() as cur:
                token = data.token
                userID = data.userID
                data = verify_password_and_get_userdata(token, userID)
                if (data is None):
                    return {'message': 'Invalid token', 'isValid': False}, 404
                password_reset_hashed_token = data['password_reset_hashed_token']
                if (password_reset_hashed_token == ""):
                    return {'message': 'Invalid token', 'isValid': False}, 400
                cur.execute(
                    "DELETE FROM user_password_reset WHERE user_id = :user_id", user_id=userID)
                con.commit()
                cur.execute("INSERT INTO user_password_reset (user_id, password_reset_hashed_token) VALUES (:user_id, :password_reset_hashed_token)", {
                    'user_id': userID, 'password_reset_hashed_token': password_reset_hashed_token})
                con.commit()
                cur.execute(
                    "SELECT email FROM users WHERE user_id = :user_id", user_id=userID)
                dataUser = cur.fetchone()
                email = dataUser[0]
                return {'message': 'Token is valid', 'isValid': True, 'email': email}, 200
    except Exception as e:
        print(e)
        return {'message': 'Something went wront, please try again later', 'isValid': False}, 500


@app.post('/api/v1/auth/reset-password')
@app.doc(description='Authentication', tags=['Authentication'])
@app.input(ResetPasswordSchema.Schema, location='json')
def reset_password(data: ResetPasswordSchema):
    try:
        with get_connection() as con:
            with con.cursor() as cur:
                token = data.token
                userID = data.userID
                password = data.password
                data = verify_password_and_get_userdata(token, userID)
                if (data is None):
                    return {'message': 'Invalid token'}, 400
                hashed_password = bcrypt.hashpw(
                    password.encode("utf-8"), salt).decode("utf-8")
                cur.execute("UPDATE users SET password = :password WHERE user_id = :user_id", {
                            'password': hashed_password, 'user_id': userID})
                con.commit()
                cur.execute(
                    "DELETE FROM user_password_reset WHERE user_id = :user_id", user_id=userID)
                con.commit()
                return {'message': 'Password reset successfully'}, 200
    except Exception as e:
        print(e)
        return {'message': 'Something went wront, please try again later'}, 500
