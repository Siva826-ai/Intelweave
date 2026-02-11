from app.db.session import engine
from app.db.models import Base

def init():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init()
    print("DB tables created (SQLAlchemy metadata subset). For full schema, apply schema/postgres.sql.")
