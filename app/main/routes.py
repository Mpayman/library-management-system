from flask import Blueprint, render_template
from flask_login import current_user, login_required

from ..models import Book, Loan, User


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    featured_books = Book.query.order_by(Book.created_at.desc()).limit(3).all()
    return render_template("index.html", featured_books=featured_books)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_staff:
        stats = {
            "books": Book.query.count(),
            "members": User.query.filter(User.role == "member").count(),
            "active_loans": Loan.query.filter(Loan.returned_at.is_(None)).count(),
            "available_books": Book.query.filter(Book.available_copies > 0).count(),
        }
        recent_loans = Loan.query.order_by(Loan.checked_out_at.desc()).limit(6).all()
    else:
        stats = {
            "books": Book.query.count(),
            "my_loans": Loan.query.filter_by(member_id=current_user.id, returned_at=None).count(),
            "history": Loan.query.filter_by(member_id=current_user.id).count(),
            "available_books": Book.query.filter(Book.available_copies > 0).count(),
        }
        recent_loans = (
            Loan.query.filter_by(member_id=current_user.id)
            .order_by(Loan.checked_out_at.desc())
            .limit(6)
            .all()
        )

    recent_books = Book.query.order_by(Book.updated_at.desc()).limit(6).all()

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_loans=recent_loans,
        recent_books=recent_books,
    )
