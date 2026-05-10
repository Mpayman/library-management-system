from app.models import User


def test_member_registration_creates_new_account(client, app):
    response = client.post(
        "/auth/register",
        data={
            "full_name": "New Student",
            "email": "newstudent@example.com",
            "phone": "+93 799 999 999",
            "student_id": "STU-999",
            "password": "secret123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Registration complete" in response.data

    with app.app_context():
        user = User.query.filter_by(email="newstudent@example.com").first()
        assert user is not None
        assert user.role == "member"


def test_login_redirects_to_dashboard(auth_client):
    response = auth_client("admin@library.local", "admin123")

    assert response.status_code == 200
    assert b"Dashboard" in response.data
    assert b"Ariana" in response.data
