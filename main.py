from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import os
import threading
from flask import Flask

TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY") or "46111cc1"

if not TOKEN:
    print("❌ TOKEN missing!")
    exit(1)

cache = {}

# Flask app
app = Flask(__name__)

@app.route("/")
@app.route("/health")
def home():
    return {"status": "Bot running!", "cache_size": len(cache)}

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# Bot functions (same as before)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Welcome! Send movie name 😊")

def get_movie(movie_name):
    movie_name = movie_name.lower().strip()
    if movie_name in cache:
        return cache[movie_name]
    
    encoded = requests.utils.quote(movie_name)
    url = f"http://www.omdbapi.com/?t={encoded}&apikey={API_KEY}"
    
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        cache[movie_name] = data
        return data
    except:
        return None

# ... (rest same, but shorter for now)

print("🤖 Movie Bot Starting...")
application = ApplicationBuilder().token(TOKEN).build()
application.run_polling(drop_pending_updates=True)