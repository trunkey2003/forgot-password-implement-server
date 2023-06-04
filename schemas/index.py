from apiflask.validators import Length
from marshmallow_dataclass import dataclass
from dataclasses import field
from typing import Optional


@dataclass
class ForgotPasswordSchema:
    email: str = field(
        metadata={'required': True, 'validate': Length(
            min=3, max=100), 'description': 'Email address of the user'}
    )
    captcha_value: str = field(
        metadata={'required': True, 'validate': Length(
            min=6, max=6), 'description': 'Captcha value'})
    captcha_id: str = field(
        metadata={'required': True, 'validate': Length(
            min=36, max=36), 'description': 'Captcha ID'})


@dataclass
class VerifyPasswordTokenSchema:
    token: str = field(
        metadata={'required': True, 'validate': Length(
            min=3, max=100), 'description': 'Token sent to the user\'s email address'})
    userID: int = field(
        metadata={'required': True, 'description': 'User ID of the user'})
    
@dataclass
class ResetPasswordSchema:
    password: str = field(
        metadata={'required': True, 'validate': Length(
            min=6, max=100), 'description': 'New password for the user'})
    token: str = field(
        metadata={'required': True, 'validate': Length(
            min=3, max=100), 'description': 'Token sent to the user\'s email address'})
    userID: int = field(
        metadata={'required': True, 'description': 'User ID of the user'})
    
    
@dataclass
class GenerateCaptchaSchema:
    previous_captcha_id: Optional[str] = field(
        metadata={'required': False, 'validate': Length(
            min=36, max=36), 'description': 'Previous captcha ID'})
    
    