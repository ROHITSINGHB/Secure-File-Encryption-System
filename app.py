import os
import hashlib
import base64
import sqlite3
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, send_file
)
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet, InvalidToken

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
        connection.row_factory = sqlite3.Row
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
            # Added files_encrypted and files_decrypted columns
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL,
                failed_attempts INTEGER DEFAULT 0,
                locked BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                files_encrypted INTEGER DEFAULT 0,
                files_decrypted INTEGER DEFAULT 0
            )
            """
            cursor.execute(create_table_query)
            # Add columns if they don't exist (for existing databases)
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN files_encrypted INTEGER DEFAULT 0")
                cursor.execute("ALTER TABLE users ADD COLUMN files_decrypted INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass # Columns already exist
            connection.commit()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error creating table: {e}")
        finally:
            connection.close()

init_database()

# ==== Helper Functions ====
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username):
    connection = get_db_connection()
    if connection:
        try:
            return connection.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        finally:
            connection.close()
    return None

def verify_user(username, password):
    user = get_user(username)
    if not user or user["locked"]:
        return False
    
    connection = get_db_connection()
    if not connection: return False
    
    try:
        if user["password"] == hash_password(password):
            connection.execute("UPDATE users SET failed_attempts = 0 WHERE username = ?", (username,))
            connection.commit()
            return True
        else:
            failed_attempts = user["failed_attempts"] + 1
            locked = failed_attempts >= 5
            connection.execute("UPDATE users SET failed_attempts = ?, locked = ? WHERE username = ?", (failed_attempts, locked, username))
            connection.commit()
            return False
    finally:
        connection.close()

def create_user(username, password, email):
    if get_user(username): return False
    connection = get_db_connection()
    if not connection: return False
    try:
        connection.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", 
                           (username, hash_password(password), email))
        connection.commit()
        return True
    finally:
        connection.close()

def reset_password(username, new_password):
    connection = get_db_connection()
    if not connection: return False
    try:
        connection.execute("UPDATE users SET password = ?, failed_attempts = 0, locked = 0 WHERE username = ?", 
                           (hash_password(new_password), username))
        connection.commit()
        return True
    finally:
        connection.close()

# ==== File Encryption/Decryption ====
class FileEncryptor:
    @staticmethod
    def _get_key(password):
        return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

    @staticmethod
    def encrypt_file(filepath, password):
        cipher = Fernet(FileEncryptor._get_key(password))
        with open(filepath, "rb") as f: data = f.read()
        enc_data = cipher.encrypt(data)
        enc_path = filepath + ".enc"
        with open(enc_path, "wb") as f: f.write(enc_data)
        return enc_path

    @staticmethod
    def decrypt_file(filepath, password, output_path):
        cipher = Fernet(FileEncryptor._get_key(password))
        with open(filepath, "rb") as f: data = f.read()
        dec_data = cipher.decrypt(data)
        with open(output_path, "wb") as f: f.write(dec_data)
        return output_path

# ==== Routes ====
@app.route("/")
def index():
    return redirect(url_for("login")) if "user" not in session else redirect(url_for("dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if verify_user(username, password):
            session["user"] = username
            return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        email = request.form.get("email", "").strip()
        if create_user(username, password, email):
            return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        new_password = request.form.get("new_password", "").strip()
        if get_user(username):
            reset_password(username, new_password)
            return redirect(url_for("login"))
    return render_template("reset.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session: return redirect(url_for("login"))
    user = get_user(session["user"])
    if not user:
        session.pop("user", None)
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=user["username"], email=user["email"], 
                           files_encrypted=user["files_encrypted"], files_decrypted=user["files_decrypted"])

@app.route("/encrypt", methods=["POST"])
def encrypt():
    if "user" not in session: return jsonify({'error': 'Authentication required'}), 401
    file = request.files.get("file")
    password = request.form.get("password", "").strip()
    if not file or not password: return jsonify({'error': 'File and password are required'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        enc_path = FileEncryptor.encrypt_file(filepath, password)
        os.remove(filepath)
        # Increment encryption count
        conn = get_db_connection()
        conn.execute("UPDATE users SET files_encrypted = files_encrypted + 1 WHERE username = ?", (session["user"],))
        conn.commit()
        conn.close()
        return send_file(enc_path, as_attachment=True, download_name=os.path.basename(enc_path))
    except Exception as e:
        return jsonify({'error': f"An unexpected error occurred during encryption."}), 500

@app.route("/decrypt", methods=["POST"])
def decrypt():
    if "user" not in session: return jsonify({'error': 'Authentication required'}), 401
    file = request.files.get("file")
    password = request.form.get("password", "").strip()
    if not file or not password: return jsonify({'error': 'File and password are required'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        output_filename = filename.replace(".enc", "") if ".enc" in filename else f"decrypted_{filename}"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        FileEncryptor.decrypt_file(filepath, password, output_path)
        os.remove(filepath)
        # Increment decryption count
        conn = get_db_connection()
        conn.execute("UPDATE users SET files_decrypted = files_decrypted + 1 WHERE username = ?", (session["user"],))
        conn.commit()
        conn.close()
        return send_file(output_path, as_attachment=True, download_name=output_filename)
    except InvalidToken:
        os.remove(filepath)
        return jsonify({'error': 'Decryption failed. Please check your password or the file may be corrupted.'}), 400
    except Exception as e:
        if os.path.exists(filepath): os.remove(filepath)
        return jsonify({'error': 'An unexpected error occurred during decryption.'}), 500

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
