# Google Cloud Function Deployment Guide

This directory contains the necessary files and instructions to deploy the Supabase JWT authentication logic as a serverless Google Cloud Function.

The function (`protected_endpoint` in `main.py`) acts as a secure endpoint that validates a Supabase JWT bearer token before granting access.

## Prerequisites

1.  **Google Cloud SDK (`gcloud`)**: You must have the `gcloud` CLI installed and authenticated.
2.  **Google Cloud Project**: A Google Cloud project must be created.
3.  **Updated Repository**: Ensure the latest changes are pushed to the `main` branch of this GitHub repository, as the function installs the package directly from there.

## Setup & Deployment

A single script handles the entire setup and deployment process.

### Step 1: Configure Your Environment

Edit the `set_envs.sh` file and replace the placeholder values with your actual Google Cloud `PROJECT_ID` and desired `REGION`.

```bash
# gcp_function/set_envs.sh
export PROJECT_ID="your-gcp-project-id"
export REGION="your-gcp-region"
```

### Step 2: Set Your JWT Secret

Create a copy of the environment variable template:

```bash
cp gcp_function/.env.yaml.template gcp_function/.env.yaml
```

Then, edit the newly created `gcp_function/.env.yaml` and replace `your-jwt-secret-here` with your actual Supabase JWT secret. This file is ignored by git, so your secret will not be committed.

### Step 3: Run the Deployment Script

Execute the following command from the **root of the repository**:

```bash
./gcp_function/setup_and_deploy.sh
```

The script will:
1.  Source the environment variables you configured.
2.  Enable the required Google Cloud APIs (Cloud Functions and Cloud Build).
3.  Deploy the function, using the secret from your `.env.yaml` file.
4.  Print the HTTPS trigger URL of your deployed function upon completion.

## Testing the Deployed Function

Once deployed, you can test the live endpoint using a tool like `curl` or `httpie`.

1.  **Generate a valid token** (from the project root):
    ```bash
    python3 create_jwt.py
    ```

2.  **Call the function URL** with the token:
    ```bash
    # Replace YOUR_FUNCTION_URL with the URL from the deployment output
    # Replace YOUR_GENERATED_TOKEN with the token from the previous step
    http GET YOUR_FUNCTION_URL "Authorization: Bearer YOUR_GENERATED_TOKEN"
    ```
