from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Iterable

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import JWT_SECRET

bearer = HTTPBearer(auto_error=False)

@dataclass
class CurrentUser:
    user_id: str
    email: str
    clearance_level: int = 1
    roles: list[str] = None

def _unauthorized(msg: str = "Unauthorized"):
    raise HTTPException(status_code=401, detail=msg)

def decode_token(token: str) -> CurrentUser:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except Exception as e:
        print(f"JWT Decode Error: {e}") # Debug logging
        _unauthorized("Invalid token")

    return CurrentUser(
        user_id=str(payload.get("sub") or ""),
        email=str(payload.get("email") or ""),
        clearance_level=int(payload.get("clearance_level") or 1),
        roles=list(payload.get("roles") or []),
    )

def get_current_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer)) -> CurrentUser:
    if creds is None or not creds.credentials:
        _unauthorized("Missing bearer token")
    return decode_token(creds.credentials)

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
