import os
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv('LLM_API_KEY', 'placeholder_api_key')
LLM_ENDPOINT = os.getenv('LLM_ENDPOINT', 'https://api.openai.com/v1/chat/completions')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')