# Secure File Encryption Web App

A Flask web application for user registration/login and secure file encryption/decryption using MongoDB as the backend.

## Features

- User authentication with password hashing (SHA-256)
- Account lockout after 5 failed login attempts
- Password reset functionality
- Encrypt and decrypt files using Fernet symmetric encryption keyed by user's password
- MongoDB for storing user data
- Responsive UI with HTML, CSS, and JavaScript

## Getting Started

### Prerequisites

- Python 3.7+
- MongoDB (local or Atlas)
- Recommended: Virtual environment

### Installation

1. Clone this repo
git clone https://github.com/yourusername/secure-file-encryption.git
cd secure-file-encryption


2. Set up virtual environment and activate it
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate


3. Install dependencies
pip install flask pymongo cryptography


4. Configure MongoDB connection string  
Edit `app.py` or set environment variable `MONGO_URI`.  
Defaults to local MongoDB (`mongodb://localhost:27017/`).

5. Run the app
python app.py


6. Open your browser at `http://127.0.0.1:5000/`

## Usage

- Register a new account
- Log in
- Upload files to encrypt or decrypt
- Log out when finished

## Project Structure

├── app.py
├── uploads/
├── templates/
│ ├── base.html
│ ├── login.html
│ ├── register.html
│ ├── reset.html
│ └── dashboard.html
├── static/
│ ├── style.css
│ └── script.js
└── README.md


## Notes

- Uploaded files are temporarily saved in `uploads/` folder.
- Passwords are hashed for security, but consider stronger algorithms for production.
- Use environment variables for sensitive info like `SECRET_KEY` and `MONGO_URI`.

## License

MIT License
