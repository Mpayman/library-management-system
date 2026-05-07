# API Documentation

All API endpoints return JSON. Session authentication is required, so sign in through the web interface first when testing in a browser.

## `GET /api/books`

Returns a list of books.

### Query Parameters

- `title`: filter by book title
- `author`: filter by author name
- `language`: filter by book language
- `year`: filter by publication year
- `availability`: `available` or `checked_out`

### Example Response

```json
[
  {
    "id": 1,
    "title": "1984",
    "author": "George Orwell",
    "publication_year": 1949,
    "language": "English",
    "isbn": "9780451524935",
    "category": "Dystopian Fiction",
    "shelf_location": "A1-04",
    "description": "A classic novel about surveillance, power, and resistance.",
    "total_copies": 4,
    "available_copies": 3,
    "created_at": "2026-04-17T12:00:00",
    "updated_at": "2026-04-17T12:00:00"
  }
]
```

## `GET /api/books/<book_id>`

Returns a single book record.

## `GET /api/members`

Staff only. Returns member and staff account records.

### Query Parameters

- `name`: filter by full name
- `email`: filter by email
- `role`: `member`, `librarian`, or `admin`
- `active`: `yes` or `no`

## `GET /api/loans`

Returns loan records.

### Query Parameters

- `title`: filter by book title
- `member`: filter by member name
- `status`: `active` or `returned`

### Behavior

- Admins and librarians see all loans.
- Members only see their own borrowing history.
