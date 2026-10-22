import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "complaints.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'admin'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_username TEXT NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Default admin account: username=admin, password=admin123
    cur.execute("SELECT * FROM users WHERE username = 'admin'")
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", hash_password("admin123"), "admin"),
        )

    conn.commit()
    conn.close()


def create_user(username, password, role="student"):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role),
        )
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()


def verify_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()
    if user and user["password"] == hash_password(password):
        return dict(user)
    return None


def add_complaint(student_username, title, category, description):
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        """INSERT INTO complaints
           (student_username, title, category, description, status, created_at, updated_at)
           VALUES (?, ?, ?, ?, 'Pending', ?, ?)""",
        (student_username, title, category, description, now, now),
    )
    conn.commit()
    conn.close()


def get_complaints_by_student(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM complaints WHERE student_username = ? ORDER BY created_at DESC",
        (username,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_complaints(status_filter=None):
    conn = get_connection()
    cur = conn.cursor()
    if status_filter and status_filter != "All":
        cur.execute(
            "SELECT * FROM complaints WHERE status = ? ORDER BY created_at DESC",
            (status_filter,),
        )
    else:
        cur.execute("SELECT * FROM complaints ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_status(complaint_id, new_status):
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        "UPDATE complaints SET status = ?, updated_at = ? WHERE id = ?",
        (new_status, now, complaint_id),
    )
    conn.commit()
    conn.close()
