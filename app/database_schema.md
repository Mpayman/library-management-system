# Database Schema Explanation

The project uses a normalized SQLite schema with four main tables:

## 1. `users`

Stores everyone who can log in to the system.

- `id`: primary key
- `full_name`: user's full name
- `email`: unique login email
- `phone`: contact phone number
- `student_id`: optional school identifier
- `role`: `admin`, `librarian`, or `member`
- `password_hash`: hashed password
- `is_active_account`: active/inactive state
- `created_at`: account creation timestamp

## 2. `authors`

Separates author data from books so one author can be linked to many books.

- `id`: primary key
- `name`: unique author name
- `biography`: optional notes

## 3. `books`

Stores each title in the catalog.

- `id`: primary key
- `title`: book title
- `author_id`: foreign key to `authors`
- `publication_year`: year published
- `language`: book language
- `isbn`: optional unique ISBN
- `category`: optional category
- `shelf_location`: where the book is stored
- `description`: short summary
- `total_copies`: total copies owned
- `available_copies`: copies currently available
- `created_at`: when the record was created
- `updated_at`: last update timestamp

## 4. `loans`

Tracks every checkout and return event.

- `id`: primary key
- `member_id`: foreign key to `users`
- `book_id`: foreign key to `books`
- `checked_out_by_id`: staff or member who processed the checkout
- `returned_by_id`: user who processed the return
- `checked_out_at`: checkout timestamp
- `due_at`: due date
- `returned_at`: return timestamp, if returned
- `notes`: optional transaction notes

## Why This Is Normalized

- Authors are stored once and reused by many books.
- Members and staff both live in one `users` table and are separated by role.
- Loan history is stored separately instead of overwriting book data, so the system keeps a permanent history.
- Availability is tracked in `books`, while detailed transaction history remains in `loans`.
