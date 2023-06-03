import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

def send_email(receiver, userName, userID, token, client_ip, clien_browser, client_time):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    link = f'{os.getenv("CLIENT_URL")}/reset-password?token={token}&userID={userID}'
    message = MIMEText(
        f'<html>'
        f'<body>'
        f'<div>Dear <i>{userName}</i>,</div>'
        f'<p><strong>Click this link to reset your password:</strong></p>'
        f'<p><a href="{link}">Reset Password</a></p>'
        f'<div>If you did not request a password reset, please ignore this email.</div>'
        f'<br/>'
        f'<div>'
            f'<div><b>IP Address</b>: {client_ip if (client_ip) else "No data"}</div>'
            f'<div><b>Browser</b>: {clien_browser if (clien_browser) else "No data"}</div>'
            f'<div><b>Time</b>: {client_time if (client_time) else "No data"}</div>'
        f'</div>'
        f'<br/>'
        f'<div>Regards,</div>'
        f'<div><b>Student Management System</b> team.</div>'
        f'</body>'
        f'</html>',
        'html'
    )
    message['From'] = formataddr(
        (str(Header('Student Management System', 'utf-8')), sender))
    message['To'] = formataddr(
        (str(Header('User', 'utf-8')), receiver))
    message['Subject'] = Header('Reset Password', 'utf-8')
    try:
        smtpObj = smtplib.SMTP_SSL('smtp.zoho.com', 465)
        smtpObj.login(sender, password)
        smtpObj.sendmail(sender, [receiver], message.as_string())
        smtpObj.quit()
        return True
    except smtplib.SMTPException as e:
        print(e)
        return False