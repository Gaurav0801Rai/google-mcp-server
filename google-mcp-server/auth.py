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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')

def get_credentials():
    """Gets valid user credentials from file or runs user auth flow if needed."""
    # Write credentials and token from environment variables if they exist and files are missing
    # This enables smooth deployment on cloud platforms like Railway where files are gitignored.
    env_creds = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if env_creds and not os.path.exists(CREDENTIALS_PATH):
        try:
            with open(CREDENTIALS_PATH, 'w') as f:
                f.write(env_creds.strip())
        except Exception as e:
            print(f"Error writing credentials.json from env: {e}")

    env_token = os.environ.get("GOOGLE_TOKEN_JSON")
    if env_token and not os.path.exists(TOKEN_PATH):
        try:
            with open(TOKEN_PATH, 'w') as f:
                f.write(env_token.strip())
        except Exception as e:
            print(f"Error writing token.json from env: {e}")

    creds = None
    
    # Load existing token.json if it exists
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception as e:
            print(f"Error loading token.json: {e}. Re-authenticating...")
            creds = None
            
    # If there are no valid credentials, authenticates the user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Failed to refresh token: {e}. Performing clean login...")
                creds = None
                
        if not creds or not creds.valid:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"\n[ERROR] credentials.json not found at '{CREDENTIALS_PATH}'.\n"
                    "Please download your OAuth 2.0 Client credentials (type Desktop Application) "
                    "from Google Cloud Console, rename it to 'credentials.json', and place it in the project root."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            # Force Google to show the consent screen so the user can select all scope checkboxes
            creds = flow.run_local_server(port=0, prompt='consent')
            
        # Save credentials for future execution
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
            
    return creds
