import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_IS_ENABLED = os.getenv('EMAIL_IS_ENABLED', 'False')
IMAP_HOST = os.getenv('IMAP_HOST', 'imap.yandex.com')
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.yandex.com')
EMAIL = os.getenv('EMAIL', 'placeholder@yandex.com')
PASSWORD = os.getenv('PASSWORD', 'placeholder_password')

TELEGRAM_IS_ENABLED = os.getenv('TELEGRAM_IS_ENABLED', 'False')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'placeholder_token')

AI_SECRETARY_URL = os.getenv('AI_SECRETARY_URL', 'http://ai-secretary:8000')