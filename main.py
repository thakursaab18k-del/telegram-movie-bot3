import os
import threading
import requests
from flask import Flask, jsonify
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# --- Flask Setup ---
app = Flask(__name__)

@app.route('/')
def health():
    return "Bot is alive! 🚀"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Movie Logic ---
def clean_query(query):
    # This removes common extra words that break OMDb searches
    tags_to_remove = ["movie", "south", "film", "full", "hindi", "dubbed", "latest"]
    words = query.lower().split()
    cleaned_words = [w for w in words if w not in tags_to_remove]
    return " ".join(cleaned_words)

async def fetch_movie_omdb(update: Update, user_input: str):
    api_key = "46111cc1"
    query = clean_query(user_input)
    
    # Use 't' for direct match details
    url = f"http://www.omdbapi.com/?t={query}&apikey={api_key}"
    response = requests.get(url).json()

    if response.get("Response") == "False":
        await update.message.reply_text("❌ *Movie not found!*\nTry searching with just the main title.", parse_mode=ParseMode.MARKDOWN)
        return

    title = response.get("Title")
    year = response.get("Year")
    rating = response.get("imdbRating")
    genre = response.get("Genre")
    plot = response.get("Plot")
    poster = response.get("Poster")

    # Cool UI: Trailer link and a search link for more info
    trailer_url = f"https://www.youtube.com/results?search_query={title.replace(' ', '+')}+trailer"
    imdb_url = f"https://www.imdb.com/title/{response.get('imdbID')}/"

    text = (
        f"🎬 *{title}* ({year})\n\n"
        f"⭐ *Rating:* {rating}/10\n"
        f"🎭 *Genre:* {genre}\n\n"
        f"📝 {plot}"
    )

    keyboard = [
        [
            InlineKeyboardButton("▶️ Watch Trailer", url=trailer_url),
            InlineKeyboardButton("ℹ️ IMDb", url=imdb_url)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if poster != "N/A":
        await update.message.reply_photo(
            photo=poster,
            caption=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    
    # Welcome Photo (Change this URL to any image you like)
    welcome_photo = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=1000"
    
    welcome_text = (
        f"👋 *Hey {user_name}!* \n\n"
        "Welcome to your 🎬 *Movie Scout*.\n\n"
        "Just send me a movie name and I'll find the details for you! 🍿"
    )

    await update.message.reply_photo(
        photo=welcome_photo,
        caption=welcome_text,
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_movie_omdb(update, update.message.text)

# --- Main Function ---
def main():
    TOKEN = os.getenv("TOKEN")
    if not TOKEN:
        print("⚠️ No TOKEN found!")
        return

    # Start Flask thread
    threading.Thread(target=run_flask, daemon=True).start()

    app_bot = ApplicationBuilder().token(TOKEN).build()

    app_bot.add_handler(CommandHandler("start", start))
    # This catches ANY text message and treats it as a search
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Movie Bot (OMDb) is LIVE!")
    # drop_pending_updates=True prevents the "Conflict" error on restart
    app_bot.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
