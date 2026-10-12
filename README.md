# Library Management System

Beginner-friendly project using HTML, CSS, Python Flask and SQLite.

## Run in VS Code

1. Open this folder in VS Code.
2. Open Terminal.
3. Create a virtual environment:
   `python -m venv venv`
4. Activate it on Windows:
   `venv\Scripts\activate`
5. Install Flask:
   `pip install -r requirements.txt`
6. Start the project:
   `python main.py`
7. Open:
   `http://127.0.0.1:5000`

## Login
Username: `admin`
Password: `admin123`

The SQLite database is created automatically inside the `database` folder.

## Main features
- Login
- Dashboard
- Add/View/Search/Edit/Delete books
- Add/View/Delete students
- Issue books
- Return books
- Automatic overdue fine: ₹2 per late day
