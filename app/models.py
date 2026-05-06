from __future__ import annotations

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db
from .utils import utcnow


class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    biography = db.Column(db.Text, nullable=True)

    books = db.relationship("Book", back_populates="author", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Author {self.name}>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(30), nullable=True)
    student_id = db.Column(db.String(40), nullable=True, unique=True)
    role = db.Column(db.String(20), nullable=False, default="member", index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active_account = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    borrowed_loans = db.relationship(
        "Loan",
        foreign_keys="Loan.member_id",
        back_populates="member",
        lazy="dynamic",
    )
    processed_checkouts = db.relationship(
        "Loan",
        foreign_keys="Loan.checked_out_by_id",
        back_populates="checked_out_by",
        lazy="dynamic",
    )
    processed_returns = db.relationship(
        "Loan",
        foreign_keys="Loan.returned_by_id",
        back_populates="returned_by",
        lazy="dynamic",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self) -> bool:
        return self.is_active_account

    @property
    def is_staff(self) -> bool:
        return self.role in {"admin", "librarian"}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "student_id": self.student_id,
            "role": self.role,
            "is_active_account": self.is_active_account,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    publication_year = db.Column(db.Integer, nullable=False, index=True)
    language = db.Column(db.String(40), nullable=False, index=True)
    isbn = db.Column(db.String(20), nullable=True, unique=True)
    category = db.Column(db.String(80), nullable=True, index=True)
    shelf_location = db.Column(db.String(40), nullable=True)
    description = db.Column(db.Text, nullable=True)
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    available_copies = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)

    author = db.relationship("Author", back_populates="books")
    loans = db.relationship(
        "Loan",
        back_populates="book",
        lazy="dynamic",
        order_by="desc(Loan.checked_out_at)",
    )

    @property
    def checked_out_copies(self) -> int:
        return max(self.total_copies - self.available_copies, 0)

    @property
    def is_available(self) -> bool:
        return self.available_copies > 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author.name if self.author else None,
            "publication_year": self.publication_year,
            "language": self.language,
            "isbn": self.isbn,
            "category": self.category,
            "shelf_location": self.shelf_location,
            "description": self.description,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Book {self.title}>"


class Loan(db.Model):
    __tablename__ = "loans"

    id = db.Column(db.Integer, primary_key=True)
    checked_out_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    due_at = db.Column(db.DateTime, nullable=False)
    returned_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    member_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False, index=True)
    checked_out_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    returned_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    member = db.relationship("User", foreign_keys=[member_id], back_populates="borrowed_loans")
    book = db.relationship("Book", back_populates="loans")
    checked_out_by = db.relationship(
        "User",
        foreign_keys=[checked_out_by_id],
        back_populates="processed_checkouts",
    )
    returned_by = db.relationship(
        "User",
        foreign_keys=[returned_by_id],
        back_populates="processed_returns",
    )

    @property
    def status(self) -> str:
        return "returned" if self.returned_at else "checked_out"

    @property
    def is_overdue(self) -> bool:
        return self.returned_at is None and utcnow() > self.due_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "book": self.book.title if self.book else None,
            "member": self.member.full_name if self.member else None,
            "checked_out_at": self.checked_out_at.isoformat(),
            "due_at": self.due_at.isoformat(),
            "returned_at": self.returned_at.isoformat() if self.returned_at else None,
            "status": self.status,
            "checked_out_by": self.checked_out_by.full_name if self.checked_out_by else None,
            "returned_by": self.returned_by.full_name if self.returned_by else None,
            "notes": self.notes,
        }

    def __repr__(self) -> str:
        return f"<Loan book={self.book_id} member={self.member_id}>"
