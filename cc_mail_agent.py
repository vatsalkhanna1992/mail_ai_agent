import os

import uvicorn
from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

import read_mail

# 1. Initialize the MCP server
mcp = FastMCP("Credit Card Transaction Summarizer")

# 2. Define the tool Claude will see
@mcp.tool()
def summarize_my_emails(count: int = 5):
    """Fetches the credit card transaction emails and returns a summary."""
    summary = read_mail.main_fn()
    return summary

# 3. ASGI app with CORS so browser-based MCP Inspector can connect
app = mcp.http_app()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS", "DELETE"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)