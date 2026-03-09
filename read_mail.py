import imaplib
import email
import os
import html2text
from dotenv import load_dotenv

def get_data_from_ai(body: str):
    from openai import OpenAI
    client = OpenAI()
    prompt = f"""
      Here are the mail body for the expenses made on the Credit Card in HTML format provided by bank. Can you fetch the amount spent on the Credit Card, bank name and the date of the transaction from this? Make sure to fetch the amount in ₹ and the date in the format of DD-MM-YYYY, also add them in table. The table should have the following columns: Date, Amount, Bank Name, Transaction Type and To/From.

      {body}
    """
    response = client.responses.create(
        model="gpt-5.4",
        input=prompt
    )

    first_table = response.output_text
    # print(first_table)
    return first_table

    # Second prompt in reference to the first: use the previous response as context
    # follow_up_prompt = f"""
    #     Here is the table from the previous step:

    #     {first_table}

    #     From the above table, can you do total of the amount with same bank name and show it in a single table?
    # """
    # response = client.responses.create(
    #     model="gpt-5.4",
    #     input=follow_up_prompt
    # )
    # print(response.output_text)

def _html_to_text(html: str) -> str:
    """Convert HTML to plain text."""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0  # don't wrap lines
    return h.handle(html).strip()

def get_email_body(msg):
    """Extract plain-text body from an email message (handles multipart and encoding)."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                try:
                    raw = part.get_payload(decode=True)
                    body = (raw or b"").decode(part.get_content_charset() or "utf-8", errors="replace")
                except Exception:
                    pass
                if body:
                    break
        if not body:
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    try:
                        raw = part.get_payload(decode=True)
                        body = (raw or b"").decode(part.get_content_charset() or "utf-8", errors="replace")
                        # body = _html_to_text(body)
                    except Exception:
                        pass
                    break
    else:
        try:
            raw = msg.get_payload(decode=True)
            body = (raw or b"").decode(msg.get_content_charset() or "utf-8", errors="replace")
            # if msg.get_content_type() == "text/html":
            #     body = _html_to_text(body)
        except Exception:
            pass
    return body.strip()

def main_fn():
    load_dotenv()
    # Load credentials from environment (never hardcode!)
    # Set GMAIL_USER and GMAIL_APP_PASSWORD in your shell or .env
    GMAIL_USER = os.environ.get("GMAIL_USER")
    GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        raise SystemExit(
            "Set GMAIL_USER and GMAIL_APP_PASSWORD environment variables. "
            "For Gmail, use an App Password: https://myaccount.google.com/apppasswords"
        )
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    except imaplib.IMAP4.error as e:
        if "Application-specific password" in str(e):
            raise SystemExit(
                "Gmail requires an App Password, not your normal password.\n"
                "1. Enable 2-Step Verification: https://myaccount.google.com/signinoptions/two-step-verification\n"
                "2. Create an App Password: https://myaccount.google.com/apppasswords\n"
                "3. Set GMAIL_APP_PASSWORD in .env to the 16-character password (no spaces)."
            ) from e
        raise
    mail.select("inbox")

    # Search for unread emails
    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()

    data_mapping = {
        "Scapia Federal Credit Card <scapiacards@federalbank.co.in>": "Your transaction was successful",
        "HDFC Bank InstaAlerts <alerts@hdfcbank.bank.in>": "debited via Credit Card",
        "alerts@axis.bank.in <alerts@axis.bank.in>": "spent on credit card",
        "RBL Bank <RBLAlerts@rbl.bank.in>": "Your RBL Bank Credit Card has just been swiped",
        "credit_cards@icicibank.com": "Transaction alert for your ICICI Bank Credit Card",
    }

    # Fetch and print all unread emails
    list = []
    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                from_addr = msg.get("From") or ""
                subject = msg.get("Subject") or ""
                for sender_key, subject_phrase in data_mapping.items():
                    if sender_key in from_addr and subject_phrase in subject:
                        body = get_email_body(msg)
                        list.append(body)
                        break
                # sum_all_data_available()
    data = get_data_from_ai(list)
    mail.logout()
    return data

main_fn()