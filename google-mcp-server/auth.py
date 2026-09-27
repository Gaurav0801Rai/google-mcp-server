import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth Scopes for Google Docs (editing/appending) and Gmail (creating drafts/sending)
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.send'
]

IS_SERVERLESS = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if IS_SERVERLESS:
    TMP_DIR = os.environ.get("TMPDIR", "/tmp")
    CREDENTIALS_PATH = os.path.join(TMP_DIR, 'credentials.json')
    TOKEN_PATH = os.path.join(TMP_DIR, 'token.json')
else:
    CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')
    TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')

def get_credentials():
    """Gets valid user credentials from file or runs user auth flow if needed."""
    creds = None

    # In serverless/cloud environments, attempt direct in-memory loading first
    env_token = os.environ.get("GOOGLE_TOKEN_JSON")
    if env_token:
        try:
            token_data = json.loads(env_token.strip())
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception as e:
            print(f"Error loading credentials from GOOGLE_TOKEN_JSON: {e}")

    # Write credentials and token from environment variables if files are missing and disk is writable
    env_creds = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if env_creds and not os.path.exists(CREDENTIALS_PATH):
        try:
            with open(CREDENTIALS_PATH, 'w') as f:
                f.write(env_creds.strip())
        except Exception as e:
            print(f"Notice: Could not write credentials.json to disk ({e}). Proceeding...")

    if env_token and not os.path.exists(TOKEN_PATH):
        try:
            with open(TOKEN_PATH, 'w') as f:
                f.write(env_token.strip())
        except Exception as e:
            print(f"Notice: Could not write token.json to disk ({e}). Proceeding...")

    # Load existing token.json from disk if not yet loaded from env
    if not creds and os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception as e:
            print(f"Error loading token.json: {e}. Re-authenticating...")
            creds = None
            
    # If credentials exist but expired, refresh them
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"Failed to refresh token: {e}. Performing clean login...")
            creds = None
            
    # If still no valid credentials, run local auth flow
    if not creds or not creds.valid:
        if not os.path.exists(CREDENTIALS_PATH):
            raise FileNotFoundError(
                f"\n[ERROR] credentials.json not found at '{CREDENTIALS_PATH}'.\n"
                "Please download your OAuth 2.0 Client credentials (type Desktop Application) "
                "from Google Cloud Console, rename it to 'credentials.json', and place it in the project root "
                "or set the GOOGLE_CREDENTIALS_JSON / GOOGLE_TOKEN_JSON environment variables."
            )
        
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        # Force Google to show the consent screen so the user can select all scope checkboxes
        creds = flow.run_local_server(port=0, prompt='consent')
        
    # Save credentials for future execution if disk is writable
    if creds and creds.valid:
        try:
            with open(TOKEN_PATH, 'w') as token_file:
                token_file.write(creds.to_json())
        except OSError:
            pass  # Read-only filesystem in serverless environments
        
    return creds

