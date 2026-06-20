import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from docs_tool import append_to_doc
from gmail_tool import create_email_draft, gmail_send_message

app = FastAPI(
    title="Google MCP Server",
    description="FastAPI-based MCP server providing tools for Google Docs and Gmail with terminal approval confirmation."
)

class DocAppendRequest(BaseModel):
    doc_id: str
    content: str

class EmailDraftRequest(BaseModel):
    to: str
    subject: str
    body: str

class EmailSendRequest(BaseModel):
    to: str
    subject: str
    body: str

def ask_approval(action: str, payload: dict) -> bool:
    """
    Prints the action name and payload, then asks for manual confirmation in the console.
    """
    # Check if we should bypass approval (e.g. running in production on Railway)
    if os.environ.get("BYPASS_APPROVAL", "false").lower() in ("true", "1", "yes"):
        print(f"[INFO] Bypassing approval for action '{action}' (BYPASS_APPROVAL is enabled).")
        return True

    print(f"\n==========================================")
    print(f"[ACTION REQUESTED]: {action}")
    print(f"Payload:")
    for key, val in payload.items():
        # Hide potentially long body or clean display
        print(f"  - {key}: {val}")
    print(f"==========================================")
    
    while True:
        try:
            choice = input("Approve? (y/n): ").strip().lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            print("Please enter 'y' or 'n'.")
        except EOFError:
            # Handle non-interactive console contexts
            print("[ERROR] Stdin is not interactive (EOF). Auto-rejecting action.")
            return False

@app.post("/append_to_doc")
def handle_append_to_doc(req: DocAppendRequest):
    payload = {
        "doc_id": req.doc_id,
        "content": req.content
    }
    
    # Block and wait for console confirmation
    if not ask_approval("append_to_doc", payload):
        raise HTTPException(status_code=403, detail="Action rejected by user confirmation.")
        
    try:
        result = append_to_doc(req.doc_id, req.content)
        return {
            "status": "success",
            "message": "Successfully appended content to Google Doc",
            "data": result
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create_email_draft")
def handle_create_email_draft(req: EmailDraftRequest):
    payload = {
        "to": req.to,
        "subject": req.subject,
        "body": req.body
    }
    
    # Block and wait for console confirmation
    if not ask_approval("create_email_draft", payload):
        raise HTTPException(status_code=403, detail="Action rejected by user confirmation.")
        
    try:
        result = create_email_draft(req.to, req.subject, req.body)
        return {
            "status": "success",
            "message": "Successfully created email draft",
            "data": result
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gmail_send_message")
def handle_gmail_send_message(req: EmailSendRequest):
    payload = {
        "to": req.to,
        "subject": req.subject,
        "body": req.body
    }
    
    # Block and wait for console confirmation
    if not ask_approval("gmail_send_message", payload):
        raise HTTPException(status_code=403, detail="Action rejected by user confirmation.")
        
    try:
        result = gmail_send_message(req.to, req.subject, req.body)
        return {
            "status": "success",
            "message": "Successfully sent email message",
            "data": result
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send_email")
def handle_send_email(req: EmailSendRequest):
    payload = {
        "to": req.to,
        "subject": req.subject,
        "body": req.body
    }
    
    # Block and wait for console confirmation
    if not ask_approval("send_email", payload):
        raise HTTPException(status_code=403, detail="Action rejected by user confirmation.")
        
    try:
        result = gmail_send_message(req.to, req.subject, req.body)
        return {
            "status": "success",
            "message": "Successfully sent email message",
            "data": result
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    # reload=False is important, as reload subprocesses in Uvicorn
    # typically detach standard input, causing EOFError when prompting input().
    uvicorn.run("server:app", host=host, port=port, reload=False)
