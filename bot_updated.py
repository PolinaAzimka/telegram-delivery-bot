
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

# Справочник стандартных весов с учетом упаковки (в кг) на японском языке
standard_weights = {
    "ブレザー": 1.0,  # Blazer
    "コート": 1.5,  # Coat
    "ドレス": 0.5,  # Dress
    "パンツ": 0.6,  # Pants
    "シャツ": 0.4,  # Shirt
    "スカート": 0.4,  # Skirt
    "スーツ": 1.2,  # Suit
    "セーター": 0.5,  # Sweater
    "Tシャツ": 0.3,  # T-shirt
    "スニーカー": 1.0,  # Sneakers
    "ジャージ": 0.6,  # Tracksuit
    "ショーツ": 0.3,  # Shorts
    "スポーツブラ": 0.2,  # Sports Bra
    "ランニングシューズ": 0.9,  # Running Shoes
    "パーカー": 0.7,  # Hoodie
    "レギンス": 0.4,  # Leggings
    "化粧水": 0.5,  # Lotion
    "乳液": 0.4,  # Emulsion
    "美容液": 0.3,  # Serum
    "文房具": 0.2,  # Stationery
    "家具": 10.0,  # Furniture
    "収納用品": 2.0,  # Storage
    "ブラジャー": 0.2,  # Bra
    "ガードル": 0.3,  # Girdle
    "手帳": 0.3,  # Planner
    "カバー": 0.2,  # Cover
}

# Логирование
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("こんにちは！ 商品のリンクを送信してください。送料を計算するのをお手伝いします。")

async def process_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    urls = update.message.text.split()
    response_message = "次のリンクを処理します:\n"
    total_weight = 0

    for url in urls:
        weight = parse_product(url)
        if weight:
            total_weight += weight
            response_message += f"{url} - {weight} kg\n"
        else:
            response_message += f"{url} - データが見つかりません、標準重量を使用します。\n"

    total_cost = calculate_delivery_cost(total_weight)
    response_message += f"合計重量: {total_weight:.2f} kg\n送料: {total_cost} 円"
    await update.message.reply_text(response_message)

def parse_product(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.text.lower()
                for keyword, weight in standard_weights.items():
                    if keyword in title:
                        return weight
            return None
        else:
            return None
    except Exception as e:
        logging.error(f"エラー {url}: {e}")
        return None

def calculate_delivery_cost(weight_kg):
    if weight_kg <= 1:
        return FIRST_KG_COST
    else:
        additional_weight = (weight_kg - 1) * 2  # 0.5 kg単位で計算
        return FIRST_KG_COST + (additional_weight * ADDITIONAL_HALF_KG_COST)

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_links))

    logging.info("ボットが開始されました。メッセージを待っています...")
    application.run_polling()

if __name__ == "__main__":
    main()
