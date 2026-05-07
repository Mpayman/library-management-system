from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from ..decorators import staff_required
from ..models import Book, Loan, User
from ..services import apply_book_filters, apply_loan_filters, apply_member_filters


api_bp = Blueprint("api", __name__)


@api_bp.get("/books")
@login_required
def books():
    query = Book.query.options(joinedload(Book.author))
    data = apply_book_filters(query, request.args).order_by(Book.title.asc()).all()
    return jsonify([book.to_dict() for book in data])


@api_bp.get("/books/<int:book_id>")
@login_required
def book_detail(book_id):
    book = Book.query.options(joinedload(Book.author)).filter_by(id=book_id).first_or_404()
    return jsonify(book.to_dict())


@api_bp.get("/members")
@staff_required
def members():
    query = User.query
    data = apply_member_filters(query, request.args).order_by(User.full_name.asc()).all()
    return jsonify([member.to_dict() for member in data])


@api_bp.get("/loans")
@login_required
def loans():
    query = Loan.query.options(joinedload(Loan.book), joinedload(Loan.member))
    if not current_user.is_staff:
        query = query.filter(Loan.member_id == current_user.id)

    data = apply_loan_filters(query, request.args).order_by(Loan.checked_out_at.desc()).all()
    return jsonify([loan.to_dict() for loan in data])
