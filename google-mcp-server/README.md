# Google Docs & Gmail MCP-Style Server

A complete MCP-style server written in Python using FastAPI. It integrates with Google Docs and Gmail APIs, prompting the user in the terminal for manual authorization before executing any write operations.

## Project Structure

```text
google-mcp-server/
├── server.py          → FastAPI app with tool endpoints
├── auth.py            → Google OAuth authentication
├── docs_tool.py       → Google Docs tool (append content)
├── gmail_tool.py      → Gmail tool (create draft)
├── requirements.txt   → All dependencies
├── README.md          → Setup and usage instructions
├── credentials.json   → (NOT committed — downloaded from Google Cloud)
└── token.json         → (NOT committed — auto-generated after OAuth)
```

---

## Setup & Installation

### 1. Prerequisites
- Python 3.8+
- A Google Cloud Platform (GCP) project with Docs & Gmail APIs enabled.

### 2. Enable Google APIs & Get Credentials
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable the following APIs:
   - **Google Docs API**
   - **Gmail API**
4. Configure the **OAuth Consent Screen**:
   - Select **External** user type.
   - Fill in the required app information.
   - Add the following Scopes:
     - `https://www.googleapis.com/auth/documents`
     - `https://www.googleapis.com/auth/gmail.compose`
   - Add your own email as a **Test User** (required while in testing status).
5. Create Credentials:
   - Go to the **Credentials** page.
   - Click **Create Credentials** -> **OAuth client ID**.
   - Select **Desktop Application** as the application type.
   - Click **Create**.
   - Download the generated JSON credentials file, rename it to `credentials.json`, and place it in the `google-mcp-server/` directory.

### 3. Install Dependencies
Navigate to the project directory and install the required Python packages:
```bash
pip install -r requirements.txt
```

---

## Running the Server

Start the FastAPI application by running:
```bash
python server.py
```
Or:
```bash
uvicorn server:app --host 127.0.0.1 --port 8000
```
*(Note: Do not run with `--reload` since Uvicorn's reload mechanism detaches stdin and prevents interactive terminal prompts from working).*

### First Run Authentication
On the first run, calling any endpoint or booting the service will trigger the OAuth flow if `token.json` is not present:
1. Your default web browser will open, prompting you to log in with your Google account.
2. Accept the authorization scopes.
3. Once authenticated, a `token.json` file will be generated in the project folder. Subsequent runs will skip this browser flow.

---

## Tool API Endpoints

### 1. Append Text to Google Doc
Appends text to the end of a specific Google Doc.

- **Endpoint**: `POST /append_to_doc`
- **Payload**:
  ```json
  {
    "doc_id": "YOUR_DOCUMENT_ID",
    "content": "This is a new line of text appended by the MCP server.\n"
  }
  ```

#### Example using `curl`:
```bash
curl -X POST http://127.0.0.1:8000/append_to_doc \
  -H "Content-Type: application/json" \
  -d "{\"doc_id\": \"1952Vw8Q1hA4...\", \"content\": \"Hello World!\\n\"}"
```

### 2. Create Email Draft
Creates a Gmail draft.

- **Endpoint**: `POST /create_email_draft`
- **Payload**:
  ```json
  {
    "to": "recipient@example.com",
    "subject": "Greetings from MCP",
    "body": "Hello, this is a draft created by the Google MCP Server!"
  }
  ```

#### Example using `curl`:
```bash
curl -X POST http://127.0.0.1:8000/create_email_draft \
  -H "Content-Type: application/json" \
  -d "{\"to\": \"recipient@example.com\", \"subject\": \"Test MCP\", \"body\": \"This is the email body.\"}"
```

---

## Interactive Approval Flow

When a POST request is sent to the server, the execution halts and the server logs the request parameters to the terminal, requesting approval:

```text
==========================================
[ACTION REQUESTED]: create_email_draft
Payload:
  - to: recipient@example.com
  - subject: Test MCP
  - body: This is the email body.
==========================================
Approve? (y/n): 
```

- Type `y` and press **Enter** to authorize the action.
- Type `n` and press **Enter** to block it. (Returns `403 Forbidden` response to the caller).
