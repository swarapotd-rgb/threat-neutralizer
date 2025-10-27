# 🛡️ Threat Neutralizer

[![Hackathon](https://img.shields.io/badge/Hackathon-Top%2010-gold?style=for-the-badge)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://python.org)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)

> A secure intelligence management system with enterprise-grade authentication and role-based access control. **Top 10 Finalist** in a competitive 30-hour hackathon 🏆

![Threat Neutralizer](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square)
![Security](https://img.shields.io/badge/Security-MFA%20Enabled-red?style=flat-square)
![Build Time](https://img.shields.io/badge/Built%20In-30%20Hours-orange?style=flat-square)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Authentication](#-authentication)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Security Features](#-security-features)
- [Screenshots](#-screenshots)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Threat Neutralizer** is a full-stack web application designed for secure management of classified information, personnel records, and operational data. Built with security-first principles during an intense 30-hour hackathon, it demonstrates production-ready implementation of:

- 🔐 Multi-Factor Authentication (JWT + TOTP)
- 👥 Role-Based Access Control (RBAC)
- 📝 Comprehensive Audit Logging
- 🚦 Advanced Rate Limiting
- 🔒 Secure File Management

### 🏆 Hackathon Achievement
- **Ranking**: Top 10 out of numerous competing teams
- **Time Constraint**: 30 hours from concept to deployment
- **Focus**: Security-first architecture with real-world applicability

---

## ✨ Features

### 🔐 Security & Authentication
- **Multi-Factor Authentication**: JWT tokens combined with TOTP (Time-based One-Time Password)
- **Role-Based Access Control**: Granular permissions for Admin, File Manager, and custom roles
- **Rate Limiting**: 
  - 100 requests per 15 minutes per IP
  - 50 failed login attempts protection
- **Password Security**: bcrypt hashing with salt
- **Token Validation**: Database-backed JWT verification
- **Audit Trail**: Comprehensive logging of all user actions
- **Account Protection**: Automatic lockout after failed attempts

### 📁 Core Modules

#### Classified Files Management
- Secure document upload and storage
- Role-based download permissions
- Binary file support with streaming responses
- Access level enforcement (Admin vs File Manager)

#### Personnel (Agents) Management
- Agent profile tracking
- Clearance level monitoring
- Mission history
- Status tracking (Active, Inactive, MIA, etc.)

#### Secured Locations
- Geographic intelligence database
- Access level controls
- Security classification tracking
- Location status monitoring

#### Operations Tracking
- Mission planning and execution logs
- Priority-based classification
- Timeline management
- Resource allocation tracking

#### Admin Dashboard
- System-wide monitoring
- Comprehensive audit log analysis
- User activity tracking
- Security event monitoring
- Filterable logs by user, role, and time range

### 🎨 User Experience
- 🎨 Modern, responsive UI with TailwindCSS
- ⚡ Real-time data updates
- 📱 Mobile-responsive design
- 🚀 Fast page loads with Vite
- 🎯 Intuitive navigation

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance Python web framework |
| **SQLite** | Embedded database with secure connection handling |
| **PyJWT** | JSON Web Token implementation |
| **PyOTP** | TOTP (Time-based OTP) implementation |
| **bcrypt** | Password hashing |
| **Pydantic** | Data validation and settings management |
| **Uvicorn** | ASGI server for FastAPI |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 18.2** | UI library with hooks |
| **Vite** | Next-generation frontend tooling |
| **TailwindCSS** | Utility-first CSS framework |
| **React Router DOM** | Client-side routing |
| **js-cookie** | Cookie management |
| **qrcode.react** | QR code generation for TOTP setup |

### Security
- 🔒 CORS middleware for cross-origin protection
- 🛡️ Rate limiting middleware
- 🔐 Token-based authentication
- 📊 Audit logging middleware
- 🚫 SQL injection prevention via parameterized queries

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.10 or higher
Node.js 16 or higher
npm or yarn package manager
```

### Installation

#### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/threat-neutralizer.git
cd threat-neutralizer/mvp-final
```

#### 2️⃣ Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install fastapi uvicorn sqlalchemy pydantic pyotp pyjwt bcrypt python-multipart

# Start the backend server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will automatically:
- Initialize the SQLite database
- Create default admin and user accounts
- Display TOTP secrets in the console

#### 3️⃣ Frontend Setup
```bash
# Open a new terminal and navigate to frontend directory
cd mvp-final

# Install dependencies
npm install

# Start the development server
npm run dev
```

#### 4️⃣ Access the Application
- 🌐 **Frontend**: http://localhost:5173
- 📚 **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- 🔌 **API Base URL**: http://localhost:8000

---

## 🔑 Authentication

### Default Test Accounts

#### 👨‍💼 Admin Account
```
Username: admin
Password: admin123
TOTP Secret: JBSWY3DPEHPK3PXP
```

#### 👤 File Manager Account
```
Username: user
Password: user123
TOTP Secret: JBSWY3DPEHPK3PXQ
```

### Generate TOTP Codes

#### Option 1: Quick Python Script
```bash
cd backend
python get_totp.py
```

Output:
```
==================================================
  THREAT NEUTRALIZER - TOTP CODES
==================================================

[ADMIN] Account: admin / Password: admin123
        TOTP Code: 123456

[USER]  Account: user / Password: user123
        TOTP Code: 654321

[TIME]  Valid for: 25 seconds
==================================================
```

#### Option 2: Authenticator App (Recommended)
Use any TOTP-compatible authenticator app:
- 📱 Google Authenticator (iOS/Android)
- 🔐 Microsoft Authenticator (iOS/Android)
- 🛡️ Authy (iOS/Android/Desktop)

**Setup Steps:**
1. Open your authenticator app
2. Select "Add account" → "Enter key manually"
3. Enter account name: `Threat Neutralizer - Admin`
4. Enter the TOTP secret: `JBSWY3DPEHPK3PXP`
5. Select time-based
6. Your app will now generate codes automatically every 30 seconds

---

## 📖 API Documentation

### Authentication Flow

#### POST `/login`
Authenticate user with credentials and TOTP code.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123",
  "totp_code": "123456"
}
```

**Response (Success - 200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "role": "admin",
  "username": "admin"
}
```

**Response (Error - 401):**
```json
{
  "detail": "Invalid credentials"
}
```

### Protected Endpoints

All protected endpoints require JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

#### 📁 File Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/files` | List all accessible files | Authenticated |
| GET | `/files/{file_id}` | Download specific file | Role-based |

#### 👥 Agent Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/agents` | List all agents | Authenticated |
| GET | `/agents/{agent_id}` | Get agent details | Authenticated |

#### 📍 Location Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/locations` | List all locations | Authenticated |
| GET | `/locations/{location_id}` | Get location details | Authenticated |

#### 🎯 Operation Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/operations` | List all operations | Authenticated |
| GET | `/operations/{operation_id}` | Get operation details | Role-filtered |

#### 📊 Admin Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/logs` | Get audit logs | Admin only |

**Query Parameters for `/logs`:**
- `username`: Filter by username
- `role`: Filter by role
- `start_time`: Filter by start timestamp
- `end_time`: Filter by end timestamp
- `limit`: Maximum number of records (default: 100)

### Interactive API Testing

Visit **http://localhost:8000/docs** for the interactive Swagger UI where you can:
- 📝 View all endpoints
- 🧪 Test API calls directly
- 📖 See request/response schemas
- 🔐 Authenticate and use protected endpoints

---

## 🏗️ Project Structure

```
threat-neutralizer/mvp-final/
├── backend/
│   ├── main.py                 # FastAPI app & route definitions
│   ├── database.py             # Database models & CRUD operations
│   ├── auth.py                 # Authentication utilities
│   ├── authenticator.py        # TOTP verification logic
│   ├── middleware.py           # Custom middleware
│   ├── log_middleware.py       # Audit logging middleware
│   ├── get_totp.py            # TOTP code generator utility
│   ├── secure.db              # SQLite database file
│   ├── classified_files/      # Secure file storage
│   │   ├── DOC001.txt
│   │   ├── DOC002.txt
│   │   └── ...
│   └── requirements.txt       # Python dependencies
│
├── src/
│   ├── pages/
│   │   ├── LoginPage.jsx      # Login & 2FA interface
│   │   ├── HomePage.jsx       # Dashboard & file management
│   │   ├── AgentsPage.jsx     # Agent listing
│   │   ├── AgentDetailPage.jsx # Individual agent details
│   │   ├── LocationsPage.jsx  # Location management
│   │   └── OperationsPage.jsx # Operations tracking
│   ├── utils/
│   │   └── api.js             # API client utilities
│   ├── App.jsx                # Main React component & routing
│   ├── App.css                # Global styles
│   ├── main.jsx               # React entry point
│   └── index.css              # Tailwind directives
│
├── public/
│   └── vite.svg               # App icon
│
├── package.json               # Node.js dependencies
├── vite.config.js            # Vite configuration
├── tailwind.config.js        # Tailwind CSS configuration
├── postcss.config.js         # PostCSS configuration
└── README.md                 # This file
```

---

## 🔒 Security Features

### Multi-Layer Security Architecture

```
┌─────────────────────────────────────────┐
│         User Authentication             │
│  (Username + Password + TOTP Code)      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        Rate Limiting Check              │
│   (100 req/15min, 50 login fails)       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Token Generation & Storage         │
│      (JWT with DB validation)           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    Role-Based Access Control (RBAC)     │
│      (Resource-level permissions)       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        Audit Log Recording              │
│    (All actions logged with metadata)   │
└─────────────────────────────────────────┘
```

### Access Control Matrix

| Resource | Admin | File Manager | Guest |
|----------|-------|--------------|-------|
| All classified files | ✅ Full Access | ❌ Denied | ❌ Denied |
| Assigned files | ✅ Yes | ✅ Yes | ❌ No |
| Agent profiles | ✅ Full Details | ✅ Basic Info | ❌ No |
| Location data | ✅ All Locations | ✅ Assigned Only | ❌ No |
| Operations | ✅ All Operations | ⚠️ Non-TOP_SECRET | ❌ No |
| Audit logs | ✅ Full Access | ❌ Denied | ❌ Denied |
| User management | ✅ Yes | ❌ No | ❌ No |

### Security Best Practices Implemented

✅ **Password Security**
- bcrypt hashing with automatic salt
- No plaintext password storage
- Secure password comparison

✅ **Token Management**
- JWT tokens with expiration (1 hour)
- Database-backed token validation
- Automatic token cleanup
- Signature verification

✅ **Rate Limiting**
- IP-based request throttling
- Automatic cleanup of old entries
- Separate limits for login attempts
- 429 status code on limit exceeded

✅ **SQL Injection Prevention**
- Parameterized queries throughout
- No string concatenation for SQL
- ORM-style database interactions

✅ **Audit Trail**
- All sensitive actions logged
- Immutable log records
- Timestamp, user, role, and action details
- Failed attempt tracking

✅ **CORS Protection**
- Configured origins
- Credential support
- Method restrictions

---

## 📸 Screenshots

### Login Page with 2FA
![Login Page](https://via.placeholder.com/800x500?text=Login+Page+Screenshot)
*Multi-factor authentication with TOTP support*

### Dashboard
![Dashboard](https://via.placeholder.com/800x500?text=Dashboard+Screenshot)
*Classified files management interface*

### Agent Management
![Agents](https://via.placeholder.com/800x500?text=Agent+Management+Screenshot)
*Personnel tracking with clearance levels*

### Operations Center
![Operations](https://via.placeholder.com/800x500?text=Operations+Screenshot)
*Mission planning and execution tracking*

---

## 🧪 Testing

### Manual Testing

#### 1. Test Login Flow
```bash
# Generate TOTP code
python backend/get_totp.py

# Login via UI at http://localhost:5173
# Enter credentials and the generated code
```

#### 2. Test API with cURL
```bash
# Login
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123",
    "totp_code": "123456"
  }'

# Get files (replace TOKEN with actual JWT)
curl -X GET "http://localhost:8000/files" \
  -H "Authorization: Bearer TOKEN"

# Get audit logs (admin only)
curl -X GET "http://localhost:8000/logs?limit=50" \
  -H "Authorization: Bearer TOKEN"
```

#### 3. Test Rate Limiting
```bash
# Run this script to test rate limiting
for i in {1..101}; do
  curl -X GET "http://localhost:8000/files" \
    -H "Authorization: Bearer TOKEN" &
done
# Should receive 429 Too Many Requests after 100 attempts
```

### Automated Testing (Future Enhancement)
- Unit tests for database operations
- Integration tests for API endpoints
- Security testing with OWASP ZAP
- Load testing with Locust

---

## 🚀 Deployment

### Production Considerations

#### Backend Deployment
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend Deployment
```bash
# Build for production
npm run build

# Serve with any static file server
# Output will be in the 'dist' directory
```

### Environment Variables (Production)
```bash
# .env file (DO NOT commit this file)
SECRET_KEY=your-super-secure-secret-key-here
DATABASE_URL=postgresql://user:pass@host/db  # For PostgreSQL migration
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_MINUTES=15
```

### Recommended Production Stack
- **Hosting**: AWS, DigitalOcean, or Heroku
- **Database**: PostgreSQL (migrate from SQLite)
- **Frontend**: Netlify, Vercel, or CloudFlare Pages
- **API Server**: Docker container with Nginx reverse proxy
- **SSL**: Let's Encrypt or CloudFlare SSL
- **Monitoring**: Sentry for error tracking, DataDog for metrics

---

## 🎓 Lessons Learned

### What Went Well ✅
- Security-first approach paid off with robust authentication
- FastAPI's auto-documentation saved hours of manual API documentation
- Modular architecture enabled parallel team development
- TailwindCSS accelerated UI development significantly
- TOTP integration added real security value with minimal complexity

### Challenges Overcome 💪
- Implementing proper RBAC within time constraints
- Balancing security with user experience
- Database schema design iterations
- TOTP clock synchronization edge cases
- Rate limiting implementation without external services

### What We'd Do Differently 🔄
- Start with PostgreSQL instead of SQLite
- Implement WebSockets for real-time updates
- Add comprehensive test suite from the beginning
- Create a Docker Compose setup for easier deployment
- Implement file encryption at rest

---

## 🔮 Future Enhancements

### Planned Features
- [ ] PostgreSQL migration for production scalability
- [ ] Real-time notifications via WebSockets
- [ ] File encryption at rest (AES-256)
- [ ] User management dashboard for admins
- [ ] Advanced search and filtering
- [ ] Export audit logs to CSV/PDF
- [ ] Mobile application (React Native)
- [ ] SSO integration (OAuth 2.0)
- [ ] Two-person rule for sensitive operations
- [ ] Automated security scanning
- [ ] Kubernetes deployment configuration
- [ ] GraphQL API alternative
- [ ] Advanced analytics dashboard
- [ ] Email notifications for security events
- [ ] Biometric authentication support

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Workflow
```bash
# 1. Fork the repository
# 2. Create your feature branch
git checkout -b feature/AmazingFeature

# 3. Commit your changes
git commit -m 'Add some AmazingFeature'

# 4. Push to the branch
git push origin feature/AmazingFeature

# 5. Open a Pull Request
```

### Coding Standards
- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript/React
- Write meaningful commit messages
- Add comments for complex logic
- Update documentation for API changes

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

Built with ❤️ by:
- **Your Name** - Full Stack Development - [LinkedIn](https://linkedin.com/in/yourprofile) | [GitHub](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Hackathon organizers for the incredible opportunity
- FastAPI team for the amazing framework
- React community for excellent documentation
- Our mentors and judges for valuable feedback
- Coffee ☕ for keeping us awake during the 30-hour sprint

---

## 📬 Contact & Links

- **📧 Email**: your.email@example.com
- **🔗 Project Link**: [GitHub Repository](https://github.com/yourusername/threat-neutralizer)
- **🎥 Demo Video**: [YouTube Link](https://youtube.com)
- **📊 Live Demo**: [Demo Site](https://your-demo-site.com)

---

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/threat-neutralizer?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/threat-neutralizer?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/threat-neutralizer)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/threat-neutralizer)

---

<div align="center">

### ⭐ If you found this project interesting, please consider giving it a star!

**Built in 30 hours | Top 10 Hackathon Project | Production Ready**

Made with 💻 and ☕

</div>
