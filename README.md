# 📬 Mail AI Agent

A Python-based MCP (Model Context Protocol) server that reads credit card transaction emails from Gmail using IMAP, extracts transaction data via OpenAI, and surfaces it to Claude as a tool — enabling Claude to read, summarize, and update your Google Sheets with spend data automatically.

---

## 🧠 How It Works

1. **`read_mail.py`** connects to Gmail via IMAP, scans unread emails from known credit card senders (HDFC, ICICI, RBL, Scapia, Axis), extracts the email body, and sends it to OpenAI to parse transaction details (date, amount, bank, merchant).
2. **`cc_mail_agent.py`** wraps that logic as an MCP tool called `summarize_my_emails`, which Claude can invoke directly during a conversation.
3. **Claude (via claude.ai)** calls the tool, receives the transaction table, and can then update your Google Sheets using the Google Sheets MCP connector.

---

## 🗂️ Project Structure

```
mail_ai_agent/
├── cc_mail_agent.py      # MCP server exposing the email tool to Claude
├── read_mail.py          # Gmail IMAP reader + OpenAI parser
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (not committed)
```

---

## ⚙️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/vatsalkhanna1992/mail_ai_agent.git
cd mail_ai_agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
GMAIL_USER=your_gmail_address@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
OPENAI_API_KEY=your_openai_api_key
```

#### Getting your Gmail App Password

Gmail does **not** allow direct password login for IMAP. You need an App Password:

1. Enable **2-Step Verification** on your Google account:
   👉 https://myaccount.google.com/signinoptions/two-step-verification
2. Generate an **App Password**:
   👉 https://myaccount.google.com/apppasswords
3. Select app: **Mail**, device: **Other (custom name)** → copy the 16-character password (no spaces).
4. Paste it as `GMAIL_APP_PASSWORD` in your `.env`.

#### Getting your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create a new secret key and paste it as `OPENAI_API_KEY` in your `.env`.

---

## 🔌 Connecting to Claude as an MCP Tool

This project runs as a local MCP server that Claude connects to. To register it with Claude:

### 1. Run the MCP Server

```bash
python cc_mail_agent.py
```

This starts the MCP server locally.

### 2. Register with Claude Desktop / claude.ai

In your Claude MCP configuration (typically `claude_desktop_config.json`), add:

```json
{
  "mcpServers": {
    "cc-mail-agent": {
      "command": "python",
      "args": ["/absolute/path/to/mail_ai_agent/cc_mail_agent.py"]
    }
  }
}
```

Once registered, Claude will have access to the `summarize_my_emails` tool and can call it during conversations.

---

## 🔗 Connecting Google Sheets in Claude

To allow Claude to read and update your Google Sheets:

1. Go to **claude.ai → Settings → Integrations**
2. Find **Google Sheets** and click **Connect**
3. Authenticate with your Google account and grant the required permissions
4. Claude will now be able to list, read, and update your spreadsheets directly in conversation

> Once connected, you can ask Claude things like:
> *"Fetch my Feb-Mar credit card spends from the Monthly Spends sheet and update the totals."*

---

## 💳 Supported Credit Card Senders

The agent currently recognises transaction alert emails from:

| Bank | Sender Email |
|------|-------------|
| Scapia (Federal Bank) | `scapiacards@federalbank.co.in` |
| HDFC Bank | `alerts@hdfcbank.bank.in` |
| Axis Bank | `alerts@axis.bank.in` |
| RBL Bank | `RBLAlerts@rbl.bank.in` |
| ICICI Bank | `credit_cards@icicibank.com` |

To add more banks, update the `data_mapping` dictionary in `read_mail.py`.

---

## 📦 Requirements

See `requirements.txt`. Key dependencies:

- `mcp` — MCP server framework
- `openai` — OpenAI API client
- `html2text` — HTML to plain text conversion
- `python-dotenv` — Environment variable loader
- `imaplib` / `email` — Built-in Python libraries for Gmail IMAP

---

## 🔒 Security Notes

- **Never commit your `.env` file.** It is already listed in `.gitignore`.
- Always use Gmail App Passwords — never your actual Gmail password.
- Your OpenAI API key should be kept private.
