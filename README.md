# FastAPI + Supabase Project Template

This documentation provides a complete guide for setting up a lightweight backend service associated with your supabase auth-enabled project.
It provides minimal FastAPI helpers for JWT token authentication & authorization : 
 - validates supabase auth JWT token vs your project secret key to secure the endpoints, while leaving all other aspects of the OAuth flow to Supabase : 
    - the token expiration & refresh token must be handled by another part of your application (typically your frontend JS that uses supabase lib) , as Supabase’s OAuth JWT tokens typically expire in 1 hour (60 minutes) by default.
 - provides a decorator the check the jwt role
 - default CORS config 

It does not include code to generate new token as this could mess with supabase, as there would be no matching users in BD
check the 

[ project template](./src/template/main.py) to get started 

## 🚀 Quick Start

```python
pip install git+https://github.com/Brunwo/supaFast
```

or add 
```python
git+https://github.com/Brunwo/supaFast
```

in your `requirements.txt`

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

## Configuration

### Option 1: Direct configuration (recommended)

```python
from fastapi_supabase import SupabaseAuthConfig, JWTAuthenticator
config = SupabaseAuthConfig(
supa_jwt_secret="your_jwt_secret",
origins=["http://localhost:3000"]
)
auth = JWTAuthenticator(config)
```
### Option 2: Environment variables


```python
from fastapi_supabase import SupabaseAuthConfig, JWTAuthenticator
This will automatically load from .env file
config = SupabaseAuthConfig.from_env()
auth = JWTAuthenticator(config)

```

possible future extensions : 

allow checks for custom RBAC roles : 
https://supabase.com/docs/guides/database/postgres/custom-claims-and-role-based-access-control-rbac

#extract a real token from your app to test it : 

```javascript

var token;

for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.endsWith('-auth-token')) {
        const storedData = JSON.parse(localStorage.getItem(key)); 
        token = storedData.access_token; 
        console.log(`Found token for key "${key}":`, token);
        break;  
    }
}

if (!token) {
    console.log("No matching token found in localStorage.");
}


```
origins=["http://localhost:3000"]
)
auth = JWTAuthenticator(config)
```
### Option 2: Environment variables

```python
from fastapi_supabase import SupabaseAuthConfig, JWTAuthenticator
# This will automatically load from .env file
config = SupabaseAuthConfig.from_env()
auth = JWTAuthenticator(config)
```

### Development Mode

For development and testing purposes, you can enable a development mode that bypasses Supabase JWT validation:

```env
# .env file
DEV_MODE=true
DEV_TOKEN=your-dev-token  # The token to check against
DEV_USER_ID=custom-dev-user  # Optional, defaults to "dev-user"
DEV_ROLE=custom-role  # Optional, defaults to "authenticated"
DEV_EMAIL=custom@email.com  # Optional
```

When dev mode is enabled:
- JWT validation against Supabase is bypassed
- Token is checked for exact match with `DEV_TOKEN`
- A warning is logged indicating dev mode is active
- The configured dev user details are returned upon successful authentication

⚠️ **Important**: Never enable dev mode in production environments.

possible future extensions : 

allow checks for custom RBAC roles : 
https://supabase.com/docs/guides/database/postgres/custom-claims-and-role-based-access-control-rbac

#extract a real token from your app to test it : 

```javascript

var token;

for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.endsWith('-auth-token')) {
        const storedData = JSON.parse(localStorage.getItem(key)); 
        token = storedData.access_token; 
        console.log(`Found token for key "${key}":`, token);
        break;  
    }
}

if (!token) {
    console.log("No matching token found in localStorage.");
}