def test_catalog_search_filters_by_title(client):
    response = client.get("/books/?title=1984")

    assert response.status_code == 200
    assert b"1984" in response.data
    assert b"Sapiens" not in response.data


def test_staff_can_add_a_book(auth_client, client):
    auth_client("admin@library.local", "admin123")

    response = client.post(
        "/books/add",
        data={
            "title": "Python Clean Code",
            "author": "Code Mentor",
            "publication_year": "2024",
            "language": "English",
            "isbn": "9781111111111",
            "category": "Programming",
            "shelf_location": "D1-01",
            "total_copies": "2",
            "available_copies": "2",
            "description": "A book about clean coding habits.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Book added successfully" in response.data
    assert b"Python Clean Code" in response.data
