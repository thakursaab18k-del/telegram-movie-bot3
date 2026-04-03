import os
import threading
from flask import Flask, jsonify
from telegram.ext import ApplicationBuilder, CommandHandler

# --- Flask Web Server Setup ---
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return jsonify({"status": "Movie Bot is running successfully!"})

def run_flask():
    # Render assigns a port dynamically via the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Telegram Bot Setup ---
async def start(update, context):
    await update.message.reply_text("🎬 Movie Bot v1.0\n/movie <name>")

def main():
    TOKEN = os.getenv("TOKEN")
    
    if not TOKEN:
        print("⚠️ No TOKEN found! Please set it in Render Environment Variables.")
        # We still start Flask so Render doesn't crash the deployment immediately, 
        # allowing you to check logs and fix the env var.
        run_flask() 
        return

    print("✅ TOKEN OK")

    # 1. Start the Flask server in a separate background thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True # Ensures the thread closes when the bot stops
    flask_thread.start()

    # 2. Start the Telegram Bot
    try:
        application = ApplicationBuilder().token(TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        
        print("🚀 Bot ready and polling...")
        # run_polling blocks the main thread, which is fine because Flask is on another thread
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Bot error: {e}")

if __name__ == '__main__':
    main()
