import sqlite3
from datetime import date, timedelta

from models.db import get_db


def get_dashboard_stats():

    db = get_db()

    stats = {

        "books": db.execute(
            "SELECT COUNT(*) FROM books"
        ).fetchone()[0],

        "copies": db.execute(
            "SELECT COALESCE(SUM(quantity),0) FROM books"
        ).fetchone()[0],

        "available": db.execute(
            "SELECT COALESCE(SUM(available),0) FROM books"
        ).fetchone()[0],

        "students": db.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0],

        "issued": db.execute(
            "SELECT COUNT(*) FROM issues WHERE status='Issued'"
        ).fetchone()[0]

    }

    db.close()

    return stats


def get_books(query=""):

    db = get_db()

    if query:

        search = f"%{query}%"

        books = db.execute(
            """
            SELECT * FROM books
            WHERE title LIKE ?
            OR author LIKE ?
            OR category LIKE ?
            OR isbn LIKE ?
            ORDER BY id DESC
            """,
            (
                search,
                search,
                search,
                search
            )
        ).fetchall()

    else:

        books = db.execute(
            """
            SELECT * FROM books
            ORDER BY id DESC
            """
        ).fetchall()

    db.close()

    return books


def add_book(
    title,
    author,
    category,
    isbn,
    quantity
):

    db = get_db()

    db.execute(
        """
        INSERT INTO books
        (title, author, category, isbn, quantity, available)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            author,
            category,
            isbn,
            quantity,
            quantity
        )
    )

    db.commit()

    db.close()


def update_book(
    book_id,
    title,
    author,
    category,
    isbn,
    quantity
):

    db = get_db()

    old = db.execute(
        """
        SELECT quantity, available
        FROM books
        WHERE id=?
        """,
        (book_id,)
    ).fetchone()

    if old:

        issued_copies = (
            old["quantity"] -
            old["available"]
        )

        available = max(
            0,
            quantity - issued_copies
        )

        db.execute(
            """
            UPDATE books

            SET title=?,
                author=?,
                category=?,
                isbn=?,
                quantity=?,
                available=?

            WHERE id=?
            """,
            (
                title,
                author,
                category,
                isbn,
                quantity,
                available,
                book_id
            )
        )

        db.commit()

    db.close()


def delete_book(book_id):

    db = get_db()

    active = db.execute(
        """
        SELECT COUNT(*)
        FROM issues
        WHERE book_id=?
        AND status='Issued'
        """,
        (book_id,)
    ).fetchone()[0]

    if active == 0:

        db.execute(
            "DELETE FROM books WHERE id=?",
            (book_id,)
        )

        db.commit()

    db.close()


def get_students():

    db = get_db()

    students = db.execute(
        """
        SELECT *
        FROM students
        ORDER BY id DESC
        """
    ).fetchall()

    db.close()

    return students


def add_student(
    name,
    roll_number,
    email,
    phone
):

    db = get_db()

    try:

        db.execute(
            """
            INSERT INTO students
            (name, roll_number, email, phone)
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                roll_number,
                email,
                phone
            )
        )

        db.commit()

        result = True

    except sqlite3.IntegrityError:

        result = False

    db.close()

    return result


def delete_student(student_id):

    db = get_db()

    db.execute(
        "DELETE FROM students WHERE id=?",
        (student_id,)
    )

    db.commit()

    db.close()


def get_available_books():

    db = get_db()

    books = db.execute(
        """
        SELECT *
        FROM books
        WHERE available > 0
        ORDER BY title
        """
    ).fetchall()

    db.close()

    return books


def get_active_issues():

    db = get_db()

    issues = db.execute(
        """
        SELECT
            issues.*,
            books.title AS book_title,
            students.name AS student_name

        FROM issues

        JOIN books
        ON books.id = issues.book_id

        JOIN students
        ON students.id = issues.student_id

        WHERE issues.status='Issued'

        ORDER BY issues.id DESC
        """
    ).fetchall()

    db.close()

    return issues


def issue_book(
    book_id,
    student_id
):

    db = get_db()

    book = db.execute(
        """
        SELECT available
        FROM books
        WHERE id=?
        """,
        (book_id,)
    ).fetchone()

    if not book:

        db.close()

        return False, "Book not found."

    if book["available"] <= 0:

        db.close()

        return False, "Book is not available."

    today = date.today()

    due_date = (
        today +
        timedelta(days=14)
    )

    db.execute(
        """
        UPDATE books
        SET available=available-1
        WHERE id=?
        """,
        (book_id,)
    )

    db.execute(
        """
        INSERT INTO issues
        (
            book_id,
            student_id,
            issue_date,
            due_date
        )

        VALUES (?, ?, ?, ?)
        """,
        (
            book_id,
            student_id,
            today.isoformat(),
            due_date.isoformat()
        )
    )

    db.commit()

    db.close()

    return True, "Book issued successfully."


def return_book(issue_id):

    db = get_db()

    issue = db.execute(
        """
        SELECT *
        FROM issues
        WHERE id=?
        AND status='Issued'
        """,
        (issue_id,)
    ).fetchone()

    if not issue:

        db.close()

        return False, 0

    today = date.today()

    due_date = date.fromisoformat(
        issue["due_date"]
    )

    late_days = max(
        0,
        (today - due_date).days
    )

    fine = late_days * 2

    db.execute(
        """
        UPDATE issues

        SET return_date=?,
            status='Returned',
            fine=?

        WHERE id=?
        """,
        (
            today.isoformat(),
            fine,
            issue_id
        )
    )

    db.execute(
        """
        UPDATE books
        SET available=available+1
        WHERE id=?
        """,
        (issue["book_id"],)
    )

    db.commit()

    db.close()

    return True, fine