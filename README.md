# 🛡️ Threat Neutralizer

[![Hackathon](https://img.shields.io/badge/Hackathon-Top%2010-gold?style=for-the-badge)](https://github.com/swarapotd-rgb/threat-neutralizer)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://python.org)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=for-the-badge&logo=react)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)

> A secure intelligence management system with enterprise-grade authentication and role-based access control. **Top 10 Finalist** in a competitive 30-hour hackathon 🏆

![Threat Neutralizer](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square)
![Security](https://img.shields.io/badge/Security-MFA%20Enabled-red?style=flat-square)
![Build Time](https://img.shields.io/badge/Built%20In-30%20Hours-orange?style=flat-square)

---

## 🎯 Overview

**Threat Neutralizer** is a full-stack web application designed for secure management of classified information, personnel records, and operational data. Built with security-first principles during an intense 30-hour hackathon, it demonstrates production-ready implementation of:

- 🔐 Multi-Factor Authentication (JWT + TOTP)
- 👥 Role-Based Access Control (RBAC)
- 📝 Comprehensive Audit Logging
- 🚦 Advanced Rate Limiting
- 🔒 Secure File Management

### 🏆 Hackathon Achievement
- **Ranking**: Top 10 Finalist
- **Time Constraint**: 30 hours from concept to deployment
- **Focus**: Security-first architecture with real-world applicability

---

## ✨ Key Features

### 🔐 Security & Authentication
- **Multi-Factor Authentication**: JWT tokens combined with TOTP (Time-based One-Time Password)
- **Role-Based Access Control**: Granular permissions for Admin, File Manager, and custom roles
- **Rate Limiting**: Protection against brute-force attacks (100 req/15min, 50 failed login attempts)
- **Password Security**: bcrypt hashing with automatic salt
- **Token Validation**: Database-backed JWT verification
- **Audit Trail**: Comprehensive logging of all user actions

### 📁 Core Modules
- **Classified Files Management**: Secure document upload, storage, and download with role-based permissions
- **Personnel (Agents) Management**: Agent profiles, clearance levels, and mission history
- **Secured Locations**: Geographic intelligence database with access controls
- **Operations Tracking**: Mission planning, execution logs, and timeline management
- **Admin Dashboard**: System-wide monitoring and audit log analysis

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLite** - Embedded database (production-ready for PostgreSQL migration)
- **PyJWT** - JSON Web Token implementation
- **PyOTP** - TOTP authentication
- **bcrypt** - Password hashing
- **Uvicorn** - ASGI server

### Frontend
- **React 18.2** - UI library with hooks
- **Vite** - Next-generation frontend tooling
- **TailwindCSS** - Utility-first CSS framework
- **React Router DOM** - Client-side routing

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.10+
Node.js 16+
npm or yarn
```

### Installation

```bash
# Clone the repository
git clone https://github.com/swarapotd-rgb/threat-neutralizer.git
cd threat-neutralizer/mvp-final

# Backend setup
cd backend
pip install fastapi uvicorn sqlalchemy pydantic pyotp pyjwt bcrypt python-multipart
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (in a new terminal)
cd ../
npm install
npm run dev
```

### Access the Application
- 🌐 **Frontend**: http://localhost:5173
- 📚 **API Docs**: http://localhost:8000/docs
- 🔌 **API**: http://localhost:8000

---

## 🔑 Authentication

### Default Test Accounts

**Admin Account:**
```
Username: admin
Password: admin123
TOTP Secret: JBSWY3DPEHPK3PXP
```

**File Manager Account:**
```
Username: user
Password: user123
TOTP Secret: JBSWY3DPEHPK3PXQ
```

### Generate TOTP Codes

```bash
# Quick method
cd backend
python get_totp.py
```

Or use any TOTP authenticator app (Google Authenticator, Microsoft Authenticator, Authy) with the secrets above.

---

## 📖 API Documentation

### Authentication Flow

**POST** `/login`
```json
{
  "username": "admin",
  "password": "admin123",
  "totp_code": "123456"
}
```

### Protected Endpoints
All require: `Authorization: Bearer <token>`

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/files` | List accessible files | Authenticated |
| GET | `/files/{id}` | Download file | Role-based |
| GET | `/agents` | List all agents | Authenticated |
| GET | `/agents/{id}` | Agent details | Authenticated |
| GET | `/locations` | List locations | Authenticated |
| GET | `/operations` | List operations | Role-filtered |
| GET | `/logs` | Audit logs | Admin only |

**Interactive API Testing**: Visit http://localhost:8000/docs for Swagger UI

---

## 🏗️ Project Structure

```
threat-neutralizer/
├── mvp-final/
│   ├── backend/
│   │   ├── main.py              # FastAPI app & routes
│   │   ├── database.py          # Database operations
│   │   ├── auth.py              # Authentication utilities
│   │   ├── get_totp.py         # TOTP generator
│   │   └── secure.db           # SQLite database
│   ├── src/
│   │   ├── pages/              # React components
│   │   ├── utils/              # API utilities
│   │   └── App.jsx             # Main component
│   └── package.json
└── README.md
```

---

## 🔒 Security Features

### Multi-Layer Security Architecture
```
User Authentication (Username + Password + TOTP)
           ↓
Rate Limiting Check (100 req/15min)
           ↓
Token Generation & Storage (JWT + DB)
           ↓
Role-Based Access Control (RBAC)
           ↓
Audit Log Recording
```

### Access Control Matrix

| Resource | Admin | File Manager | Guest |
|----------|-------|--------------|-------|
| All files | ✅ | ❌ | ❌ |
| Assigned files | ✅ | ✅ | ❌ |
| Agent profiles | ✅ | ✅ | ❌ |
| Operations | ✅ | ⚠️ Filtered | ❌ |
| Audit logs | ✅ | ❌ | ❌ |

---

## 🧪 Testing

### Manual Testing
```bash
# Generate TOTP code
python backend/get_totp.py

# Test API with cURL
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123","totp_code":"123456"}'
```

### API Testing
Use the interactive Swagger UI at http://localhost:8000/docs


```
<div align="center">

### ⭐ If you found this project interesting, please consider giving it a star!

**Built in 30 hours | Top 10 Hackathon Project | Production Ready**

Made with 💻 and ☕

</div>

