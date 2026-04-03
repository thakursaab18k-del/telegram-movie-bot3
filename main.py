import os
from flask import Flask
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("❌ TOKEN missing!")
    exit(1)

app = Flask(__name__)

@app.route("/")
@app.route("/health")
def home():
    return {"status": "Movie Bot Ready!", "token_ok": True}

print("✅ Starting Movie Bot...")

# Create application
application = Application.builder().token(TOKEN).build()

async def start(update, context):
    await update.message.reply_text("🎬 Movie Bot Ready!\nSend movie name!")

application.add_handler(CommandHandler("start", start))
print("🚀 Bot handlers added!")

# Run bot
print("🔄 Starting polling...")
application.run_polling(drop_pending_updates=True)