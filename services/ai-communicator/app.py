import logging_config  # Must be first
import logging
from fastapi import FastAPI
from config import YANDEX_IMAP_HOST, YANDEX_EMAIL, YANDEX_PASSWORD, TELEGRAM_BOT_TOKEN, AI_SECRETARY_URL
import requests
import time
import threading
import imapclient
import email
from telegram import Bot
from telegram.error import TelegramError

app = FastAPI(title="AI-Communicator", version="1.0.0")

logger = logging.getLogger(__name__)

def poll_emails():
    while True:
        try:
            with imapclient.IMAPClient(YANDEX_IMAP_HOST, ssl=True) as client:
                client.login(YANDEX_EMAIL, YANDEX_PASSWORD)
                client.select_folder('INBOX')
                messages = client.search(['UNSEEN'])
                for msgid in messages:
                    raw_message = client.fetch([msgid], ['BODY[]'])
                    email_message = email.message_from_bytes(raw_message[msgid][b'BODY[]'])
                    sender = email_message['From']
                    subject = email_message['Subject']
                    body = ""
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                break
                    else:
                        body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                    
                    request_text = f"Subject: {subject}\n{body}"
                    username = sender.split('@')[0] if '@' in sender else sender
                    
                    params = {
                        "channel": "email",
                        "username": username,
                        "request": request_text,
                        "department": "unknown",  # Placeholder
                        "position": "unknown"
                    }
                    response = requests.get(f"{AI_SECRETARY_URL}/analyze-request", params=params)
                    if response.status_code == 200:
                        logger.info("Processed email", extra={"msgid": msgid, "sender": sender})
                    else:
                        logger.error("Failed to process email", extra={"msgid": msgid, "status": response.status_code})
                    
                    client.add_flags([msgid], [imapclient.SEEN])
        except Exception as e:
            logger.error("Error polling emails", extra={"error": str(e)})
        time.sleep(60)  # Poll every minute

def poll_telegram():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    last_update_id = 0
    while True:
        try:
            updates = bot.get_updates(offset=last_update_id + 1, timeout=30)
            for update in updates:
                if update.message and update.message.text:
                    chat_id = update.message.chat.id
                    username = update.message.from_user.username or str(update.message.from_user.id)
                    request_text = update.message.text
                    
                    params = {
                        "channel": "tg",
                        "username": username,
                        "request": request_text,
                        "department": "unknown",
                        "position": "unknown"
                    }
                    response = requests.get(f"{AI_SECRETARY_URL}/analyze-request", params=params)
                    if response.status_code == 200:
                        logger.info("Processed TG message", extra={"chat_id": chat_id, "username": username})
                    else:
                        logger.error("Failed to process TG message", extra={"chat_id": chat_id, "status": response.status_code})
                
                last_update_id = update.update_id
        except TelegramError as e:
            logger.error("Telegram error", extra={"error": str(e)})
        except Exception as e:
            logger.error("Error polling Telegram", extra={"error": str(e)})
        time.sleep(10)  # Poll every 10 seconds

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=poll_emails, daemon=True).start()
    threading.Thread(target=poll_telegram, daemon=True).start()
    logger.info("Started polling threads")

@app.get("/health")
async def health():
    return {"status": "healthy"}