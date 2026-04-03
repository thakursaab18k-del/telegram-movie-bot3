import os
from flask import Flask

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("❌ No TOKEN!")
    exit(1)

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def home():
    return {'status': 'Movie Bot OK'}

print("✅ Bot starting...")

from telegram.ext import ApplicationBuilder
application = ApplicationBuilder().token(TOKEN).build()

async def start(update, context):
    await update.message.reply_text('🎬 Movie Bot! Use /movie <name>')

async def movie(update, context):
    title = ' '.join(context.args)
    if not title:
        await update.message.reply_text('/movie <name>')
        return
    await update.message.reply_text(f'🔍 Searching {title}...')

application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('movie', movie))

print("🚀 Bot live!")
application.run_polling(drop_pending_updates=True)