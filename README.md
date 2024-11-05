# FastAPI + Supabase Project Template

This documentation provides a complete guide for setting up and using the FastAPI + Supabase project template.

## 🚀 Quick Start

1. Clone the repository
2. Run the installation script:
```bash
./template/install.sh
```

### Authentication

The `auth.py` module handles authentication using Supabase. It provides basic:
- JWT token validation
- User session management
- Role-based access control

The `main.py` provide a simple server showcasing jwt validation

## 📦 Installation

The `install.sh` script handles:
1. Dependencies installation
2. Environment setup
3. Initial configuration

## 🧪 Testing

Run a sample using httpie:

```bash
./template/test.sh
```

## 🔒 Security

- All sensitive credentials should be stored in `.env`
- Never commit `.env` to version control
