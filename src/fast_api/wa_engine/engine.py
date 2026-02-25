from seleniumbase import SB
import os
from gmail_engine import gmail_imap



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
session_path = os.path.join(BASE_DIR, "sessions", "number1")


import os
from datetime import datetime

def login():
    with SB(browser="chrome", user_data_dir=session_path, headless=True) as sb:
        sb.open("https://web.whatsapp.com")

        try:
            sb.wait_for_element("div[role='grid']", timeout=20)
            print("✅ Already logged in")
            return "Already logged in"

        except Exception:
            print("❌ Not logged in. Waiting for QR...")

            sb.wait_for_element("canvas", timeout=240)

            # Create unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"qr_{timestamp}"

            sb.save_screenshot(name=filename, folder="wa_qr")

            file_path = os.path.join("wa_qr", f"{filename}.png")

            print("📸 QR Screenshot saved:", file_path)

            # 🔥 SEND EMAIL HERE
            try:
                # 🔥 SEND EMAIL
                gmail_imap.send_email_with_attachment(
                    to_email="muhammedsinankallayi7009@gmail.com",
                    subject="WhatsApp Login QR",
                    body="Scan this QR to login to WhatsApp Web.",
                    attachment_path=file_path
                )
                print("📧 Email sent successfully")

            finally:
                # 🔥 DELETE QR IMAGE
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print("🗑 QR image deleted")

            sb.wait_for_element("div[role='grid']", timeout=300)

            print("✅ Login completed")
            return "Login successful"
def send_message(to_phone, msgfrom, msgsub, msgcontext):
    with SB(browser="chrome", user_data_dir=session_path, headless=True) as sb:
        phone = to_phone  # with country code

        url = f"https://web.whatsapp.com/send?phone={phone}&text=📩 IITM BS Gmail*%0A%0A📌*{msgsub}*%0A%0AFrom:{msgfrom}%0A%0A%0A{msgcontext}"
        sb.open(url)

        sb.sleep(5)
        sb.wait_for_element("span[data-icon='wds-ic-send-filled']", timeout=240)
        sb.click("span[data-icon='wds-ic-send-filled']")
        sb.sleep(5)

        print("Message sent!")
        return {"status": "sent", "to": to_phone, "message": msgfrom}





# Ensure session folder exists
os.makedirs(session_path, exist_ok=True)

if __name__ == "__main__":
    if not os.listdir(session_path):
        print("❌ No session found. Please login.")
        login()
    else:
        print("✅ Session folder exists.")
        # Example test message
        send_message("1234567890", "Hello World")
