from seleniumbase import SB
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
session_path = os.path.join(BASE_DIR, "sessions", "number1")


def login():
    with SB(browser="chrome", user_data_dir=session_path, headless=False) as sb:
        sb.open("https://web.whatsapp.com")

        try:
            # If chat grid loads → already logged in
            sb.wait_for_element("div[role='grid']", timeout=20)
            print("✅ Already logged in")
            return "Already logged in"

        except Exception:
            # QR Code page
            print("❌ Not logged in. Please scan QR code.")
            sb.wait_for_element("canvas", timeout=120)
            sb.wait_for_element("div[role='grid']", timeout=120)
            print("✅ Login completed")
            return "Login successful"


def send_message(to_phone, msgfrom, msgsub, msgcontext):
    with SB(browser="chrome", user_data_dir=session_path, headless=True) as sb:
        phone = to_phone  # with country code

        url = f"https://web.whatsapp.com/send?phone={phone}&text=📩 IITM BS Gmail*%0A%0A📌*{msgsub}*%0A%0AFrom:{msgfrom}%0A%0A%0A{msgcontext}"
        sb.open(url)

        sb.sleep(5)
        sb.wait_for_element("span[data-icon='wds-ic-send-filled']", timeout=30)
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
