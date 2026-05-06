from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.orm import joinedload

from ..decorators import staff_required
from ..extensions import db
from ..models import Loan, User
from ..services import apply_member_filters, create_member_account, update_member_account


members_bp = Blueprint("members", __name__)


@members_bp.route("/")
@staff_required
def list_members():
    query = User.query
    members = apply_member_filters(query, request.args).order_by(User.full_name.asc()).all()
    return render_template("members/list.html", members=members)


@members_bp.route("/add", methods=["GET", "POST"])
@staff_required
def add_member():
    if request.method == "POST":
        requested_role = request.form.get("role", "member")
        if requested_role == "admin" and current_user.role != "admin":
            flash("Only an admin can create another admin account.", "danger")
            return render_template("members/form.html", member=None)

        try:
            create_member_account(
                full_name=request.form.get("full_name", ""),
                email=request.form.get("email", ""),
                password=request.form.get("password", ""),
                phone=request.form.get("phone", ""),
                student_id=request.form.get("student_id", ""),
                role=requested_role,
                is_active_account=request.form.get("is_active_account") == "on",
            )
            db.session.commit()
        except ValueError as error:
            db.session.rollback()
            flash(str(error), "danger")
        else:
            flash("Member account created successfully.", "success")
            return redirect(url_for("members.list_members"))

    return render_template("members/form.html", member=None)


@members_bp.route("/<int:user_id>")
@staff_required
def member_detail(user_id):
    member = User.query.filter_by(id=user_id).first_or_404()
    recent_loans = (
        Loan.query.options(joinedload(Loan.book))
        .filter_by(member_id=user_id)
        .order_by(Loan.checked_out_at.desc())
        .limit(10)
        .all()
    )
    return render_template("members/detail.html", member=member, recent_loans=recent_loans)


@members_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@staff_required
def edit_member(user_id):
    member = db.get_or_404(User, user_id)

    if request.method == "POST":
        try:
            update_member_account(
                member,
                request.form,
                allow_admin_role=current_user.role == "admin",
            )
            db.session.commit()
        except ValueError as error:
            db.session.rollback()
            flash(str(error), "danger")
        else:
            flash("Member information updated successfully.", "success")
            return redirect(url_for("members.member_detail", user_id=member.id))

    return render_template("members/form.html", member=member)
