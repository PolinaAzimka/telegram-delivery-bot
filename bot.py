
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Get token from environment variable
TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправьте мне ссылки на товары, и я помогу рассчитать стоимость доставки.")

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    urls = update.message.text.split()
    await update.message.reply_text(f"Я обработаю следующие ссылки: {', '.join(urls)}")

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))

    logging.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
