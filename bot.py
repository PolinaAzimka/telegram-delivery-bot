
import os
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Получение токена из переменных окружения
TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Настройки доставки
FIRST_KG_COST = int(os.getenv("FIRST_KG_COST", 3000))
ADDITIONAL_HALF_KG_COST = int(os.getenv("ADDITIONAL_HALF_KG_COST", 1000))
VOLUME_WEIGHT_DIVISOR = int(os.getenv("VOLUME_WEIGHT_DIVISOR", 5000))

# Логирование
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправьте мне ссылки на товары, и я помогу рассчитать стоимость доставки.")

async def process_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    urls = update.message.text.split()
    response_message = "Я обработаю следующие ссылки:\n"
    total_weight = 0

    for url in urls:
        weight = parse_product(url)
        if weight:
            total_weight += weight
            response_message += f"{url} - {weight} кг\n"
        else:
            response_message += f"{url} - Не удалось получить данные\n"

    total_cost = calculate_delivery_cost(total_weight)
    response_message += f"Общий вес: {total_weight:.2f} кг\nСтоимость доставки: {total_cost} йен"
    await update.message.reply_text(response_message)

def parse_product(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Пример извлечения данных (нужно адаптировать под разные сайты)
            weight_tag = soup.find("span", class_="product-weight")
            if weight_tag:
                weight = float(weight_tag.text.strip().replace("kg", "").replace(",", "."))
                return weight
            else:
                return None
        else:
            return None
    except Exception as e:
        logging.error(f"Ошибка при обработке {url}: {e}")
        return None

def calculate_delivery_cost(weight_kg):
    if weight_kg <= 1:
        return FIRST_KG_COST
    else:
        additional_weight = (weight_kg - 1) * 2  # Учитываем 0.5 кг шаги
        return FIRST_KG_COST + (additional_weight * ADDITIONAL_HALF_KG_COST)

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_links))

    logging.info("Бот запущен и ожидает сообщения...")
    application.run_polling()

if __name__ == "__main__":
    main()
