import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return jsonify({"status": "Movie Bot Starting...", "python": "3.14 compatible"})

TOKEN = os.getenv("TOKEN")
if TOKEN:
    print("✅ TOKEN OK")
else:
    print("⚠️ No TOKEN - bot disabled")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
    exit()

try:
    from telegram.ext import ApplicationBuilder
    application = ApplicationBuilder().token(TOKEN).build()
    
    async def start(update, context):
        await update.message.reply_text("🎬 Movie Bot v1.0\n/movie <name>")
    
    application.add_handler(CommandHandler("start", start))
    print("🚀 Bot ready!")
    application.run_polling(drop_pending_updates=True)
    
except Exception as e:
    print(f"❌ Bot error: {e}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))