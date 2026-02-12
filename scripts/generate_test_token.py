#!/usr/bin/env python
"""
Generate a test JWT token for Postman/API testing.

Usage:
    python scripts/generate_test_token.py
    
    Or with custom values:
    python scripts/generate_test_token.py --user-id "123e4567-e89b-12d3-a456-426614174000" --clearance 2
"""
import jwt
import sys
import os
from datetime import datetime, timedelta
from uuid import uuid4

# Add parent directory to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import JWT_SECRET

def generate_token(
    user_id: str = None,
    email: str = "test@intelweave.local",
    clearance_level: int = 2,
    roles: list = None,
    expires_in_hours: int = 24
):
    """Generate a JWT token for testing."""
    if user_id is None:
        user_id = str(uuid4())
    
    if roles is None:
        roles = ["analyst"]
    
    from datetime import timezone
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "clearance_level": clearance_level,
        "roles": roles,
        "iat": now,
        "exp": now + timedelta(hours=expires_in_hours)
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate test JWT token")
    parser.add_argument("--user-id", type=str, help="User ID (UUID)")
    parser.add_argument("--email", type=str, default="test@intelweave.local", help="User email")
    parser.add_argument("--clearance", type=int, default=2, help="Clearance level (1-5)")
    parser.add_argument("--roles", nargs="+", default=["analyst"], help="User roles")
    parser.add_argument("--expires", type=int, default=24, help="Expiration in hours")
    
    args = parser.parse_args()
    
    token = generate_token(
        user_id=args.user_id,
        email=args.email,
        clearance_level=args.clearance,
        roles=args.roles,
        expires_in_hours=args.expires
    )
    
    print("\n" + "="*60)
    print("JWT Token Generated Successfully")
    print("="*60)
    print(f"\nToken:\n{token}\n")
    print("="*60)
    print("\nCopy this token and paste it into Postman's 'token' variable")
    print("   (In Postman: Environments -> IntelWeave Local -> token variable)\n")
    print("="*60)
    print("\nToken Details:")
    print(f"  User ID: {args.user_id or 'Generated UUID'}")
    print(f"  Email: {args.email}")
    print(f"  Clearance Level: {args.clearance}")
    print(f"  Roles: {', '.join(args.roles)}")
    print(f"  Expires: {args.expires} hours\n")

