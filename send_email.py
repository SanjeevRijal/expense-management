from flask import url_for
from flask_mail import Message
from config import mail


def send_password_reset_email(user):
    reset_url = url_for('verify_token', token=user.reset_token, _external=True)
    msg = Message('Password Reset Request', sender='hopsanjeev@gmail.com', recipients=[user.email])
    msg.html = f''' <p>Dear {user.name},</p>
    <p>You recently requested to reset the password for your account. Click the button below to proceed.</p>
    <p><a href="{reset_url}" style="background-color:#4CAF50;border:none;color:white;padding:15px 32px;text-align:center;text-decoration:none;display:inline-block;font-size:16px;margin:4px 2px;cursor:pointer;border-radius:10px;">Reset Password</a></p>
    <p>This password reset link is only valid for the next one hour.<p>
    <p>If you did not request a password reset, please ignore this email or reply to let us know. <p>

    '''
    mail.send(msg)
