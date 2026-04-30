from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TTYAN_CHAT_ID = int(os.getenv("TTYAN_CHAT_ID"))
MELISKIN_ID = int(os.getenv("MELISKIN_ID"))