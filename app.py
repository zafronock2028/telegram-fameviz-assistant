import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ChatMemberHandler, ContextTypes

# Configuración
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
FLOWISE_URL = os.getenv("FLOWISE_URL")

class FlowiseAPI:
    def __init__(self, url):
        self.url = url + "/api/v1/prediction"

    def query(self, question, session_id):
        payload = {
            "question": question,
            "session_id": session_id
        }
        response = requests.post(self.url, json=payload)
        return response.json()["text"]

flowise = FlowiseAPI(FLOWISE_URL)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text
    response = flowise.query(user_text, session_id=str(user_id))
    await update.message.reply_text(f"@{update.effective_user.username or update.effective_user.first_name} 👇\n{response}")

async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        welcome_msg = f"👋 ¡Bienvenido/a {member.first_name} a FameViz!\n\nEscribe *info* para comenzar o pregunta cualquier duda que tengas."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_msg, parse_mode="Markdown")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(ChatMemberHandler(welcome_new_members))
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_url=os.environ.get("WEBHOOK_URL") + BOT_TOKEN
    )
