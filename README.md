# FastAPI Supabase Auth Helper

This project provides a lightweight library and an example template for integrating Supabase JWT authentication with FastAPI backends. It helps secure your FastAPI endpoints by validating Supabase JWTs and checking user roles.

**Key Features:**
- Validates Supabase Auth JWT tokens against your project's JWT secret.
- Provides FastAPI dependencies and decorators for easy route protection.
- Supports role-based access control (RBAC) via JWT claims.
- Configurable CORS middleware setup.
- Includes a development mode for bypassing Supabase validation with a fixed token.
- Example project template (`src/template/main.py`) to demonstrate usage.

## 🚀 Quick Start: Running the Example Template

This guide helps you run the example FastAPI application included in `src/template/`.

**1. Prerequisites:**
   - Python 3.8+
   - Node.js and npm (optional, for using the JWT generator script)
   - `git` (for cloning, if you haven't already)

**2. Clone the Repository (if you haven't):**
   ```bash
   # If you are working with this repo directly
   # git clone <repository_url>
   # cd <repository_name>
   ```

**3. Set up Environment & Install Dependencies:**
   The `install.sh` script installs the library and its development dependencies, including `httpie` (for `test.sh`) and `python-dotenv`.
   ```bash
   bash install.sh
   ```
   This installs the `fastapi-supabase` package in editable mode along with its dependencies.

**4. Configure Environment Variables for the Example App:**
   The example app in `src/template/main.py` requires a `.env` file within its own directory (`src/template/.env`).
   - Copy the template: `cp src/template/.env.template src/template/.env`
   - Edit `src/template/.env` and set the following:
     ```env
     # src/template/.env
     SUPA_JWT_SECRET="your_actual_supabase_jwt_secret_or_a_strong_placeholder_for_dev_mode"
     ORIGINS="http://localhost:3000,http://127.0.0.1:3000" # Adjust for your frontend

     # For Development/Testing the example with test.sh:
     DEV_MODE=true
     # This DEV_TOKEN should match the TEST_TOKEN in the root .env if you use test.sh
     DEV_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImlzX2Fub255bW91cyI6ZmFsc2UsImV4cCI6MTkwMDAwMDAwMH0.dummy_signature_for_test_sh"
     DEV_USER_ID="dev-user-from-env"
     DEV_ROLE="authenticated"
     DEV_EMAIL="dev@example.com"
     ```
     **Note on `SUPA_JWT_SECRET`**: For `DEV_MODE=true`, this secret is not actively used for validation by the example app, but it's good practice to have it set. The `DEV_TOKEN` will be used instead. For production or testing against actual Supabase JWTs, set `DEV_MODE=false` and ensure `SUPA_JWT_SECRET` is your actual Supabase project JWT secret.

**5. Launch the Example Application:**
   ```bash
   bash launch.sh
   ```
   This will start the FastAPI server, typically on `http://0.0.0.0:8000`. The `src/template/main.py` script handles loading its own `.env` file.

**6. Test Endpoints (Optional - see "Testing" section for more):**
   You can now access endpoints like:
   - `http://localhost:8000/public`
   - `http://localhost:8000/health`
   - For protected endpoints, you'll need a valid token (see "Generating Test Tokens" and "Testing" sections).

## 📦 Using the Library in Your Own Project

To use `fastapi-supabase` in your own FastAPI project:

**1. Installation:**
   ```bash
   pip install fastapi-supabase # Or from git: pip install git+https://github.com/Brunwo/supaFast
   ```
   Ensure you also have `fastapi` and `uvicorn`.

**2. Configuration:**
   The library uses `pydantic-settings` for configuration, loading values from environment variables or a `.env` file in your project's root by default.

   **Option A: Environment Variables (Recommended for Production)**
   Set these in your environment:
   - `SUPA_JWT_SECRET`: Your Supabase JWT Secret (required).
   - `ORIGINS`: Comma-separated list of allowed CORS origins (e.g., "http://localhost:3000,https://yourdomain.com").
   - `DEV_MODE`: `true` or `false`. Defaults to `false`.
   - `DEV_TOKEN`, `DEV_USER_ID`, `DEV_ROLE`, `DEV_EMAIL`: If `DEV_MODE=true`.

   **Option B: Direct Instantiation**
   ```python
   from fastapi import FastAPI
   from fastapi_supabase import SupabaseAuthConfig, JWTAuthenticator, add_cors_middleware, auth

   app = FastAPI()

   # Configure
   auth_config = SupabaseAuthConfig(
       supa_jwt_secret="your_actual_secret_here_if_not_using_env_vars",
       origins=["http://localhost:your_frontend_port"],
       # dev_mode=False, # Explicitly
   )
   jwt_authenticator = JWTAuthenticator(config=auth_config)

   # Add CORS middleware
   add_cors_middleware(app, auth_config)

   @app.get("/protected-route")
   async def protected_route_example(current_user: auth.TokenData = Depends(jwt_authenticator)):
       return {"message": "Hello, authenticated user!", "user_id": current_user.user_id, "role": current_user.role}

   # See src/template/main.py for more examples including role checks.
   ```

## ⚙️ Configuration Details

The `SupabaseAuthConfig` model (from `fastapi_supabase.config`) loads the following settings:

- `supa_jwt_secret` (str, required): Your Supabase project's JWT secret.
- `origins` (Optional[List[str]], default=None): List of allowed CORS origins. Parsed from a comma-separated string in env vars.
- `dev_mode` (bool, default=False): If true, bypasses Supabase JWT validation and uses `DEV_TOKEN`.
- `dev_token` (Optional[str]): Token to use when `dev_mode` is true.
- `dev_user_id` (Optional[str], default="dev-user"): User ID for dev mode.
- `dev_role` (Optional[str], default="authenticated"): Role for dev mode.
- `dev_email` (Optional[str], default="dev@example.com"): Email for dev mode.

These are loaded from environment variables (case-insensitive) or a `.env` file in the current working directory of your application when `SupabaseAuthConfig()` is called.

### Development Mode
When `dev_mode` is true:
- JWT validation against `supa_jwt_secret` is bypassed.
- The provided token is checked for an exact match with `dev_token`.
- A warning is logged.
- Configured dev user details (`dev_user_id`, `dev_role`, `dev_email`) are returned.
⚠️ **Important**: Never enable dev mode in production environments.

## 🧪 Testing

### Running `test.sh` for the Example App
The `test.sh` script provides basic end-to-end tests for the example application (`src/template/main.py`).

**1. Setup Root `.env` for `test.sh`:**
   `test.sh` expects a `.env` file in the *root* of the repository to source a `TEST_TOKEN`.
   - Create or ensure `.env` exists in the project root.
   - Add `TEST_TOKEN`:
     ```env
     # Root .env file (for test.sh)
     TEST_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImlzX2Fub255bW91cyI6ZmFsc2UsImV4cCI6MTkwMDAwMDAwMH0.dummy_signature_for_test_sh"
     ```
     **Important**: If `src/template/main.py` is running in `DEV_MODE=true` (as recommended for `test.sh`), its `DEV_TOKEN` (in `src/template/.env`) **must match** this `TEST_TOKEN`.

**2. Run the Test Script:**
   Ensure the example application is running (e.g., via `bash launch.sh` in another terminal or backgrounded). Then:
   ```bash
   bash test.sh
   ```
   This script uses `httpie` to make requests to the public and protected endpoints.

### Generating Test Tokens
A Node.js script `generate-jwt.js` is provided to create custom JWTs for testing.

**1. Prerequisites:**
   - Node.js and npm.
   - Install dependencies for the script:
     ```bash
     npm install jsonwebtoken yargs dotenv
     ```
     (Run this in the root of the project or ensure these are globally available if preferred).

**2. Make Executable:**
   ```bash
   chmod +x generate-jwt.js
   ```

**3. Usage:**
   ```bash
   ./generate-jwt.js --role <role_name> --subject <user_id> [--expiry <time>] [--secret <your_jwt_secret>] [--debug]
   ```
   - `--role` (or `-r`): (Required) Role for the token (e.g., `authenticated`, `admin`).
   - `--subject` (or `-s`): User ID/subject for the token (default: `system-generated-user`).
   - `--expiry` (or `-e`): Token expiry (e.g., "1h", "7d", default: "1h").
   - `--secret` (or `-k`): The JWT secret to sign the token. If not provided, it tries to load `SUPABASE_JWT_SECRET` from a root `.env` file.
   - `--debug` (or `-d`): Outputs the generated token and its decoded payload.

   **Example:**
   ```bash
   # Using a secret from command line
   ./generate-jwt.js --role authenticated --subject user123 --secret "SUPER_SECRET_DEVELOPMENT_VALUE_MUST_BE_32_CHARS_OR_LONGER" --debug

   # Relying on SUPABASE_JWT_SECRET from .env
   # (Ensure SUPABASE_JWT_SECRET is in your root .env)
   # ./generate-jwt.js --role admin --subject admin-user
   ```
   Use the generated token in the `Authorization: Bearer <token>` header when testing your protected endpoints.

## 🔐 Security
- Store `SUPA_JWT_SECRET` securely. Do not commit it to version control. Use environment variables or a secrets manager in production.
- The `dev_mode` is for development convenience only. **Never enable it in production.**
- Ensure `origins` for CORS is configured restrictively to only allow your frontend domains.

## ☁️ Google Cloud Function Proxy (Conceptual)

This library can be used within a Google Cloud Function (GCF) to act as an authenticating proxy for a backend service (e.g., another Cloud Run instance).

**Concept:**
1. The GCF receives incoming requests.
2. It uses `fastapi-supabase` (or its core logic) to validate the JWT from the `Authorization` header.
3. It checks for required roles if specified.
4. If authentication and authorization succeed, it forwards the request to the target backend service, potentially injecting user identity information (like `X-Authenticated-User-Id`) in headers.
5. It returns the response from the backend service.

**Key Environment Variables for such a GCF:**
- `SUPA_JWT_SECRET`: Your Supabase JWT secret.
- `TARGET_CLOUD_RUN_URL`: The URL of the backend service to proxy to.
- `GCF_EXPECTED_AUDIENCE`: (Optional) Expected 'aud' claim for JWTs.
- `GCF_EXPECTED_ISSUER`: (Optional) Expected 'iss' claim for JWTs.
- `GCF_REQUIRED_ROLES`: (Optional) Comma-separated list of roles required to access the backend.

An example implementation of such a proxy GCF can be structured using FastAPI, similar to the provided template, but with added logic for request forwarding (e.g., using `httpx`). (A more detailed example was discussed during development and can be provided if needed).

## ↔️ Authentication Flow (Brief)
1. Your frontend application uses a Supabase client library (e.g., `supabase-js`) to handle user login.
2. Upon successful login, Supabase issues a JWT.
3. Your frontend stores this JWT and sends it in the `Authorization: Bearer <token>` header with requests to your FastAPI backend.
4. This `fastapi-supabase` library on your backend validates the token.
5. If valid, your endpoint processes the request. The decoded token data (user ID, role, etc.) is available via the `Depends(jwt_authenticator)` dependency.

The library primarily handles step 4 and 5. Token expiration and refresh should be managed by your frontend using Supabase client libraries.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome. Please open an issue to discuss any significant changes.