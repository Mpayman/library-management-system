from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from ..models import Loan
from ..services import apply_loan_filters


loans_bp = Blueprint("loans", __name__)


@loans_bp.route("/")
@login_required
def active_loans():
    query = Loan.query.options(joinedload(Loan.book), joinedload(Loan.member)).filter(
        Loan.returned_at.is_(None)
    )
    if not current_user.is_staff:
        query = query.filter(Loan.member_id == current_user.id)

    loans = apply_loan_filters(query, request.args, include_history=False).order_by(
        Loan.checked_out_at.desc()
    ).all()
    return render_template("loans/list.html", loans=loans)


@loans_bp.route("/history")
@login_required
def history():
    query = Loan.query.options(joinedload(Loan.book), joinedload(Loan.member))
    if not current_user.is_staff:
        query = query.filter(Loan.member_id == current_user.id)

    loans = apply_loan_filters(query, request.args).order_by(Loan.checked_out_at.desc()).all()
    return render_template("loans/history.html", loans=loans)
