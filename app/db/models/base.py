from datetime import datetime
from sqlalchemy.orm import DeclarativeBase

def now():
    return datetime.utcnow()

class Base(DeclarativeBase):
    pass
