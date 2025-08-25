import os
import hashlib
import base64
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_file
)
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet

# ==== Configuration ====
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change_this_secret_key")  # Use env var in production
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === MongoDB connection ===
# Set your MongoDB URI here; example for local MongoDB:
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.security_db               # Database name
users_col = db.users                  # Collection name

# ==== Helper Functions ====
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username):
    return users_col.find_one({"username": username})

def verify_user(username, password):
    user = get_user(username)
    if not user or user.get("locked", False):
        return False
    if user["password"] == hash_password(password):
        users_col.update_one({"username": username}, {"$set": {"failed_attempts": 0}})
        return True
    else:
        failed_attempts = user.get("failed_attempts", 0) + 1
        update_data = {"failed_attempts": failed_attempts}
        if failed_attempts >= 5:
            update_data["locked"] = True
        users_col.update_one({"username": username}, {"$set": update_data})
        return False

def create_user(username, password, email):
    if get_user(username):
        return False
    user_doc = {
        "username": username,
        "password": hash_password(password),
        "email": email,
        "failed_attempts": 0,
        "locked": False
    }
    users_col.insert_one(user_doc)
    return True

def reset_password(username, new_password):
    users_col.update_one({"username": username}, {
        "$set": {
            "password": hash_password(new_password),
            "failed_attempts": 0,
            "locked": False
        }
    })

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
    app.run(debug=True)
