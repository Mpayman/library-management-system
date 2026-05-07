import pytest

from app.models import Book, User
from app.services import checkout_book, create_or_update_book


def test_create_or_update_book_rejects_duplicate_isbn(app):
    with app.app_context():
        existing_book = Book.query.filter_by(title="1984").first()

        with pytest.raises(ValueError):
            create_or_update_book(
                {
                    "title": "Another Book",
                    "author": "New Author",
                    "publication_year": "2025",
                    "language": "English",
                    "isbn": existing_book.isbn,
                    "category": "Test",
                    "shelf_location": "Z1-01",
                    "total_copies": "1",
                    "available_copies": "1",
                    "description": "Duplicate ISBN example.",
                }
            )


def test_checkout_book_prevents_duplicate_active_loan(app):
    with app.app_context():
        member = User.query.filter_by(email="member1@library.local").first()
        book = Book.query.filter_by(title="1984").first()

        with pytest.raises(ValueError):
            checkout_book(book, member, member)
