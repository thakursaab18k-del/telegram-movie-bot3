from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import os
import threading
from flask import Flask

# 🔐 ENV ONLY
TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY") or "46111cc1"

if not TOKEN:
    raise ValueError("TOKEN environment variable is required!")

cache = {}

# ================== 🌐 WEB SERVER FOR RENDER ==================
flask_app = Flask(__name__)

@flask_app.route("/")
@flask_app.route("/health")
def home():
    return {"status": "Bot is running!", "cache_size": len(cache)}

def run_web():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port, debug=False)

# Start web server
threading.Thread(target=run_web, daemon=True).start()

# ================== 🤖 BOT CODE ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Welcome to Movie Bot 🤖\n\n"
        "Send any movie name or use /movie <name> 😊"
    )

def get_movie(movie_name):
    movie_name = movie_name.lower().strip()
    
    if movie_name in cache:
        return cache[movie_name]

    encoded_name = requests.utils.quote(movie_name)
    url = f"http://www.omdbapi.com/?t={encoded_name}&apikey={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        cache[movie_name] = data
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_watch_links(title):
    query = requests.utils.quote(title.replace(" ", "+"))
    return [
        [InlineKeyboardButton("🔍 Netflix", url=f"https://www.netflix.com/search?q={query}")],
        [InlineKeyboardButton("🔍 Prime Video", url=f"https://www.primevideo.com/search/ref=atv_nb_sr?phrase={query}")],
        [InlineKeyboardButton("🔍 Hotstar", url=f"https://www.hotstar.com/in/search?q={query}")],
        [InlineKeyboardButton("🔍 JustWatch", url=f"https://www.justwatch.com/in/search?q={query}")]
    ]

async def send_movie(update: Update, movie_name):
    await update.message.chat.send_action("typing")
    msg = await update.message.reply_text("🔍 Searching...")
    
    data = get_movie(movie_name)
    await msg.delete()

    if not data:
        await update.message.reply_text("⚠️ Server error!")
        return

    if data.get("Response") == "True":
        title = data.get("Title", "N/A")
        rating = data.get("imdbRating", "N/A")
        year = data.get("Year", "N/A")
        genre = data.get("Genre", "N/A")
        plot = data.get("Plot", "No description")
        poster = data.get("Poster", "")

        caption = f"""🎬 <b>{title}</b>
⭐ <b>Rating:</b> {rating}
📅 <b>Year:</b> {year}
🎭 <b>Genre:</b> {genre}

📝 {plot}"""

        trailer_query = requests.utils.quote(f"{title} trailer")
        trailer_url = f"https://www.youtube.com/results?search_query={trailer_query}"

        keyboard = [
            [InlineKeyboardButton("▶️ Trailer", url=trailer_url)],
            *get_watch_links(title)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            if poster and poster.startswith("http"):
                await update.message.reply_photo(
                    photo=poster, caption=caption, 
                    reply_markup=reply_markup, parse_mode="HTML"
                )
            else:
                await update.message.reply_text(
                    caption, reply_markup=reply_markup,
                    parse_mode="HTML", disable_web_page_preview=True
                )
        except:
            await update.message.reply_text(
                f"🎬 {title}\n⭐ {rating} | 📅 {year}\n🎭 {genre}\n\n{plot}",
                reply_markup=reply_markup
            )
    else:
        await update.message.reply_text("❌ Movie not found")

async def movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_name = " ".join(context.args).strip()
    if not movie_name:
        await update.message.reply_text("📝 /movie <movie name>")
        return
    await send_movie(update, movie_name)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_name = update.message.text.strip()
    if len(movie_name) < 2 or movie_name.startswith('/'):
        return
    await send_movie(update, movie_name)

# ================== 🚀 RUN BOT ==================
print("🤖 Starting Movie Bot...")
application = ApplicationBuilder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("movie", movie))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🚀 Bot running!")
application.run_polling(drop_pending_updates=True)