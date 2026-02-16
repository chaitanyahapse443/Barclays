from fastapi import APIRouter, HTTPException, Depends
import os
import jwt
from datetime import datetime, timedelta
from passlib.hash import bcrypt
from ..services.rbac_service import get_current_user
from ..services import storage

router = APIRouter()

# For demo: create users table entry on first login if not present
_SECRET = os.environ.get('SECRET_KEY', 'dev-secret')


def _ensure_demo_users():
    # create a simple users store in cases DB (quick demo)
    # uses storage.save_case as a quick persistence hack; in production replace with real user table
    try:
        existing = storage.get_case('USER_STORE')
        if existing:
            return
    except Exception:
        pass
    users = {
        'analyst': {'password': bcrypt.hash('password'), 'roles': ['analyst']},
        'admin': {'password': bcrypt.hash('adminpass'), 'roles': ['analyst', 'admin']},
    }
    storage.save_case({'case_id': 'USER_STORE', 'users': users})


@router.post('/login')
def login(credentials: dict):
    username = credentials.get('username')
    password = credentials.get('password')
    _ensure_demo_users()
    store = storage.get_case('USER_STORE')
    users = store.get('users', {}) if store else {}
    u = users.get(username)
    if not u:
        raise HTTPException(status_code=401, detail='invalid credentials')
    if not bcrypt.verify(password, u.get('password')):
        raise HTTPException(status_code=401, detail='invalid credentials')
    roles = u.get('roles', [])
    payload = {
        'sub': username,
        'roles': roles,
        'iat': datetime.utcnow().timestamp(),
        'exp': (datetime.utcnow() + timedelta(hours=8)).timestamp(),
    }
    token = jwt.encode(payload, _SECRET, algorithm='HS256')
    return {'access_token': token, 'user': {'username': username, 'roles': roles}}
