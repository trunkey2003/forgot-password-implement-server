from services.database_connection_service import get_connection
import bcrypt
from datetime import datetime

def verify_password_and_get_userdata(token: int, userID: str):
    with get_connection() as con:
        with con.cursor() as cur:
            cur.execute(
                "select * from user_password_reset where user_id = :user_id", user_id=userID)
            dataUserPasswordReset = cur.fetchall()
            if dataUserPasswordReset is None or len(dataUserPasswordReset) == 0:
                return None
            for row in dataUserPasswordReset:
                if (bcrypt.checkpw(token.encode("utf-8"), row[1].encode("utf-8"))):
                    expiration_timestamp = row[2]
                    if (expiration_timestamp < datetime.now()):
                        return None
                    return {'password_reset_hashed_token': row[1]}
            return None

def verify_captcha(captcha_id, captcha_value):
    try:
        with get_connection() as con:
            with con.cursor() as cur:
                cur.execute(
                    "SELECT * FROM captcha WHERE captcha_id = :captcha_id", captcha_id=captcha_id)
                dataCaptcha = cur.fetchone()
                if dataCaptcha is None:
                    return False
                captcha_value_db = dataCaptcha[1]
                cur.execute(
                    "DELETE FROM captcha WHERE captcha_id = :captcha_id", captcha_id=captcha_id)
                con.commit()
                return bcrypt.checkpw(captcha_value.encode("utf-8"), captcha_value_db.encode("utf-8")) == True
    except Exception as e:
        print(e)
        return False
