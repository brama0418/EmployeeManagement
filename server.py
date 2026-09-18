from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "employee-management-secret"


# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    conn = sqlite3.connect("users.db")
    return conn


# ---------------- CREATE TABLES ----------------

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS employee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employeename TEXT NOT NULL,
    email TEXT NOT NULL,
    phonenumber TEXT NOT NULL,
    department TEXT NOT NULL,
    salary TEXT NOT NULL,
    joiningdate TEXT NOT NULL,
    address TEXT NOT NULL
)
""")

conn.commit()
conn.close()


# ---------------- HOME ----------------

@app.route("/")
def home():

    if "username" not in session:
        return redirect("/login")

    return render_template("navbar.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO users
                (fullname, username, password)
                VALUES (?, ?, ?)
            """, (
                fullname,
                username,
                password
            ))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            return "Username already exists"

        conn.close()

        return redirect("/login")

    return render_template("register demo.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM users
            WHERE username = ?
            AND password = ?
        """, (
            username,
            password
        ))

        user = cursor.fetchone()

        conn.close()

        if user:

            session["username"] = username

            return redirect("/")

        return "Invalid username or password"

    return render_template("login.html")


# ---------------- ADD EMPLOYEE ----------------

@app.route("/add-employee", methods=["GET", "POST"])
def add_employee():

    if request.method == "POST":

        employeename = request.form["name"]
        email = request.form["email"]
        phonenumber = request.form["phone"]
        department = request.form["department"]
        salary = request.form["salary"]
        joiningdate = request.form["joining_date"]
        address = request.form["address"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO employee
            (
                employeename,
                email,
                phonenumber,
                department,
                salary,
                joiningdate,
                address
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            employeename,
            email,
            phonenumber,
            department,
            salary,
            joiningdate,
            address
        ))

        conn.commit()
        conn.close()

        return redirect("/employee")

    return render_template("add-employee.html")


# ---------------- EMPLOYEE DETAILS ----------------

@app.route("/employee")
def employee():

    if "username" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM employee
    """)

    employees = cursor.fetchall()

    conn.close()

    return render_template(
        "employee.html",
        employees=employees
    )


# ---------------- SEARCH EMPLOYEE ----------------

@app.route("/search", methods=["GET", "POST"])
def search_employee():

    if "username" not in session:
        return redirect("/login")

    employees = []
    search_name = ""

    if request.method == "POST":

        search_name = request.form["name"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                employeename,
                email,
                department,
                phonenumber
            FROM employee
            WHERE employeename LIKE ?
        """, (
            "%" + search_name + "%",
        ))

        employees = cursor.fetchall()

        conn.close()

    return render_template(
        "Search.html",
        employees=employees,
        search_name=search_name
    )


# ---------------- EDIT EMPLOYEE ----------------

@app.route("/edit-employee/<int:id>", methods=["GET", "POST"])
def edit_employee(id):

    if "username" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        employeename = request.form["name"]
        email = request.form["email"]
        phonenumber = request.form["phone"]
        department = request.form["department"]
        salary = request.form["salary"]
        joiningdate = request.form["joining_date"]
        address = request.form["address"]

        cursor.execute("""
            UPDATE employee
            SET employeename = ?,
                email = ?,
                phonenumber = ?,
                department = ?,
                salary = ?,
                joiningdate = ?,
                address = ?
            WHERE id = ?
        """, (
            employeename,
            email,
            phonenumber,
            department,
            salary,
            joiningdate,
            address,
            id
        ))

        conn.commit()
        conn.close()

        return redirect("/employee")

    cursor.execute("""
        SELECT *
        FROM employee
        WHERE id = ?
    """, (id,))

    employee = cursor.fetchone()

    conn.close()

    return render_template(
        "edit-employee.html",
        employee=employee
    )
# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ---------------- DELETE EMPLOYEE ----------------

@app.route("/delete-employee/<int:id>")
def delete_employee(id):

    if "username" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM employee
        WHERE id = ?
    """, (id,))

    conn.commit()
    conn.close()

    return redirect("/employee")


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)