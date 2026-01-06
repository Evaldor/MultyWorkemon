import os
from dotenv import load_dotenv

load_dotenv()

YANDEX_IMAP_HOST = os.getenv('YANDEX_IMAP_HOST', 'imap.yandex.com')
YANDEX_SMTP_HOST = os.getenv('YANDEX_SMTP_HOST', 'smtp.yandex.com')
YANDEX_EMAIL = os.getenv('YANDEX_EMAIL', 'placeholder@yandex.com')
YANDEX_PASSWORD = os.getenv('YANDEX_PASSWORD', 'placeholder_password')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'placeholder_token')

AI_SECRETARY_URL = os.getenv('AI_SECRETARY_URL', 'http://ai-secretary:8000')