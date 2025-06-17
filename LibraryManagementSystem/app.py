from flask import Flask, render_template, request, redirect,session
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_123'  # Replace this with a better secret in production


def get_connection():
    return sqlite3.connect('library.db')

@app.route('/')
def home():
    return render_template('index.html')  # Your HTML file

@app.route('/signup', methods=['POST'])
def signup():
    role = request.form['role']
    username = request.form['username']
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    conn = get_connection()
    cursor = conn.cursor()

    if role == 'student':
        cursor.execute("INSERT INTO students (student_id, name, email, password) VALUES (?, ?, ?, ?)",
                       (username, name, email, password))
    elif role == 'librarian':
        cursor.execute("INSERT INTO librarians (librarian_id, name, email, password) VALUES (?, ?, ?, ?)",
                       (username, name, email, password))
    elif role == 'admin':
        cursor.execute("INSERT INTO admins (username, name, email, password) VALUES (?, ?, ?, ?)",
                       (username, name, email, password))

    conn.commit()
    conn.close()
    return f"Signup successful for {role.title()} {name}!"

@app.route('/login', methods=['POST'])
def login():
    role = request.form['role']
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    if role == 'student':
        cursor.execute("SELECT * FROM students WHERE student_id=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            from datetime import datetime

            cursor.execute("SELECT book_title, issue_date, due_date, returned FROM borrowed_books WHERE student_id=?", (username,))
            records = cursor.fetchall()

            books = []
            today = datetime.now().date()

            for book in records:
                due_date = datetime.strptime(book[2], "%Y-%m-%d").date()
                days_left = (due_date - today).days
                books.append((book[0], book[1], book[2], book[3], days_left))  # 5 values now

            conn.close()
            return render_template('student_dashboard.html', user=user, books=books)

        else:
            conn.close()
            return "❌ Login failed. Wrong credentials."


    elif role == 'librarian':
        cursor.execute("SELECT * FROM librarians WHERE librarian_id=? AND password=?", (username, password))
        librarian = cursor.fetchone()
        conn.close()
        if librarian:
            session['user_id'] = librarian[0]  # librarian_id
            session['user_role'] = 'librarian'
            return redirect('/librarian')
        else:
            return "❌ Librarian login failed."

    elif role == 'admin':
        cursor.execute("SELECT * FROM admins WHERE username=? AND password=?", (username, password))
        admin = cursor.fetchone()
        conn.close()
        if admin:
            session['user_id'] = admin[0]  # username
            session['user_role'] = 'admin'
            return redirect('/admin')
        else:
            return "❌ Admin login failed."



    user = cursor.fetchone()
    conn.close()

    if user:
        return f"Login successful. Welcome, {user[1]} ({role.title()})"
    else:
        return "Login failed. Please check your credentials."
@app.route('/admin')
def admin_dashboard():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # All books
    cursor.execute("SELECT title, available_copies FROM books")
    available_books = cursor.fetchall()

    # All borrowed books
    cursor.execute("""
        SELECT borrowed_books.student_id, students.name, borrowed_books.book_title,
               borrowed_books.issue_date, borrowed_books.due_date
        FROM borrowed_books
        JOIN students ON students.student_id = borrowed_books.student_id
        WHERE returned = 0
    """)
    borrowed_books = cursor.fetchall()

    # Librarians list
    cursor.execute("SELECT librarian_id, name, email FROM librarians")
    librarians = cursor.fetchall()

    # Librarian actions
    cursor.execute("SELECT * FROM librarian_actions ORDER BY timestamp DESC")
    actions = cursor.fetchall()

    conn.close()

    return render_template(
        'admin_dashboard.html',
        available_books=available_books,
        borrowed_books=borrowed_books,
        librarians=librarians,
        actions=actions
    )

@app.route('/librarian')
def librarian_dashboard():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Get available books
    cursor.execute("SELECT title, available_copies FROM books WHERE available_copies > 0")
    available_books = cursor.fetchall()

    # Get borrowed books (not yet returned)
    cursor.execute("""
        SELECT borrowed_books.student_id, students.name, borrowed_books.book_title,
               borrowed_books.issue_date, borrowed_books.due_date
        FROM borrowed_books
        JOIN students ON students.student_id = borrowed_books.student_id
        WHERE returned = 0
    """)
    borrowed_books = cursor.fetchall()

    conn.close()
    return render_template('librarian_dashboard.html', available_books=available_books, borrowed_books=borrowed_books)

from datetime import datetime
@app.route('/update_book_stock', methods=['POST'])
def update_book_stock():
    book_title = request.form['book_title']
    new_copies = int(request.form['new_copies'])

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE books
        SET available_copies = ?
        WHERE title = ?
    ''', (new_copies, book_title))

    conn.commit()
    conn.close()

    return redirect('/admin')
@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    copies = int(request.form['copies'])

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO books (title, total_copies, available_copies)
        VALUES (?, ?, ?)
    ''', (title, copies, copies))

    conn.commit()
    conn.close()

    return redirect('/admin')
@app.route('/delete_book', methods=['POST'])
def delete_book():
    title = request.form['book_title']

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Delete book only if it's not currently borrowed (optional safety)
    cursor.execute("DELETE FROM books WHERE title = ?", (title,))

    conn.commit()
    conn.close()

    return redirect('/admin')

@app.route('/submit_book', methods=['POST'])
def submit_book():
    student_id = request.form['student_id']
    book_title = request.form['book_title']

    # ⬇️ OPTIONAL: detect who submitted (admin or librarian)
    # For now we hardcode the librarian ID, later use session
    librarian_id = session.get('user_id', 'Unknown')
  # Replace with session if login tracking is implemented

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # 1. Mark book as returned
    cursor.execute("""
        UPDATE borrowed_books
        SET returned = 1
        WHERE student_id = ? AND book_title = ? AND returned = 0
    """, (student_id, book_title))

    # 2. Increase available copies
    cursor.execute("""
        UPDATE books
        SET available_copies = available_copies + 1
        WHERE title = ?
    """, (book_title,))

    # 3. Log the librarian action
    cursor.execute("""
        INSERT INTO librarian_actions (librarian_id, action, book_title, student_id, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (librarian_id, 'Returned', book_title, student_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

    return redirect('/librarian')  # or redirect('/admin') if admin performed it

@app.route('/remove_librarian', methods=['POST'])
def remove_librarian():
    librarian_id = request.form['librarian_id']

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Optionally: Check if the librarian exists
    cursor.execute("DELETE FROM librarians WHERE librarian_id = ?", (librarian_id,))

    conn.commit()
    conn.close()

    return redirect('/admin')

@app.route('/library', methods=['POST'])
def library():
    student_id = request.form['student_id']

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    cursor.execute("SELECT title, available_copies FROM books WHERE available_copies > 0")
    available_books = cursor.fetchall()

    conn.close()
    return render_template('student_library.html', student_id=student_id, books=available_books)

from datetime import datetime, timedelta

@app.route('/borrow', methods=['POST'])
def borrow():
    student_id = request.form['student_id']
    book_title = request.form['book_title']

    issue_date = datetime.now().strftime('%Y-%m-%d')
    due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')

    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Insert into borrowed_books
    cursor.execute('''
        INSERT INTO borrowed_books (student_id, book_title, issue_date, due_date, returned)
        VALUES (?, ?, ?, ?, 0)
    ''', (student_id, book_title, issue_date, due_date))

    # Decrease availability
    cursor.execute('''
        UPDATE books
        SET available_copies = available_copies - 1
        WHERE title = ? AND available_copies > 0
    ''', (book_title,))

    conn.commit()
    conn.close()

    return redirect('/')



if __name__ == '__main__':
    app.run(debug=True)
