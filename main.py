from flask import Flask, render_template, request, redirect, url_for, session, flash

from models.db import init_db, get_db
from services.library_service import (
    get_dashboard_stats,
    get_books,
    add_book,
    update_book,
    delete_book,
    get_students,
    add_student,
    delete_student,
    get_available_books,
    get_active_issues,
    issue_book,
    return_book
)

app = Flask(
    __name__,
    template_folder="ui/templates",
    static_folder="ui/static",
    static_url_path="/static"
)

app.secret_key = "library-management-secret-key"

init_db()


def logged_in():
    return "user" in session


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":

            session["user"] = username

            return redirect(url_for("dashboard"))

        flash("Invalid username or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():

    if not logged_in():
        return redirect(url_for("login"))

    stats = get_dashboard_stats()

    return render_template(
        "dashboard.html",
        stats=stats
    )


@app.route("/books")
def books():

    if not logged_in():
        return redirect(url_for("login"))

    query = request.args.get("q", "")

    book_list = get_books(query)

    return render_template(
        "books.html",
        books=book_list,
        query=query
    )


@app.route("/books/add", methods=["GET", "POST"])
def add_book_page():

    if not logged_in():
        return redirect(url_for("login"))

    if request.method == "POST":

        quantity = int(
            request.form.get("quantity", 1)
        )

        add_book(
            request.form.get("title"),
            request.form.get("author"),
            request.form.get("category"),
            request.form.get("isbn"),
            quantity
        )

        flash("Book added successfully.")

        return redirect(url_for("books"))

    return render_template(
        "add_book.html",
        edit=False
    )


@app.route("/books/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):

    if not logged_in():
        return redirect(url_for("login"))

    db = get_db()

    book = db.execute(
        "SELECT * FROM books WHERE id=?",
        (book_id,)
    ).fetchone()

    db.close()

    if not book:
        flash("Book not found.")

        return redirect(url_for("books"))

    if request.method == "POST":

        quantity = int(
            request.form.get("quantity", 1)
        )

        update_book(
            book_id,
            request.form.get("title"),
            request.form.get("author"),
            request.form.get("category"),
            request.form.get("isbn"),
            quantity
        )

        flash("Book updated successfully.")

        return redirect(url_for("books"))

    return render_template(
        "add_book.html",
        book=book,
        edit=True
    )


@app.route("/books/delete/<int:book_id>")
def remove_book(book_id):

    if not logged_in():
        return redirect(url_for("login"))

    delete_book(book_id)

    flash("Book deleted successfully.")

    return redirect(url_for("books"))


@app.route("/students")
def students():

    if not logged_in():
        return redirect(url_for("login"))

    return render_template(
        "students.html",
        students=get_students()
    )


@app.route("/students/add", methods=["POST"])
def add_student_page():

    if not logged_in():
        return redirect(url_for("login"))

    name = request.form.get("name")
    roll_number = request.form.get("roll_number")
    email = request.form.get("email")
    phone = request.form.get("phone")

    result = add_student(
        name,
        roll_number,
        email,
        phone
    )

    if result:
        flash("Student added successfully.")
    else:
        flash("Roll number already exists.")

    return redirect(url_for("students"))


@app.route("/students/delete/<int:student_id>")
def remove_student(student_id):

    if not logged_in():
        return redirect(url_for("login"))

    delete_student(student_id)

    flash("Student deleted successfully.")

    return redirect(url_for("students"))


@app.route("/issue", methods=["GET", "POST"])
def issue():

    if not logged_in():
        return redirect(url_for("login"))

    if request.method == "POST":

        book_id = int(request.form["book_id"])
        student_id = int(request.form["student_id"])

        success, message = issue_book(
            book_id,
            student_id
        )

        flash(message)

        return redirect(url_for("issue"))

    return render_template(
        "issue_book.html",
        books=get_available_books(),
        students=get_students(),
        issues=get_active_issues()
    )


@app.route("/return/<int:issue_id>")
def return_issue(issue_id):

    if not logged_in():
        return redirect(url_for("login"))

    success, fine = return_book(issue_id)

    if success:

        flash(
            f"Book returned successfully. Fine: ₹{fine}"
        )

    else:

        flash("Book return failed.")

    return redirect(url_for("issue"))


if __name__ == "__main__":

    app.run(debug=True)