from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import os
import threading
from flask import Flask

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("❌ Add TOKEN environment variable!")
    exit(1)

cache = {}

# Flask App for Render
app = Flask(__name__)

@app.route("/")
@app.route("/health")
def home():
    return {"status": "Movie Bot Live!", "movies_cached": len(cache)}

# Start web server
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# Bot Functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Movie Bot!\nSend movie name or /movie <name>")

def get_movie(name):
    name = name.lower().strip()
    if name in cache: return cache[name]
    
    try:
        url = f"http://www.omdbapi.com/?t={requests.utils.quote(name)}&apikey={os.getenv('API_KEY', '46111cc1')}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        cache[name] = data
        return data
    except:
        return None

async def send_movie(update: Update, name):
    await update.message.chat.send_action("typing")
    data = get_movie(name)
    
    if not data or data.get("Response") != "True":
        await update.message.reply_text("❌ Movie not found!")
        return
    
    title = data.get("Title")
    rating = data.get("imdbRating", "N/A")
    year = data.get("Year")
    poster = data.get("Poster")
    
    caption = f"🎬 <b>{title}</b>\n⭐ {rating}\n📅 {year}"
    
    kb = [[InlineKeyboardButton("Trailer", f"https://youtube.com/results?search_query={requests.utils.quote(title+' trailer')}")]]
    markup = InlineKeyboardMarkup(kb)
    
    try:
        if poster and poster.startswith('http'):
            await update.message.reply_photo(poster, caption=caption, reply_markup=markup, parse_mode='HTML')
        else:
            await update.message.reply_text(caption, reply_markup=markup, parse_mode='HTML')
    except:
        await update.message.reply_text(f"{title} ⭐{rating} ({year})")

async def movie_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = " ".join(context.args)
    if not name:
        await update.message.reply_text("Usage: /movie <name>")
        return
    await send_movie(update, name)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if len(text) > 2 and not text.startswith('/'):
        await send_movie(update, text)

# Start Bot
print("🤖 Movie Bot Starting...")
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("movie", movie_cmd))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("🚀 Bot Live!")
application.run_polling(drop_pending_updates=True)