from __future__ import annotations

from datetime import timedelta

from sqlalchemy import func

from .extensions import db
from .models import Author, Book, Loan, User
from .utils import utcnow


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.strip().split())


def parse_int(value: str | None, field_name: str, minimum: int | None = None) -> int:
    raw_value = normalize_text(value)
    if not raw_value:
        raise ValueError(f"{field_name} is required.")
    try:
        parsed = int(raw_value)
    except ValueError as error:
        raise ValueError(f"{field_name} must be a number.") from error
    if minimum is not None and parsed < minimum:
        raise ValueError(f"{field_name} must be at least {minimum}.")
    return parsed


def get_or_create_author(author_name: str) -> Author:
    author_name = normalize_text(author_name)
    if not author_name:
        raise ValueError("Author name is required.")

    author = Author.query.filter(func.lower(Author.name) == author_name.lower()).first()
    if author:
        return author

    author = Author(name=author_name)
    db.session.add(author)
    return author


def apply_book_filters(query, filters):
    title = normalize_text(filters.get("title"))
    author = normalize_text(filters.get("author"))
    language = normalize_text(filters.get("language"))
    year = normalize_text(filters.get("year"))
    availability = normalize_text(filters.get("availability"))

    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.join(Book.author).filter(Author.name.ilike(f"%{author}%"))
    if language:
        query = query.filter(Book.language.ilike(f"%{language}%"))
    if year:
        try:
            query = query.filter(Book.publication_year == int(year))
        except ValueError:
            pass
    if availability == "available":
        query = query.filter(Book.available_copies > 0)
    if availability == "checked_out":
        query = query.filter(Book.available_copies == 0)

    return query


def apply_member_filters(query, filters):
    name = normalize_text(filters.get("name"))
    email = normalize_text(filters.get("email"))
    role = normalize_text(filters.get("role"))
    active = normalize_text(filters.get("active"))

    if name:
        query = query.filter(User.full_name.ilike(f"%{name}%"))
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if role:
        query = query.filter(User.role == role)
    if active == "yes":
        query = query.filter(User.is_active_account.is_(True))
    if active == "no":
        query = query.filter(User.is_active_account.is_(False))

    return query


def apply_loan_filters(query, filters, include_history=True):
    status = normalize_text(filters.get("status"))
    member_name = normalize_text(filters.get("member"))
    title = normalize_text(filters.get("title"))

    if title:
        query = query.join(Loan.book).filter(Book.title.ilike(f"%{title}%"))
    if member_name:
        query = query.join(Loan.member).filter(User.full_name.ilike(f"%{member_name}%"))

    if status == "active":
        query = query.filter(Loan.returned_at.is_(None))
    elif status == "returned":
        query = query.filter(Loan.returned_at.is_not(None))
    elif not include_history:
        query = query.filter(Loan.returned_at.is_(None))

    return query


def create_or_update_book(form_data, book: Book | None = None) -> Book:
    title = normalize_text(form_data.get("title"))
    author_name = normalize_text(form_data.get("author"))
    language = normalize_text(form_data.get("language"))
    category = normalize_text(form_data.get("category"))
    shelf_location = normalize_text(form_data.get("shelf_location"))
    description = normalize_text(form_data.get("description"))
    isbn = normalize_text(form_data.get("isbn")) or None

    if not title:
        raise ValueError("Title is required.")
    if not language:
        raise ValueError("Language is required.")

    publication_year = parse_int(form_data.get("publication_year"), "Publication year", 0)
    total_copies = parse_int(form_data.get("total_copies"), "Total copies", 1)

    active_loans = book.loans.filter(Loan.returned_at.is_(None)).count() if book else 0
    if total_copies < active_loans:
        raise ValueError(
            "Total copies cannot be lower than the number of books currently checked out."
        )

    if book is None:
        book = Book()

    requested_available = normalize_text(form_data.get("available_copies"))
    if active_loans:
        available_copies = total_copies - active_loans
    elif requested_available:
        available_copies = parse_int(requested_available, "Available copies", 0)
    else:
        available_copies = total_copies

    if available_copies > total_copies:
        raise ValueError("Available copies cannot be greater than total copies.")

    duplicate_query = Book.query.filter(Book.isbn == isbn) if isbn else None
    if duplicate_query is not None:
        existing = duplicate_query.first()
        if existing and existing.id != book.id:
            raise ValueError("A book with this ISBN already exists.")

    book.title = title
    book.author = get_or_create_author(author_name)
    book.publication_year = publication_year
    book.language = language
    book.category = category or None
    book.shelf_location = shelf_location or None
    book.description = description or None
    book.isbn = isbn
    book.total_copies = total_copies
    book.available_copies = available_copies

    db.session.add(book)
    return book


def create_member_account(
    *,
    full_name: str,
    email: str,
    password: str,
    phone: str | None = None,
    student_id: str | None = None,
    role: str = "member",
    is_active_account: bool = True,
) -> User:
    full_name = normalize_text(full_name)
    email = normalize_text(email).lower()
    phone = normalize_text(phone) or None
    student_id = normalize_text(student_id) or None

    if not full_name:
        raise ValueError("Full name is required.")
    if not email:
        raise ValueError("Email is required.")
    if len(password or "") < 6:
        raise ValueError("Password must be at least 6 characters long.")
    if role not in {"admin", "librarian", "member"}:
        raise ValueError("Invalid role selected.")
    if User.query.filter(func.lower(User.email) == email).first():
        raise ValueError("An account with this email already exists.")
    if student_id and User.query.filter(User.student_id == student_id).first():
        raise ValueError("This student ID is already assigned to another member.")

    member = User(
        full_name=full_name,
        email=email,
        phone=phone,
        student_id=student_id,
        role=role,
        is_active_account=is_active_account,
    )
    member.set_password(password)
    db.session.add(member)
    return member


def update_member_account(
    member: User,
    form_data,
    *,
    allow_admin_role: bool = False,
) -> User:
    full_name = normalize_text(form_data.get("full_name"))
    email = normalize_text(form_data.get("email")).lower()
    phone = normalize_text(form_data.get("phone")) or None
    student_id = normalize_text(form_data.get("student_id")) or None
    role = normalize_text(form_data.get("role")) or member.role
    password = form_data.get("password", "")
    is_active_account = form_data.get("is_active_account") == "on"

    if not full_name:
        raise ValueError("Full name is required.")
    if not email:
        raise ValueError("Email is required.")
    if role not in {"admin", "librarian", "member"}:
        raise ValueError("Invalid role selected.")
    if role == "admin" and not allow_admin_role:
        raise ValueError("Only an admin can assign the admin role.")

    duplicate_email = User.query.filter(func.lower(User.email) == email, User.id != member.id).first()
    if duplicate_email:
        raise ValueError("Another account already uses this email.")

    if student_id:
        duplicate_student_id = User.query.filter(
            User.student_id == student_id,
            User.id != member.id,
        ).first()
        if duplicate_student_id:
            raise ValueError("Another account already uses this student ID.")

    member.full_name = full_name
    member.email = email
    member.phone = phone
    member.student_id = student_id
    member.role = role
    member.is_active_account = is_active_account

    if password:
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        member.set_password(password)

    db.session.add(member)
    return member


def update_profile(member: User, form_data) -> User:
    full_name = normalize_text(form_data.get("full_name"))
    phone = normalize_text(form_data.get("phone")) or None
    student_id = normalize_text(form_data.get("student_id")) or None
    password = form_data.get("password", "")

    if not full_name:
        raise ValueError("Full name is required.")

    if student_id:
        duplicate_student_id = User.query.filter(
            User.student_id == student_id,
            User.id != member.id,
        ).first()
        if duplicate_student_id:
            raise ValueError("Another account already uses this student ID.")

    member.full_name = full_name
    member.phone = phone
    member.student_id = student_id

    if password:
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        member.set_password(password)

    db.session.add(member)
    return member


def checkout_book(book: Book, member: User, processed_by: User, notes: str | None = None) -> Loan:
    if not member.is_active_account:
        raise ValueError("This member account is inactive.")
    if not book.is_available:
        raise ValueError("No copies are currently available for checkout.")

    existing_active_loan = Loan.query.filter_by(
        member_id=member.id,
        book_id=book.id,
        returned_at=None,
    ).first()
    if existing_active_loan:
        raise ValueError("This member already has an active loan for the selected book.")

    loan = Loan(
        member=member,
        book=book,
        checked_out_by=processed_by,
        due_at=utcnow() + timedelta(days=14),
        notes=normalize_text(notes) or None,
    )
    book.available_copies -= 1
    db.session.add(loan)
    db.session.add(book)
    return loan


def return_book(loan: Loan, processed_by: User) -> Loan:
    if loan.returned_at:
        raise ValueError("This loan has already been returned.")

    loan.returned_at = utcnow()
    loan.returned_by = processed_by
    loan.book.available_copies = min(loan.book.available_copies + 1, loan.book.total_copies)
    db.session.add(loan)
    db.session.add(loan.book)
    return loan
