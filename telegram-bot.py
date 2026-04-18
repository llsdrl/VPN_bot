from flask import Flask, request
import os
import traceback
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Bot, CommandHandler, CallbackQueryHandler

app = Flask(__name__)

TOKEN = "8749332624:AAGYZevZVbF3f2lbOI8oUC_RnhCIv0uJRV8"

print("Creating bot...")
bot = Bot(token=TOKEN)
print("Bot created!")

tariffs = {
    "1month": {"name": "📅 1 месяц", "price": "109₽", "period": "1 месяц", "desc": "Для тестирования"},
    "3month": {"name": "📅 3 месяца", "price": "290₽", "period": "3 месяца", "savings": "Скидка 11%", "desc": "Оптимально"},
    "6month": {"name": "📅 6 месяцев", "price": "530₽", "period": "6 месяцев", "savings": "Скидка 19%", "desc": "Лучшая цена"}
}

ADMIN_CHAT_ID = None

async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("🔐 Подключить VPN", callback_data="tariffs")],
        [InlineKeyboardButton("ℹ️ Информация", callback_data="info")],
        [InlineKeyboardButton("🛠 Техподдержка", callback_data="support")],
        [InlineKeyboardButton("📊 Мой статус", callback_data="status")]
    ]
    await update.message.reply_text(
        "🔒 *Приватный VPN*\n\n• Обход блокировок\n• Скорость до 1 Гбит/с\n• 50+ стран\n• Без логов\n\nВыберите раздел:",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

async def button_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "tariffs":
        keyboard = [
            [InlineKeyboardButton("📅 1 месяц - 109₽", callback_data="tariff_1month")],
            [InlineKeyboardButton("📅 3 месяца - 290₽", callback_data="tariff_3month")],
            [InlineKeyboardButton("📅 6 месяцев - 530₽", callback_data="tariff_6month")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ]
        await query.edit_message_text("🔐 *Тарифы*\n\n⚡ До 1 Гбит/с\n🌍 50+ стран\n🔒 Безлимит", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "info":
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back")]]
        await query.edit_message_text("ℹ️ *Информация*\n\n🔒 Шифрование: WireGuard\n🌐 Протокол: WireGuard\n📍 Стран: 50+\n\n📊 *Подписка:* Не активна", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "support":
        keyboard = [[InlineKeyboardButton("💬 Написать", url="https://t.me/llsdrl")], [InlineKeyboardButton("🔙 Назад", callback_data="back")]]
        await query.edit_message_text("🛠 *Техподдержка*\n\n📱 @llsdrl\n⏰ 24/7", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "status":
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back")]]
        await query.edit_message_text("📊 *Статус*\n\n🔐 VPN: Не активна\n📋 Тариф: Не выбран", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "back":
        keyboard = [
            [InlineKeyboardButton("🔐 Подключить VPN", callback_data="tariffs")],
            [InlineKeyboardButton("ℹ️ Информация", callback_data="info")],
            [InlineKeyboardButton("🛠 Техподдержка", callback_data="support")],
            [InlineKeyboardButton("📊 Мой статус", callback_data="status")]
        ]
        await query.edit_message_text("🔒 *Приватный VPN*\n\n• Обход блокировок\n• Скорость до 1 Гбит/с\n• 50+ стран\n\nВыберите раздел:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data.startswith("tariff_"):
        key = data.split("_")[1]
        t = tariffs[key]
        savings = f"\n💎 {t['savings']}" if "savings" in t else ""
        keyboard = [[InlineKeyboardButton("💳 Оплатить", callback_data=f"select_{key}")], [InlineKeyboardButton("🔙 К тарифам", callback_data="tariffs")]]
        await query.edit_message_text(f"{t['name']}\n\n💰 *Цена:* {t['price']}\n⏱ *Период:* {t['period']}{savings}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data.startswith("select_"):
        key = data.split("_")[1]
        t = tariffs[key]
        user = query.from_user
        username = f"@{user.username}" if user.username else "нет"
        if ADMIN_CHAT_ID:
            await bot.send_message(ADMIN_CHAT_ID, f"🛒 Заявка!\n👤 {user.first_name}\n🔗 {username}\n📋 {t['name']}\n💰 {t['price']}")
        await query.edit_message_text(f"✅ *Заявка отправлена!*\n\nТариф: {t['name']}\nЦена: {t['price']}\n\n📱 @llsdrl", parse_mode="Markdown")

async def setadmin(update: Update, context):
    global ADMIN_CHAT_ID
    ADMIN_CHAT_ID = update.message.chat_id
    await update.message.reply_text(f"✅ Admin: {ADMIN_CHAT_ID}")

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    try:
        update = Update.de_json(request.get_json(), bot)
        if update.message and update.message.text == "/start":
            await start(update, None)
        elif update.message and update.message.text == "/setadmin":
            await setadmin(update, None)
        elif update.callback_query:
            await button_callback(update, None)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    return "OK"

@app.route("/health")
def health():
    return "OK"

@app.route("/")
def index():
    return "VPN Bot Running"

if __name__ == "__main__":
    print("Starting Flask...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))