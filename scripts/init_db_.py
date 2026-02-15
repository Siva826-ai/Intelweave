from app.db.session import engine
from app.db.models import Base, User
import uuid

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    # Create a seed user for testing
    from sqlalchemy.orm import Session
    with Session(engine) as session:
        seed_emails = ["sivasubramanian035@gmail.com", "admin@intelweave.local"]
        for seed_email in seed_emails:
            user = session.query(User).filter(User.email == seed_email).first()
            if not user:
                print(f"Creating seed user: {seed_email}")
                user = User(
                    user_id=uuid.uuid4(),
                    email=seed_email,
                    full_name="Seed Administrator",
                    clearance_level=2,
                    is_active=True
                )
                session.add(user)
                session.commit()
                print(f"Seed user {seed_email} created.")
            else:
                print(f"Seed user {seed_email} already exists.")

    # Seed a default case
    from app.db.models import Case
    with Session(engine) as session:
        case_title = "Main Investigation: Operation Alpha"
        case = session.query(Case).filter(Case.title == case_title).first()
        if not case:
            print(f"Creating seed case: {case_title}")
            case = Case(
                case_id=uuid.uuid4(),
                title=case_title,
                status="active",
                jurisdiction="Global",
                integrity_score=95.5
            )
            session.add(case)
            session.commit()
            print("Seed case created.")
        else:
            print("Seed case already exists.")

if __name__ == "__main__":
    init_db()