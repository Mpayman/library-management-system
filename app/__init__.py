from pathlib import Path

import click
from flask import Flask, render_template

from .config import Config
from .extensions import db, login_manager
from .seed import seed_demo_data


def create_app(config_object=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    register_blueprints(app)
    register_error_handlers(app)
    register_cli_commands(app)

    @app.shell_context_processor
    def make_shell_context():
        from .models import Author, Book, Loan, User

        return {
            "db": db,
            "Author": Author,
            "Book": Book,
            "Loan": Loan,
            "User": User,
        }

    return app


def register_blueprints(app: Flask) -> None:
    from .api.routes import api_bp
    from .auth.routes import auth_bp
    from .books.routes import books_bp
    from .loans.routes import loans_bp
    from .main.routes import main_bp
    from .members.routes import members_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(books_bp, url_prefix="/books")
    app.register_blueprint(members_bp, url_prefix="/members")
    app.register_blueprint(loans_bp, url_prefix="/loans")
    app.register_blueprint(api_bp, url_prefix="/api")


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(_error):
        db.session.rollback()
        return render_template("errors/500.html"), 500


def register_cli_commands(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        click.echo("Database tables created.")

    @app.cli.command("seed-db")
    def seed_db():
        db.create_all()
        seeded = seed_demo_data()
        message = "Demo data created." if seeded else "Demo data already exists."
        click.echo(message)

    @app.cli.command("reset-db")
    def reset_db():
        db.drop_all()
        db.create_all()
        seed_demo_data()
        click.echo("Database reset and demo data loaded.")
