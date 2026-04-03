import os
from flask import Flask
from telegram.ext import ApplicationBuilder

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("❌ ERROR: TOKEN environment variable missing!")
    exit(1)

app = Flask(__name__)

@app.route("/")
@app.route("/health")
def home():
    return {"status": "Movie Bot OK", "token_set": bool(TOKEN)}

print("✅ TOKEN found, starting bot...")
app = ApplicationBuilder().token(TOKEN).build()
print("🚀 Bot started!")
app.run_polling(drop_pending_updates=True)