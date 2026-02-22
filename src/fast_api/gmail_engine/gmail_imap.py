import imaplib
import email
from email.utils import parseaddr
import os

import os

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

KEYWORDS = [
    "donot_reply",
    "dont_reply",
    "support",
    "all-students",
    "iitm bs",
    "support@study.iitm.ac.in"
]

def get_latest_filtered_mails(limit=20):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, APP_PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, "ALL")
    all_ids = messages[0].split()

    mail_ids = all_ids[-limit:][::-1]  # latest first

    collected_messages = []

    for mail_id in mail_ids:
        status, msg_data = mail.fetch(mail_id, "(RFC822)")

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                sender = msg.get("From")
                subject = msg.get("Subject")

                if sender:
                    name, email_addr = parseaddr(sender)

                    email_addr = email_addr.lower()
                    name = name.lower()

                    if any(k.lower() in email_addr or k.lower() in name for k in KEYWORDS):

                        body = ""

                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode(errors="ignore")
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode(errors="ignore")

                        clean_body = " ".join(body.strip().split())[:700]

                        formatted = (
                            f"📩 IITM BS UPDATE %0A"
                            f"📌 {subject}\n\n"
                            f"From: {email_addr}\n\n"
                            f"{clean_body}"
                        )

                        collected_messages.append({
                            "from": email_addr,
                            "subject": subject,
                            "body": clean_body
                        })
                        break

    mail.logout()

    return collected_messages