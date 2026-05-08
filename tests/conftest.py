from pathlib import Path
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app  # noqa: E402
from app.config import Config  # noqa: E402
from app.extensions import db  # noqa: E402
from app.seed import seed_demo_data  # noqa: E402


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test_library.db"

    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path.as_posix()}"
        SECRET_KEY = "test-secret-key"

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        seed_demo_data()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_client(client):
    def do_login(email, password):
        return client.post(
            "/auth/login",
            data={"email": email, "password": password},
            follow_redirects=True,
        )

    return do_login
