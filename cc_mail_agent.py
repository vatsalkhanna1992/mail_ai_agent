from mcp.server.fastmcp import FastMCP
import read_mail

# 1. Initialize the MCP server
mcp = FastMCP("Credit Card Transaction Summarizer")

# 2. Define the tool Claude will see
@mcp.tool()
def summarize_my_emails(count: int = 5):
    """Fetches the credit card transaction emails and returns a summary."""
    # Place your existing logic here
    summary = read_mail.main_fn()
    return summary

if __name__ == "__main__":
    mcp.run()