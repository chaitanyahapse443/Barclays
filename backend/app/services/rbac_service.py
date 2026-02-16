import os
from fastapi import Depends, HTTPException, Header
import jwt

_SECRET = os.environ.get('SECRET_KEY', 'dev-secret')


def has_role(user: dict, role: str) -> bool:
    return role in user.get('roles', [])


def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail='Missing authorization header')
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise HTTPException(status_code=401, detail='Invalid authorization header')
    token = parts[1]
    try:
        payload = jwt.decode(token, _SECRET, algorithms=['HS256'])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail='Invalid token')

