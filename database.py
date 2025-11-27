
import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    """Initializes the database and creates the users table."""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    # Check if the default admin user exists
    c.execute("SELECT * FROM users WHERE username = ?", ('admin',))
    if c.fetchone() is None:
        # Create a default admin user
        c.execute("INSERT INTO users (username, password, email, full_name, role) VALUES (?, ?, ?, ?, ?)",
                  ('admin', generate_password_hash('admin'), 'admin@example.com', 'Admin User', 'admin'))
    conn.commit()
    conn.close()
