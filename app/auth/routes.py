from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func

from ..extensions import db
from ..models import User
from ..services import create_member_account, normalize_text, update_profile


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = normalize_text(request.form.get("email")).lower()
        password = request.form.get("password", "")
        user = User.query.filter(func.lower(User.email) == email).first()

        if user and user.check_password(password) and user.is_active_account:
            login_user(user)
            flash("Welcome back. You are now signed in.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        try:
            create_member_account(
                full_name=request.form.get("full_name", ""),
                email=request.form.get("email", ""),
                password=request.form.get("password", ""),
                phone=request.form.get("phone", ""),
                student_id=request.form.get("student_id", ""),
                role="member",
            )
            db.session.commit()
        except ValueError as error:
            db.session.rollback()
            flash(str(error), "danger")
        else:
            flash("Registration complete. Please sign in with your new account.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        try:
            update_profile(current_user, request.form)
            db.session.commit()
        except ValueError as error:
            db.session.rollback()
            flash(str(error), "danger")
        else:
            flash("Your profile was updated successfully.", "success")
            return redirect(url_for("auth.profile"))

    return render_template("auth/profile.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))
