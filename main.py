from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import os
import threading
from flask import Flask

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("❌ TOKEN required!")
    exit(1)

cache = {}

app = Flask(__name__)

@app.route("/")
@app.route("/health")
def home():
    return {"status": "Movie Bot Live!", "cache": len(cache)}

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Movie Bot! Send movie name")

def get_movie(name):
    name = name.lower().strip()
    if name in cache: return cache[name]
    try:
        url = f"http://www.omdbapi.com/?t={requests.utils.quote(name)}&apikey=46111cc1"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        cache[name] = data
        return data
    except:
        return None

async def send_movie(update: Update, name):
    data = get_movie(name)
    if not data or data.get("Response") != "True":
        await update.message.reply_text("❌ Not found")
        return
    title = data["Title"]
    rating = data.get("imdbRating", "N/A")
    poster = data.get("Poster", "")
    caption = f"🎬 {title}\n⭐ {rating}"
    kb = [[InlineKeyboardButton("Trailer", f"https://youtube.com/results?search_query={title} trailer")]]
    try:
        if poster.startswith('http'):
            await update.message.reply_photo(poster, caption=caption, reply_markup=InlineKeyboardMarkup(kb))
        else:
            await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(kb))
    except:
        await update.message.reply_text(f"{title} ⭐{rating}")

async def movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = " ".join(context.args)
    if name: await send_movie(update, name)
    else: await update.message.reply_text("/movie <name>")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(update.message.text.strip()) > 2:
        await send_movie(update, update.message.text)

print("🤖 Starting...")
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("movie", movie))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
application.run_polling(drop_pending_updates=True)