from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = "your_secret_key"  # needed for sessions & flash

# Hardcoded admin credentials (can later move to DB)
ADMIN_USER = "admin"
ADMIN_PASS = "password123"


# --- Database Setup ---
def init_db():
    conn = sqlite3.connect("activity.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            pinno TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            activity TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()


@app.route("/", methods=["GET", "POST"])
def hiii():

    return render_template("index.html")


# --- Home + Form ---
@app.route("/form", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        pinno = request.form.get("pinno")
        email = request.form.get("email")
        phone = request.form.get("phone")
        activity = request.form.get("activites")

        conn = sqlite3.connect("activity.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO registrations (name, pinno, email, phone, activity) VALUES (?, ?, ?, ?, ?)",
            (name, pinno, email, phone, activity)
        )
        conn.commit()
        conn.close()

        flash("Your activity registration was successful!", "success")
        return redirect(url_for("index"))

    return render_template("form.html")


# --- Login Page ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("registrations"))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


# --- Logout ---
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))


# --- Registrations Table (Protected) ---
@app.route("/registrations")
def registrations():
    if "user" not in session:  # check login
        flash("Please login to view registrations.", "warning")
        return redirect(url_for("login"))

    conn = sqlite3.connect("activity.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registrations")
    rows = cursor.fetchall()
    conn.close()
    return render_template("registrations.html", rows=rows)


# --- Download Excel (Protected) ---
@app.route("/download_excel")
def download_excel():
    if "user" not in session:
        flash("Please login to download data.", "warning")
        return redirect(url_for("login"))

    conn = sqlite3.connect("activity.db")
    df = pd.read_sql_query("SELECT * FROM registrations", conn)
    conn.close()

    file_path = "registrations.xlsx"
    df.to_excel(file_path, index=False, engine="openpyxl")

    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
