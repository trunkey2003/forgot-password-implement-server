from services.database_connection_service import get_connection
import bcrypt

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
                    return {'password_reset_hashed_token': row[1]}
            return ""
