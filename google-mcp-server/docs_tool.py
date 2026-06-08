from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth import get_credentials

def append_to_doc(doc_id: str, content: str):
    """
    Appends the specified text content to the end of a Google Document.
    
    Args:
        doc_id (str): The Google Document ID.
        content (str): The text content to append.
    """
    creds = get_credentials()
    try:
        service = build('docs', 'v1', credentials=creds)
        
        # Retrieve the document to find the correct ending index
        doc = service.documents().get(documentId=doc_id).execute()
        content_list = doc.get('body', {}).get('content', [])
        
        if content_list:
            # Get the end index from the last structural element in the document.
            # We subtract 1 to insert right before the closing newline of the document.
            end_index = content_list[-1].get('endIndex') - 1
            if end_index < 1:
                end_index = 1
        else:
            end_index = 1
            
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': end_index,
                    },
                    'text': content
                }
            }
        ]
        
        result = service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        
        return result
    except HttpError as err:
        print(f"Google Docs API HTTP error: {err}")
        raise err
    except Exception as e:
        print(f"Unexpected error in docs_tool: {e}")
        raise e
