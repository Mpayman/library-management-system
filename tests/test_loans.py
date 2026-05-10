from app.extensions import db
from app.models import Book, Loan, User


def test_member_can_checkout_and_return_a_book(auth_client, client, app):
    auth_client("member1@library.local", "member123")

    with app.app_context():
        book = Book.query.filter_by(title="The Color Purple").first()
        member = User.query.filter_by(email="member1@library.local").first()
        book_id = book.id
        member_id = member.id

    checkout_response = client.post(
        f"/books/{book_id}/checkout",
        data={"notes": "Testing checkout flow"},
        follow_redirects=True,
    )

    assert checkout_response.status_code == 200
    assert b"checked out successfully" in checkout_response.data

    with app.app_context():
        loan = Loan.query.filter_by(book_id=book_id, member_id=member_id, returned_at=None).first()
        book = db.session.get(Book, book_id)
        assert loan is not None
        assert book.available_copies == 2
        loan_id = loan.id

    return_response = client.post(
        f"/books/{book_id}/return/{loan_id}",
        follow_redirects=True,
    )

    assert return_response.status_code == 200
    assert b"has been returned" in return_response.data

    with app.app_context():
        loan = db.session.get(Loan, loan_id)
        book = db.session.get(Book, book_id)
        assert loan.returned_at is not None
        assert book.available_copies == 3
