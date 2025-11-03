# Secure File Encryption Web App

A Flask web application for user registration/login and secure file encryption/decryption using SQLite as the backend database.

## 🌐 Live Demo
**Deployed on Railway**: [https://secure-file-encryption-system-production.up.railway.app](https://secure-file-encryption-system-production.up.railway.app)

## ✨ Features

* **User Authentication** with password hashing (SHA-256)
* **Account Security**: Lockout after 5 failed login attempts
* **Password Reset** functionality
* **File Encryption/Decryption** using Fernet symmetric encryption
* **SQLite Database** for lightweight, reliable data storage
* **Responsive UI** with clean HTML templates
* **Session Management** with Flask sessions
* **Secure File Handling** with automatic cleanup

## 🚀 Getting Started

### Prerequisites
* Python 3.7+
* Git
* Virtual environment (recommended)

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/secure-file-encryption.git
   cd secure-file-encryption
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables** (optional for local testing)
   ```bash
   export SECRET_KEY="your_secret_key_here"  # Windows: set SECRET_KEY=your_secret_key_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://127.0.0.1:5000/`

## 📁 Project Structure

```
secure-file-encryption/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Railway deployment configuration
├── users.db              # SQLite database (created automatically)
├── uploads/              # Temporary file storage (auto-created)
├── templates/            # HTML templates
│   ├── login.html
│   ├── register.html
│   ├── reset.html
│   └── dashboard.html
├── static/               # CSS and JS files
│   ├── style.css
│   └── script.js
└── README.md
```

## 💻 Usage

1. **Register**: Create a new account with username, email, and password
2. **Login**: Sign in with your credentials
3. **Encrypt Files**: 
   - Upload any file
   - Enter an encryption password
   - Download the encrypted `.enc` file
4. **Decrypt Files**: 
   - Upload an `.enc` file
   - Enter the correct decryption password
   - Download the original file
5. **Security**: Account locks after 5 failed login attempts
6. **Password Reset**: Reset your password if needed

## 🔧 Technologies Used

* **Backend**: Flask (Python)
* **Database**: SQLite
* **Encryption**: Cryptography (Fernet)
* **Frontend**: HTML5, CSS3, JavaScript
* **Deployment**: Railway
* **Server**: Gunicorn

## 🚀 Deployment

### Deploy to Railway

1. **Fork this repository**
2. **Connect to Railway**:
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your forked repository
3. **Set environment variables**:
   - Add `SECRET_KEY` with a secure random string
4. **Deploy**: Railway automatically deploys your app!

### Deploy to Other Platforms

The app is also compatible with:
- Heroku
- Render
- Vercel
- Any platform supporting Python/Flask

## 🔐 Security Features

* **Password Hashing**: SHA-256 hashing for stored passwords
* **Account Lockout**: Automatic lockout after 5 failed attempts
* **Session Security**: Flask session management
* **File Encryption**: Military-grade Fernet encryption
* **Temporary Files**: Automatic cleanup of uploaded files
* **Input Validation**: Secure filename handling

## 📋 Requirements

```
blinker==1.9.0
cffi==1.17.1
click==8.2.1
colorama==0.4.6
cryptography==45.0.6
dnspython==2.7.0
Flask==3.1.2
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.2
pycparser==2.22
Werkzeug==3.1.3
gunicorn==23.0.0
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret key | `change_this_secret_key` |
| `PORT` | Server port (Railway sets this automatically) | `5000` |

### Local Development

For local development, create a `.env` file:
```
SECRET_KEY=your_very_secure_secret_key_here
```

## 🐛 Troubleshooting

### Common Issues

1. **Database not found**: SQLite database is created automatically
2. **Encryption fails**: Check if password contains special characters
3. **Upload fails**: Ensure file size is within limits
4. **Account locked**: Wait or use password reset functionality

### Logs

Check application logs for detailed error information:
```bash
# Local development
python app.py

# Railway deployment
Check logs in Railway dashboard
```

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section
2. Review the logs
3. Open an issue on GitHub

## 🎯 Future Enhancements

- [ ] Multiple file encryption at once
- [ ] User file history
- [ ] Advanced encryption algorithms
- [ ] File sharing capabilities
- [ ] API endpoints
- [ ] Mobile app version

---

## Deployment with Jenkins ✅
