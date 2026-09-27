import os
import sys

# Ensure root directory and google-mcp-server package directory are in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

GOOGLE_MCP_DIR = os.path.join(ROOT_DIR, "google-mcp-server")
if os.path.exists(GOOGLE_MCP_DIR) and GOOGLE_MCP_DIR not in sys.path:
    sys.path.insert(0, GOOGLE_MCP_DIR)

try:
    from server import app
except ImportError:
    from google_mcp_server.server import app

# Vercel ASGI serverless handler
app = app
