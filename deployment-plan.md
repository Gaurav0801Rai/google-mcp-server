# Google MCP Server Deployment Plan (Railway)

This document provides step-by-step instructions for deploying the Google Docs & Gmail MCP Server to [Railway](https://railway.app/).

---

## 🛠️ Architecture & Railway Considerations

Because this server is designed as an interactive tool that reads credentials from local files and prompts for user verification in the terminal, deploying it to a cloud container environment requires addressing three key aspects:

1. **Non-Interactive Environment**: Cloud servers run in headless containers where terminal input (`stdin`) is unavailable. The code has been updated to support bypassing manual console approval.
2. **Dynamic Host & Port Binding**: Railway dynamically assigns a port to the container and expects the server to listen on all interfaces (`0.0.0.0`). The code has been updated to dynamically read the host and port configurations from environment variables.
3. **Secret Management & Git**: Secret files like `credentials.json` and `token.json` must **never** be committed to GitHub. The code has been updated to reconstruct these files on startup if they are provided as environment variables.

---

## 📋 Prerequisites

Before deploying to Railway, ensure that you have:
1. Created a [Railway account](https://railway.app/).
2. Installed the [Railway CLI](https://docs.railway.app/guides/cli) (optional, but recommended for local-to-cloud deployments).
3. Generated credentials and a valid user token locally by running the server once.

---

## 🚀 Step-by-Step Deployment Guide

### Step 1: Generate Google OAuth Credentials and Tokens Locally
Since Google Cloud restricts Desktop Application OAuth redirects to `http://localhost`, you **must** perform the initial authentication locally:
1. Ensure `credentials.json` is in the `google-mcp-server` directory.
2. Run the server locally:
   ```bash
   python server.py
   ```
3. Call any endpoint (e.g., `/append_to_doc`) to trigger the OAuth browser popup.
4. Log in and authorize the requested permissions.
5. This will generate a `token.json` file in your `google-mcp-server/` directory.

### Step 2: Prepare Your Environment Variables
You will need to pass the contents of your credentials and token files to Railway. Read the contents of these files:
- **Google Credentials Content**: The full text inside `credentials.json`.
- **Google Token Content**: The full text inside `token.json`.

> [!WARNING]
> Both `credentials.json` and `token.json` contain highly sensitive OAuth tokens and secrets that grant write access to your Google Docs and Gmail accounts. Keep these secure and do not share them.

### Step 3: Create a Railway Project
1. Go to the [Railway Dashboard](https://railway.app/) and click **New Project**.
2. Select **Deploy from GitHub repo** (if your project is pushed to GitHub) or choose **Empty Project** if you are deploying from your local machine using the CLI.
3. If deploying via CLI:
   - Run `railway login` in your local terminal.
   - Run `railway init` inside the project directory.

### Step 4: Configure Environment Variables in Railway
Go to your Railway Service settings under the **Variables** tab and add the following:

| Variable Name | Value | Description |
| :--- | :--- | :--- |
| `HOST` | `0.0.0.0` | Allows Railway to route external traffic to your FastAPI app. |
| `PORT` | *(Leave blank / Auto)* | Railway automatically injects the correct port. |
| `BYPASS_APPROVAL` | `true` | Automatically bypasses the `Approve? (y/n)` console prompt in production. |
| `GOOGLE_CREDENTIALS_JSON` | *Copy-paste entire text from `credentials.json`* | The GCP desktop client credentials. |
| `GOOGLE_TOKEN_JSON` | *Copy-paste entire text from `token.json`* | The authorized user token generated in Step 1. |

> [!NOTE]
> The server automatically reads `GOOGLE_CREDENTIALS_JSON` and `GOOGLE_TOKEN_JSON` at startup and writes them to their correct locations on disk so the Google API client can locate them.

### Step 5: Configure Build and Start Settings
In Railway, verify the following configuration under the **Settings** tab:
- **Build Command**: Railway automatically detects Python and runs `pip install -r requirements.txt`. No build command is needed.
- **Start Command**: Set this to:
  ```bash
  python server.py
  ```
  *(Note: Since `server.py` invokes Uvicorn dynamically and binds it to `HOST` and `PORT`, this starts the server successfully).*

### Step 6: Deploy & Verify
1. Trigger the deployment on Railway.
2. Once the build completes and the container is running, check the **Deploy Logs** to verify that the server has started successfully and bound to the assigned port.
3. Railway will generate a public URL for your service (e.g., `https://google-mcp-server-production.up.railway.app`).
4. Test the API endpoints using the public URL.

---

## 🔍 Verification & Testing

Verify that the deployed server can execute actions without requiring console approval:

### 1. Test Google Docs Append API
```bash
curl -X POST https://<your-railway-url>.up.railway.app/append_to_doc \
  -H "Content-Type: application/json" \
  -d '{"doc_id": "<your-google-doc-id>", "content": "Hello from Railway!\n"}'
```

### 2. Test Gmail Draft API
```bash
curl -X POST https://<your-railway-url>.up.railway.app/create_email_draft \
  -H "Content-Type: application/json" \
  -d '{"to": "your-email@example.com", "subject": "Hello from Railway", "body": "This is a draft sent from the deployed MCP server on Railway."}'
```

Check the Railway runtime logs to verify the output:
```text
[INFO] Bypassing approval for action 'append_to_doc' (BYPASS_APPROVAL is enabled).
```
