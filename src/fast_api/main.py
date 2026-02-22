from fastapi import FastAPI
from pydantic import BaseModel
from wa_engine.engine import send_message, login
from gmail_engine.gmail_imap import get_latest_filtered_mails
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager


scheduler = BackgroundScheduler()


class MessageRequest(BaseModel):
    to_phone: int


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    if not scheduler.running:
        scheduler.start()
        print("Scheduler started")

    yield  # App runs here

    # Shutdown
    scheduler.shutdown()
    print("Scheduler stopped")

app = FastAPI(lifespan=lifespan)



@app.get("/")
def root():
    return {"hello": "world"}


@app.post("login")
def wa_login():
    response = login()
    return response


@app.post("/send-message")
def send_message_endpoint(request: MessageRequest):
    messages = get_latest_filtered_mails()
    responses = []
    if not messages:
        return {"status": "No matching emails found"}

    for msg in messages:
        response = send_message(
            request.to_phone,
            msg["from"],
            msg["subject"],
            msg["body"]
        )
        responses.append(response)

    return {"sent_count": len(responses), "responses": responses}


def auto_send_messages():
    messages = get_latest_filtered_mails()

    if not messages:
        print("No matching emails found")
        return

    for msg in messages:
        send_message(
            919895676101,  # set your fixed number here
            msg["from"],
            msg["subject"],
            msg["body"]
        )
    print("Auto messages sent")


scheduler.add_job(auto_send_messages, "interval", minutes=60)



