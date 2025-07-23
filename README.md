# FastAPI Supabase Auth Helper

This project provides a lightweight library and an example template for integrating Supabase JWT authentication with FastAPI backends. It helps secure your FastAPI endpoints by validating Supabase JWTs and checking user roles.

## ✨ Current Status

This library now supports two primary modes for JWT verification:

1.  **Modern (Default):** Asynchronous verification using Supabase's JWKS endpoint (RS256/ES256 algorithms). This is the recommended and default approach for new projects and those that have migrated their Supabase JWT signing to asymmetric keys.
2.  **Legacy:** Synchronous verification using a shared `SUPA_JWT_SECRET` (HS256 algorithm). This mode is provided for backward compatibility with older Supabase projects or specific use cases where HS256 is still in use. It can be enabled via the `SUPABASE_USE_LEGACY_JWT` configuration flag.

## Key Features:**
- Validates Supabase Auth JWT tokens against your project's JWT secret (legacy HS256).
- Supports asynchronous JWT verification using JWKS (RS256/ES256) for enhanced security.
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
     SUPABASE_URL="https://your-supabase-url.supabase.co"
     SUPABASE_ANON_KEY="your-supabase-anon-key"
     SUPABASE_USE_LEGACY_JWT=False # Set to True for legacy HS256 verification

     # Only required if SUPABASE_USE_LEGACY_JWT is True
     # SUPA_JWT_SECRET="your_actual_supabase_jwt_secret"

     # For Development/Testing the example with test.sh:
     DEV_MODE=true
     # This DEV_TOKEN should match the TEST_TOKEN in the root .env if you use test.sh
     DEV_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImlzX2Fub255bW91cyI6ZmFsc2UsImV4cCI6MTkwMDAwMDAwMH0.dummy_signature_for_test_sh"
     DEV_USER_ID="dev-user-from-env"
     DEV_ROLE="authenticated"
     DEV_EMAIL="dev@example.com"
     ```
     **Note on `SUPABASE_USE_LEGACY_JWT`**: If `False` (default), the application will attempt to verify JWTs using the JWKS endpoint derived from `SUPABASE_URL`. If `True`, it will use `SUPA_JWT_SECRET` for HS256 verification. For `DEV_MODE=true`, the `DEV_TOKEN` will be used instead of actual JWT validation.

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
   - `SUPABASE_URL`: Your Supabase project URL (e.g., `https://your-project.supabase.co`).
   - `SUPABASE_ANON_KEY`: Your Supabase project's `anon` key.
   - `SUPABASE_USE_LEGACY_JWT`: `True` or `False`. Defaults to `False`.
   - `SUPA_JWT_SECRET`: Your Supabase JWT Secret. Required only if `SUPABASE_USE_LEGACY_JWT` is `True`.
   - `ORIGINS`: Comma-separated list of allowed CORS origins (e.g., "http://localhost:3000,https://yourdomain.com").
   - `DEV_MODE`: `true` or `false`. Defaults to `false`.
   - `DEV_TOKEN`, `DEV_USER_ID`, `DEV_ROLE`, `DEV_EMAIL`: If `DEV_MODE=true`.

   **Option B: Direct Instantiation**
   ```python
   from fastapi import FastAPI
   from fastapi_supabase import SupabaseAuthConfig, JWTAuthenticator, add_cors_middleware
   from fastapi_supabase.models import TokenData # Import TokenData

   app = FastAPI()

   # Configure
   auth_config = SupabaseAuthConfig(
       supa_url="https://your-supabase-url.supabase.co",
       supa_anon_key="your-supabase-anon-key",
       supa_use_legacy_jwt=False, # Set to True for legacy HS256 verification
       # supa_jwt_secret="your_actual_secret_here_if_using_legacy", # Only if supa_use_legacy_jwt is True
       origins=["http://localhost:your_frontend_port"],
       # dev_mode=False, # Explicitly
   )
   jwt_authenticator = JWTAuthenticator(config=auth_config)

   # Add CORS middleware
   add_cors_middleware(app, auth_config)

   @app.get("/protected-route")
   async def protected_route_example(current_user: TokenData = Depends(jwt_authenticator)):
       return {"message": "Hello, authenticated user!", "user_id": current_user.user_id, "role": current_user.role}

   # See src/template/main.py for more examples including role checks.
   ```

## ⚙️ Configuration Details

The `SupabaseAuthConfig` model (from `fastapi_supabase.config`) loads the following settings:

- `supa_jwt_secret` (Optional[str]): Your Supabase project's JWT secret. Required only if `supa_use_legacy_jwt` is `True`.
- `supa_url` (Optional[str]): Your Supabase project URL (e.g., `https://your-project.supabase.co`). Required for JWKS verification.
- `supa_anon_key` (Optional[str]): Your Supabase project's `anon` key. Used for client-side interactions if needed.
- `supa_use_legacy_jwt` (bool, default=False): If `True`, uses the legacy HS256 JWT verification with `supa_jwt_secret`. If `False` (default), uses JWKS verification (RS256/ES256) with `supa_jwks_url`.
- `supa_jwks_url` (Optional[str]): The URL to your Supabase project's JWKS endpoint (e.g., `https://your-project.supabase.co/auth/v1/.well-known/jwks.json`). Required if `supa_use_legacy_jwt` is `False`.
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

### Testing with Supabase-issued JWTs (RS256/ES256)

To test with actual JWTs issued by your Supabase project (which are typically RS256 or ES256 signed):

**1. Ensure your Supabase project is configured for asymmetric JWT signing.**
   Refer to the Supabase documentation on "JWT Signing Keys" to migrate your project if it's still using HS256.

**2. Obtain a JWT from your Supabase project.**
   You can use the `supabase_tests/get-test-jwt.js` script (after updating `supabase_tests/package.json` with the correct `anon` key and ensuring `test@test.com` is a valid user in your Supabase project):
   ```bash
   cd supabase_tests
   npm install # if you haven't already
   npm run get-jwt
   ```
   This will save the JWT to `supabase_tests/jwt.token`.

**3. Configure `src/template/.env` for JWKS verification.**
   Set `SUPABASE_USE_LEGACY_JWT=False` and ensure `SUPABASE_URL` is correctly set.

**4. Run the FastAPI application.**

**5. Test with the obtained JWT.**
   Use the JWT from `supabase_tests/jwt.token` in your `Authorization: Bearer` header:
   ```bash
   curl -H "Authorization: Bearer $(cat supabase_tests/jwt.token)" http://localhost:8000/protected
   ```

### Testing with Legacy HS256 JWTs

If you need to test with legacy HS256 JWTs (e.g., for backward compatibility):

**1. Configure `src/template/.env` for legacy verification.**
   Set `SUPABASE_USE_LEGACY_JWT=True` and provide your `SUPA_JWT_SECRET`.

**2. Obtain an HS256 JWT.**
   You can use the `generate-jwt.js` script with your `SUPA_JWT_SECRET`:
   ```bash
   ./generate-jwt.js --role authenticated --subject user123 --secret "YOUR_SUPABASE_JWT_SECRET" --debug
   ```

**3. Run the FastAPI application.**

**4. Test with the obtained HS256 JWT.**
   ```bash
   curl -H "Authorization: Bearer YOUR_HS256_JWT_TOKEN" http://localhost:8000/protected
   ```

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

## 💡 Development Journey & Learnings

This feature implementation involved several key learning points and challenges:

- **Understanding Supabase JWT Evolution:** Initially, Supabase primarily used HS256 symmetric key signing. The new requirement highlighted a shift towards asymmetric (RS256/ES256) signing via JWKS endpoints for enhanced security and scalability. This necessitated a dual-path implementation to support both legacy and modern approaches.

- **JWKS Fetching and Caching:** Implementing asynchronous fetching of JWKS data from the Supabase endpoint was crucial. A `cachetools.TTLCache` was integrated to prevent excessive network requests and improve performance, ensuring the JWKS is refreshed periodically.

- **Handling Multiple Asymmetric Algorithms:** Supabase can use both RS256 and ES256 for asymmetric signing. The `JWTChecker` was designed to dynamically identify the algorithm from the JWT header and use the correct `PyJWT` algorithm for verification.

- **Circular Import Resolution:** A common Python challenge, circular imports, arose when `TokenData` was defined in `auth.py` and needed by the checker modules, which in turn were imported by `auth.py`. This was resolved by extracting `TokenData` into a separate `models.py` file, breaking the dependency cycle.

- **Robust Testing Workflow:** The iterative process of obtaining a valid JWT for testing proved challenging due to OAuth browser redirects and Supabase's default security features (captcha, email confirmation). This led to:
    - Developing a dedicated Node.js script (`get-test-jwt.js`) for programmatic login using email/password, bypassing browser interactions.
    - Understanding the necessity of disabling Supabase's captcha and email confirmation for automated testing.
    - Realizing the importance of ensuring the Supabase project itself is configured for asymmetric JWT signing to generate the correct tokens for JWKS verification.

- **Clear Configuration and Documentation:** The introduction of new configuration variables (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_USE_LEGACY_JWT`, `supa_jwks_url`) required careful integration and clear documentation in the `README.md` to guide users on setting up both new and legacy verification methods.

This development process underscored the importance of a thorough understanding of authentication flows, careful dependency management, and a robust testing strategy when integrating with external authentication providers like Supabase.

## 🔐 Security