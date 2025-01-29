import jwt
from datetime import datetime, timedelta
from app.config import settings

datetime_now = datetime.utcnow()


def create_access_token(user_id: int) -> int:
    """Generate JWT access token."""

    access_payload = {
        'user_id': user_id,
        'exp': datetime_now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        'iat': datetime_now,
        'type': 'access'
    }

    to_encode = access_payload.copy()
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(user_id: int) -> int:
    """Generate JWT refresh token."""

    access_payload = {
        'user_id': user_id,
        'exp': datetime_now + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
        'iat': datetime_now,
        'type': 'refresh'
    }

    to_encode = access_payload.copy()
    return jwt.encode(payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str):
    """Decode access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None