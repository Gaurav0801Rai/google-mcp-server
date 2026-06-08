import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials

def create_email_draft(to: str, subject: str, body: str):
    """
    Creates an email draft in the user's Gmail account.
    
    Args:
        to (str): The email recipient.
        subject (str): The subject line of the email.
        body (str): The text content of the email.
    """
    creds = get_credentials()
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Create draft message structure
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to
        message['Subject'] = subject
        
        # The Gmail API requires drafts/messages payload raw to be urlsafe base64 encoded
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        draft_payload = {
            'message': {
                'raw': encoded_message
            }
        }
        
        draft = service.users().drafts().create(
            userId="me",
            body=draft_payload
        ).execute()
        
        return draft
    except HttpError as err:
        print(f"Gmail API HTTP error: {err}")
        raise err
    except Exception as e:
        print(f"Unexpected error in gmail_tool: {e}")
        raise e
