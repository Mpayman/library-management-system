from datetime import timedelta

from .extensions import db
from .models import Author, Book, Loan, User
from .utils import utcnow


def seed_demo_data() -> bool:
    if User.query.first():
        return False

    admin = User(
        full_name="Ariana Noor",
        email="admin@library.local",
        role="admin",
        phone="+93 700 000 001",
        student_id="ADM-001",
    )
    admin.set_password("admin123")

    librarian = User(
        full_name="Farid Omari",
        email="librarian@library.local",
        role="librarian",
        phone="+93 700 000 002",
        student_id="LIB-001",
    )
    librarian.set_password("librarian123")

    member_one = User(
        full_name="Lina Ahmadi",
        email="member1@library.local",
        role="member",
        phone="+93 700 000 003",
        student_id="STU-101",
    )
    member_one.set_password("member123")

    member_two = User(
        full_name="Omid Rahimi",
        email="member2@library.local",
        role="member",
        phone="+93 700 000 004",
        student_id="STU-102",
    )
    member_two.set_password("member123")

    db.session.add_all([admin, librarian, member_one, member_two])

    orwell = Author(name="George Orwell")
    walker = Author(name="Alice Walker")
    harari = Author(name="Yuval Noah Harari")
    hosseini = Author(name="Khaled Hosseini")
    db.session.add_all([orwell, walker, harari, hosseini])
    db.session.flush()

    books = [
        Book(
            title="1984",
            author=orwell,
            publication_year=1949,
            language="English",
            isbn="9780451524935",
            category="Dystopian Fiction",
            shelf_location="A1-04",
            description="A classic novel about surveillance, power, and resistance.",
            total_copies=4,
            available_copies=3,
        ),
        Book(
            title="The Color Purple",
            author=walker,
            publication_year=1982,
            language="English",
            isbn="9780156028356",
            category="Historical Fiction",
            shelf_location="B2-11",
            description="An intimate story of resilience, family, and voice.",
            total_copies=3,
            available_copies=3,
        ),
        Book(
            title="Sapiens",
            author=harari,
            publication_year=2011,
            language="English",
            isbn="9780062316097",
            category="History",
            shelf_location="C3-02",
            description="A sweeping exploration of human history and society.",
            total_copies=5,
            available_copies=4,
        ),
        Book(
            title="The Kite Runner",
            author=hosseini,
            publication_year=2003,
            language="English",
            isbn="9781594631931",
            category="Drama",
            shelf_location="A4-06",
            description="A moving novel about friendship, guilt, and redemption.",
            total_copies=2,
            available_copies=2,
        ),
    ]
    db.session.add_all(books)
    db.session.flush()

    active_loan = Loan(
        member=member_one,
        book=books[0],
        checked_out_by=librarian,
        checked_out_at=utcnow() - timedelta(days=2),
        due_at=utcnow() + timedelta(days=12),
        notes="Issued during orientation week.",
    )

    past_loan = Loan(
        member=member_two,
        book=books[2],
        checked_out_by=admin,
        returned_by=admin,
        checked_out_at=utcnow() - timedelta(days=20),
        due_at=utcnow() - timedelta(days=6),
        returned_at=utcnow() - timedelta(days=8),
        notes="Returned in good condition.",
    )

    db.session.add_all([active_loan, past_loan])
    db.session.commit()
    return True
