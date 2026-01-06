import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/multyworkemon')
AI_GUESSER_URL = os.getenv('AI_GUESSER_URL', 'http://ai-guesser:8001')
AI_SYSTEMANALITIC_URL = os.getenv('AI_SYSTEMANALITIC_URL', 'http://ai-systemanalitic:8002')