import os
import hashlib
import base64
import sqlite3
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_file
)
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet

# ==== Configuration ====
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change_this_secret_key")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === SQLite Database ===
DATABASE_PATH = "users.db"

def get_db_connection():
    """Get database connection"""
    try:
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row  # This makes rows behave like dictionaries
        return connection
    except Exception as e:
        print(f"Error connecting to SQLite: {e}")
        return None

def init_database():
    """Initialize database and create users table if it doesn't exist"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL,
                failed_attempts INTEGER DEFAULT 0,
                locked BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error creating table: {e}")
        finally:
            connection.close()

# Initialize database on startup
init_database()

# ==== Helper Functions ====
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT * FROM users WHERE username = ?"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            return dict(user) if user else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            connection.close()
    return None

def verify_user(username, password):
    user = get_user(username)
    if not user or user.get("locked", False):
        return False
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        if user["password"] == hash_password(password):
            # Reset failed attempts on successful login
            query = "UPDATE users SET failed_attempts = 0 WHERE username = ?"
            cursor.execute(query, (username,))
            connection.commit()
            return True
        else:
            # Increment failed attempts
            failed_attempts = user.get("failed_attempts", 0) + 1
            locked = failed_attempts >= 5
            query = "UPDATE users SET failed_attempts = ?, locked = ? WHERE username = ?"
            cursor.execute(query, (failed_attempts, locked, username))
            connection.commit()
            return False
    except Exception as e:
        print(f"Error verifying user: {e}")
        return False
    finally:
        connection.close()

def create_user(username, password, email):
    if get_user(username):
        return False
    
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO users (username, password, email, failed_attempts, locked) 
        VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query, (username, hash_password(password), email, 0, False))
        connection.commit()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False
    finally:
        connection.close()

def reset_password(username, new_password):
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        query = """
        UPDATE users SET password = ?, failed_attempts = 0, locked = 0 
        WHERE username = ?
        """
        cursor.execute(query, (hash_password(new_password), username))
        connection.commit()
        return True
    except Exception as e:
        print(f"Error resetting password: {e}")
        return False
    finally:
        connection.close()

# ==== File Encryption/Decryption ====
class FileEncryptor:
    @staticmethod
    def _get_key(password):
        digest = hashlib.sha256(password.encode()).digest()
        return base64.urlsafe_b64encode(digest[:32])

    @staticmethod
    def encrypt_file(filepath, password):
        key = FileEncryptor._get_key(password)
        cipher = Fernet(key)
        with open(filepath, "rb") as f:
            data = f.read()
        enc_data = cipher.encrypt(data)
        enc_path = filepath + ".enc"
        with open(enc_path, "wb") as f:
            f.write(enc_data)
        return enc_path

    @staticmethod
    def decrypt_file(filepath, password, output_path):
        key = FileEncryptor._get_key(password)
        cipher = Fernet(key)
        with open(filepath, "rb") as f:
            data = f.read()
        dec_data = cipher.decrypt(data)
        with open(output_path, "wb") as f:
            f.write(dec_data)
        return output_path

# ==== Routes ====

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("Enter both username and password", "error")
            return render_template("login.html")

        if verify_user(username, password):
            session["user"] = username
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials or account locked", "error")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        email = request.form.get("email", "").strip()

        if not username or not password or not email:
            flash("All fields are required", "error")
            return render_template("register.html")

        if create_user(username, password, email):
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        else:
            flash("Username already exists", "error")

    return render_template("register.html")

@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        new_password = request.form.get("new_password", "").strip()

        if not username or not new_password:
            flash("All fields are required", "error")
            return render_template("reset.html")

        user = get_user(username)
        if not user:
            flash("Username not found", "error")
            return render_template("reset.html")

        reset_password(username, new_password)
        flash("Password reset successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("reset.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))

    return render_template("dashboard.html", username=session["user"])

@app.route("/encrypt", methods=["POST"])
def encrypt():
    if "user" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))

    file = request.files.get("file")
    password = request.form.get("password", "").strip()

    if not file or not password:
        flash("File and password required for encryption", "error")
        return redirect(url_for("dashboard"))

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        enc_path = FileEncryptor.encrypt_file(filepath, password)
        os.remove(filepath)
        return send_file(enc_path, as_attachment=True, download_name=os.path.basename(enc_path))
    except Exception as e:
        flash(f"Encryption failed: {e}", "error")
        return redirect(url_for("dashboard"))

@app.route("/decrypt", methods=["POST"])
def decrypt():
    if "user" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))

    file = request.files.get("file")
    password = request.form.get("password", "").strip()

    if not file or not password:
        flash("File and password required for decryption", "error")
        return redirect(url_for("dashboard"))

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        output_filename = filename.replace(".enc", "") or "decrypted_file"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        FileEncryptor.decrypt_file(filepath, password, output_path)
        os.remove(filepath)
        return send_file(output_path, as_attachment=True, download_name=output_filename)
    except Exception as e:
        flash(f"Decryption failed: {e}", "error")
        os.remove(filepath)
        return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
