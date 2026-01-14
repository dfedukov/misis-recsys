"""
Bot Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
FAQ_JSON_PATH = os.getenv("FAQ_JSON_PATH", "faq.json")
FAQ_INDEX_PATH = os.getenv("FAQ_INDEX_PATH", "data/faq_index")
