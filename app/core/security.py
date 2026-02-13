from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Iterable
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import JWT_SECRET

bearer = HTTPBearer(auto_error=False)

# Constants for token expiration
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

@dataclass
class CurrentUser:
    user_id: str
    email: str
    clearance_level: int = 1
    roles: list[str] = None

def _unauthorized(msg: str = "Unauthorized"):
    raise HTTPException(status_code=401, detail=msg)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        _unauthorized("Token has expired")
    except jwt.InvalidTokenError:
        _unauthorized("Invalid token")
    except Exception as e:
        print(f"JWT Decode Error: {e}")
        _unauthorized("Could not validate credentials")

def get_current_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer)) -> CurrentUser:
    if creds is None or not creds.credentials:
        _unauthorized("Missing bearer token")
    
    payload = decode_token(creds.credentials)
    
    # Ensure it's an access token
    if payload.get("type") != "access":
        _unauthorized("Invalid token type")

    return CurrentUser(
        user_id=str(payload.get("sub") or ""),
        email=str(payload.get("email") or ""),
        clearance_level=int(payload.get("clearance_level") or 1),
        roles=list(payload.get("roles") or []),
    )

def require_roles(required: Iterable[str]):
    required = set(required)
    def _dep(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        roles = set(user.roles or [])
        if not (roles & required):
            raise HTTPException(status_code=403, detail=f"Forbidden: requires one of roles {sorted(required)}")
        return user
    return _dep

def require_clearance(min_level: int):
    def _dep(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if int(user.clearance_level) < int(min_level):
            raise HTTPException(status_code=403, detail=f"Forbidden: requires clearance >= {min_level}")
        return user
    return _dep