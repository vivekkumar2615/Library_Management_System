import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "database"

DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_FILE = DATABASE_DIR / "library.db"


def get_db():

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_db():

    db = get_db()

    db.executescript("""

    CREATE TABLE IF NOT EXISTS books (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        title TEXT NOT NULL,

        author TEXT NOT NULL,

        category TEXT,

        isbn TEXT,

        quantity INTEGER NOT NULL DEFAULT 1,

        available INTEGER NOT NULL DEFAULT 1

    );


    CREATE TABLE IF NOT EXISTS students (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT NOT NULL,

        roll_number TEXT NOT NULL UNIQUE,

        email TEXT,

        phone TEXT

    );


    CREATE TABLE IF NOT EXISTS issues (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        book_id INTEGER NOT NULL,

        student_id INTEGER NOT NULL,

        issue_date TEXT NOT NULL,

        due_date TEXT NOT NULL,

        return_date TEXT,

        status TEXT DEFAULT 'Issued',

        fine INTEGER DEFAULT 0

    );

    """)

    db.commit()

    db.close()