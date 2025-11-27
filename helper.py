
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def get_data():
    """
    This function returns a sample dictionary.
    """
    return {"message": "Hello from the backend!"}

def create_user(username, password, email, full_name, role):
    """Creates a new user in the database."""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, email, full_name, role) VALUES (?, ?, ?, ?, ?)",
                  (username, generate_password_hash(password), email, full_name, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_username(username):
    """Retrieves a user from the database by username."""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user:
        return {'id': user[0], 'username': user[1], 'email': user[3], 'full_name': user[4], 'role': user[5]}
    return None

def verify_user(username, password):
    """Verifies a user's credentials."""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    stored_password = c.fetchone()
    conn.close()
    if stored_password and check_password_hash(stored_password[0], password):
        return True
    return False

def update_user(username, email, full_name, role):
    """Updates a user's information."""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE users SET email = ?, full_name = ?, role = ? WHERE username = ?",
              (email, full_name, role, username))
    conn.commit()
    conn.close()

def delete_user(username):
    """Deletes a user from the database."""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
