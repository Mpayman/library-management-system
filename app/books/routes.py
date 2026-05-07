from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from ..decorators import staff_required
from ..extensions import db
from ..models import Book, Loan, User
from ..services import apply_book_filters, checkout_book, create_or_update_book, return_book


books_bp = Blueprint("books", __name__)


@books_bp.route("/")
def list_books():
    query = Book.query.options(joinedload(Book.author))
    books = apply_book_filters(query, request.args).order_by(Book.title.asc()).all()
    return render_template("books/list.html", books=books)


@books_bp.route("/<int:book_id>")
def book_detail(book_id):
    book = Book.query.options(joinedload(Book.author)).filter_by(id=book_id).first_or_404()
    active_loans = (
        Loan.query.options(joinedload(Loan.member))
        .filter_by(book_id=book_id, returned_at=None)
        .order_by(Loan.checked_out_at.desc())
        .all()
    )
    recent_history = (
        Loan.query.options(joinedload(Loan.member))
        .filter_by(book_id=book_id)
        .order_by(Loan.checked_out_at.desc())
        .limit(8)
        .all()
    )
    members = (
        User.query.filter_by(role="member", is_active_account=True).order_by(User.full_name.asc()).all()
        if current_user.is_authenticated and current_user.is_staff
        else []
    )
    return render_template(
        "books/detail.html",
        book=book,
        active_loans=active_loans,
        recent_history=recent_history,
        members=members,
    )


@books_bp.route("/add", methods=["GET", "POST"])
@staff_required
def add_book():
    if request.method == "POST":
        try:
            create_or_update_book(request.form)
            db.session.commit()
        except ValueError as error:
            db.session.rollback()
            flash(str(error), "danger")
        else:
            flash("Book added successfully.", "success")
            return redirect(url_for("books.list_books"))

    return render_template("books/form.html", book=None)


@books_bp.route("/<int:book_id>/edit", methods=["GET", "POST"])
@staff_required
def edit_book(book_id):
    book = db.get_or_404(Book, book_id)

    if request.method == "POST":
        try:
            create_or_update_book(request.form, book=book)
            db.session.commit()
        except ValueError as error:
            db.session.rollback()
            flash(str(error), "danger")
        else:
            flash("Book details updated successfully.", "success")
            return redirect(url_for("books.book_detail", book_id=book.id))

    return render_template("books/form.html", book=book)


@books_bp.route("/<int:book_id>/checkout", methods=["POST"])
@login_required
def checkout(book_id):
    book = db.get_or_404(Book, book_id)

    if current_user.is_staff:
        member_id = request.form.get("member_id")
        member = User.query.filter_by(id=member_id, role="member").first()
        if member is None:
            flash("Please choose a valid library member.", "danger")
            return redirect(url_for("books.book_detail", book_id=book.id))
    else:
        member = current_user

    try:
        checkout_book(book, member, current_user, request.form.get("notes"))
        db.session.commit()
    except ValueError as error:
        db.session.rollback()
        flash(str(error), "danger")
    else:
        flash(f"'{book.title}' has been checked out successfully.", "success")

    return redirect(url_for("books.book_detail", book_id=book.id))


@books_bp.route("/<int:book_id>/return/<int:loan_id>", methods=["POST"])
@login_required
def check_in(book_id, loan_id):
    loan = Loan.query.filter_by(id=loan_id, book_id=book_id).first_or_404()

    if not current_user.is_staff and loan.member_id != current_user.id:
        abort(403)

    try:
        return_book(loan, current_user)
        db.session.commit()
    except ValueError as error:
        db.session.rollback()
        flash(str(error), "danger")
    else:
        flash(f"'{loan.book.title}' has been returned.", "success")

    return redirect(url_for("books.book_detail", book_id=book_id))
