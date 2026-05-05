 # Stacks & Stories Library Management System
 The project is a Flask library management system that was developed as a project with a Python course. It supports librarian and member workflows to support catalog management, member accounts, book checkout and return, search, borrowing history, and role based authentication.

## Features

- Authentication of role of the user; the user is the administrator, librarian, and the member.
- Catalogue browsing, with search by title, author, language, year and availability, visible to the public.
- Staff book management: add, edit, and monitor copies.
- Staff member management: create, edit, activate, and deactivate accounts.
- Checkout and turnaround processes.
- Loan history of books and members.
- JSON API book, members, and loans endpoints.
- SQLite database containing normalized users, authors, books and loans tables.
- Unit tests and integration tests using pytest.
- Teaching folder containing architecture notes and presentation aid.

## Project Structure

```text
library_management_system/
|-- app/
|   |-- api/
|   |-- auth/
|   |-- books/
|   |-- loans/
|   |-- main/
|   |-- members/
|   |-- static/
|   |-- templates/
|   |-- __init__.py
|   |-- config.py
|   |-- decorators.py
|   |-- extensions.py
|   |-- models.py
|   |-- seed.py
|   `-- services.py
|-- docs/
|-- tests/
|-- .gitignore
|-- pytest.ini
|-- requirements.txt
`-- run.py
```

## How to Run

1. Open PowerShell or a terminal in the project folder.
2. Create a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Create the database tables:

   ```powershell
   python -m flask --app run.py init-db
   ```

5. Load demo data:

   ```powershell
   python -m flask --app run.py seed-db
   ```

6. Run the application:

   ```powershell
   python run.py
   ```

7. Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Demo Accounts

- Admin: `admin@library.local` / `admin123`
- Librarian: `librarian@library.local` / `librarian123`
- Member: `member1@library.local` / `member123`

## API Endpoints

Detailed API documentation is in [docs/api.md](docs/api.md).

- `GET /api/books`
- `GET /api/books/<book_id>`
- `GET /api/members`
- `GET /api/loans`

All API routes require login. Staff-only endpoints are marked in the API documentation.

## Database Documentation

- ER and schema notes: [docs/database_schema.md](docs/database_schema.md)
- SQL schema: [docs/schema.sql](docs/schema.sql)

## Running Tests

```powershell
pytest
```

## Notes

- The application uses SQLite for easy classroom setup and submission.
- New public registrations become `member` accounts automatically.
- The staff members have the ability to create librarian and member accounts, whilst only admins can grant the role of admins.
