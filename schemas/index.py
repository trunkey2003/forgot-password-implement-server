from apiflask.validators import Length
from marshmallow_dataclass import dataclass
from dataclasses import field


@dataclass
class ForgotPasswordSchema:
    email: str = field(
        metadata={'required': True, 'validate': Length(
            min=3, max=100), 'description': 'Email address of the user'}
    )


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