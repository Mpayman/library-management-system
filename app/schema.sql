CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(30),
    student_id VARCHAR(40) UNIQUE,
    role VARCHAR(20) NOT NULL DEFAULT 'member',
    password_hash VARCHAR(255) NOT NULL,
    is_active_account BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL UNIQUE,
    biography TEXT
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    publication_year INTEGER NOT NULL,
    language VARCHAR(40) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    category VARCHAR(80),
    shelf_location VARCHAR(40),
    description TEXT,
    total_copies INTEGER NOT NULL DEFAULT 1,
    available_copies INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    author_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES authors(id)
);

CREATE TABLE loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checked_out_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_at DATETIME NOT NULL,
    returned_at DATETIME,
    notes TEXT,
    member_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    checked_out_by_id INTEGER NOT NULL,
    returned_by_id INTEGER,
    FOREIGN KEY (member_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (checked_out_by_id) REFERENCES users(id),
    FOREIGN KEY (returned_by_id) REFERENCES users(id)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_language ON books(language);
CREATE INDEX idx_books_year ON books(publication_year);
CREATE INDEX idx_loans_member_id ON loans(member_id);
CREATE INDEX idx_loans_book_id ON loans(book_id);
