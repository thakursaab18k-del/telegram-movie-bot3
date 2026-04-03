import os
import threading
import requests
from flask import Flask, jsonify
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)

# --- Flask Setup ---
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return jsonify({"status": "Movie Bot running 🎬"})

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Start Command ---
async def start(update, context):
    await update.message.reply_text(
        "🎬 Movie Bot\n\nSend movie name or use:\n/movie <name>"
    )

# --- Movie Fetch Function ---
async def fetch_movie(update, movie_name):
    api_key = "46111cc1"

    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={api_key}"
    response = requests.get(url).json()

    if response.get("Response") == "False":
        await update.message.reply_text("❌ Movie not found!")
        return

    title = response.get("Title")
    year = response.get("Year")
    rating = response.get("imdbRating")
    genre = response.get("Genre")
    plot = response.get("Plot")
    poster = response.get("Poster")

    trailer_url = f"https://www.youtube.com/results?search_query={title}+trailer"

    text = f"""🎬 *{title}* ({year})

⭐ Rating: {rating}/10
🎭 Genre: {genre}

📝 {plot}
"""

    keyboard = [
        [InlineKeyboardButton("▶️ Watch Trailer", url=trailer_url)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if poster != "N/A":
        await update.message.reply_photo(
            photo=poster,
            caption=text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

# --- /movie command ---
async def movie(update, context):
    if not context.args:
        await update.message.reply_text("❗ Usage: /movie <name>")
        return

    movie_name = " ".join(context.args)
    await fetch_movie(update, movie_name)

# --- Auto message handler ---
async def auto_movie(update, context):
    movie_name = update.message.text
    await fetch_movie(update, movie_name)

# --- Main Function ---
def main():
    TOKEN = os.getenv("TOKEN")

    if not TOKEN:
        print("⚠️ No TOKEN found!")
        return

    # Run Flask in background
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Telegram Bot
    app_bot = ApplicationBuilder().token(TOKEN).build()

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("movie", movie))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_movie))

    print("🚀 Bot running...")
    app_bot.run_polling()

if __name__ == "__main__":
    main()