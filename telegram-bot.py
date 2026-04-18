import asyncio
import logging
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

nest_asyncio.apply()
logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()

tariffs = {
    "1month": {
        "name": "📅 1 месяц",
        "price": "109₽",
        "period": "1 месяц",
        "desc": "Отличный вариант для тестирования"
    },
    "3month": {
        "name": "📅 3 месяца",
        "price": "290₽",
        "period": "3 месяца",
        "savings": "Скидка 11%",
        "desc": "Оптимальный выбор"
    },
    "6month": {
        "name": "📅 6 месяцев",
        "price": "530₽",
        "period": "6 месяцев",
        "savings": "Скидка 19%",
        "desc": "Лучшая цена, максимальная экономия"
    }
}

subscription_info = {
    "status": "Не активна",
    "plan": "Не выбран",
    "expires": "-"
}

ADMIN_CHAT_ID = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Подключить VPN", callback_data="tariffs")],
        [InlineKeyboardButton("ℹ️ Информация", callback_data="info")],
        [InlineKeyboardButton("🛠 Техподдержка", callback_data="support")],
        [InlineKeyboardButton("📊 Мой статус", callback_data="status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔒 *Приватный VPN*\n\n"
        "• Обход блокировок\n"
        "• Скорость до 1 Гбит/с\n"
        "• 50+ стран\n"
        "• Без логов\n"
        "• 256-битное шифрование\n\n"
        "Выберите нужный раздел:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def tariffs_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📅 1 месяц - 109₽", callback_data="tariff_1month")],
        [InlineKeyboardButton("📅 3 месяца - 290₽ (скидка 11%)", callback_data="tariff_3month")],
        [InlineKeyboardButton("📅 6 месяцев - 530₽ (скидка 19%)", callback_data="tariff_6month")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔐 *Выберите тарифный план*\n\n"
        "⚡ Скорость: до 1 Гбит/с\n"
        "🌍 50+ стран\n"
        "🔒 Безлимитные устройства\n"
        "🚫 Без логов",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def tariff_info(update: Update, context: ContextTypes.DEFAULT_TYPE, tariff_key: str):
    t = tariffs[tariff_key]
    savings_text = f"\n💎 {t['savings']}" if "savings" in t else ""
    
    keyboard = [
        [InlineKeyboardButton("💳 Оплатить", callback_data=f"select_{tariff_key}")],
        [InlineKeyboardButton("🔙 К тарифам", callback_data="tariffs")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"{t['name']}\n\n"
        f"💰 *Цена:* {t['price']}\n"
        f"⏱ *Период:* {t['period']}{savings_text}\n\n"
        f"_{t['desc']}_",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "ℹ️ *Информация о VPN*\n\n"
        "🔒 *Шифрование:* WireGuard (AES-256)\n"
        "🌐 *Протокол:* WireGuard\n"
        "📍 *Локации:* 50+ стран\n"
        "⏱ *Uptime:* 99.9%\n"
        "🚫 *Логи:* Не ведутся\n"
        "📱 *Устройства:* Безлимит\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Состояние подписки*\n"
        f"Статус: {subscription_info['status']}\n"
        f"Тариф: {subscription_info['plan']}\n"
        f"Истекает: {subscription_info['expires']}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💬 Написать в поддержку", url="https://t.me/llsdrl")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🛠 *Техническая поддержка*\n\n"
        "Наши специалисты помогут с:\n"
        "• Настройкой VPN\n"
        "• Решением технических проблем\n"
        "• Вопросами по оплате\n\n"
        "📱 *Telegram:* @llsdrl\n"
        "⏰ Время работы: 24/7",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📊 *Мой статус*\n\n"
        f"🔐 VPN: {subscription_info['status']}\n"
        f"📋 Тариф: {subscription_info['plan']}\n"
        f"📅 Истекает: {subscription_info['expires']}\n\n"
        "Выберите тариф для активации!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Справка*\n\n"
        "/start - Главное меню\n"
        "/tariffs - Тарифы\n"
        "/info - Информация\n"
        "/support - Техподдержка\n"
        "/status - Ваш статус",
        parse_mode="Markdown"
    )

async def setadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_CHAT_ID
    if context.args:
        try:
            ADMIN_CHAT_ID = int(context.args[0])
            await update.message.reply_text(f"✅ Admin chat ID установлен: {ADMIN_CHAT_ID}")
            print(f"Admin chat ID set to: {ADMIN_CHAT_ID}")
        except ValueError:
            await update.message.reply_text("❌ Неверный формат ID")
    else:
        ADMIN_CHAT_ID = update.message.chat_id
        await update.message.reply_text(f"✅ Admin chat ID установлен: {ADMIN_CHAT_ID}")
        print(f"Admin chat ID set to: {ADMIN_CHAT_ID}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    chat_id = query.message.chat_id
    
    if data == "tariffs":
        keyboard = [
            [InlineKeyboardButton("📅 1 месяц - 109₽", callback_data="tariff_1month")],
            [InlineKeyboardButton("📅 3 месяца - 290₽ (скидка 11%)", callback_data="tariff_3month")],
            [InlineKeyboardButton("📅 6 месяцев - 530₽ (скидка 19%)", callback_data="tariff_6month")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=query.message.message_id,
            text="🔐 *Выберите тарифный план*\n\n⚡ Скорость: до 1 Гбит/с\n🌍 50+ стран\n🔒 Безлимитные устройства\n🚫 Без логов",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    elif data == "info":
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=query.message.message_id,
            text="ℹ️ *Информация о VPN*\n\n🔒 *Шифрование:* WireGuard (AES-256)\n🌐 *Протокол:* WireGuard\n📍 *Локации:* 50+ стран\n⏱ *Uptime:* 99.9%\n🚫 *Логи:* Не ведутся\n📱 *Устройства:* Безлимит\n\n━━━━━━━━━━━━━━━━━━━━\n📊 *Состояние подписки*\nСтатус: Не активна\nТариф: Не выбран\nИстекает: -",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    elif data == "support":
        keyboard = [
            [InlineKeyboardButton("💬 Написать в поддержку", url="https://t.me/llsdrl")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=query.message.message_id,
            text="🛠 *Техническая поддержка*\n\nНаши специалисты помогут с:\n• Настройкой VPN\n• Решением технических проблем\n• Вопросами по оплате\n\n📱 *Telegram:* @llsdrl\n⏰ Время работы: 24/7",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    elif data == "status":
        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=query.message.message_id,
            text="📊 *Мой статус*\n\n🔐 VPN: Не активна\n📋 Тариф: Не выбран\n📅 Истекает: -\n\nВыберите тариф для активации!",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    elif data == "back":
        keyboard = [
            [InlineKeyboardButton("🔐 Подключить VPN", callback_data="tariffs")],
            [InlineKeyboardButton("ℹ️ Информация", callback_data="info")],
            [InlineKeyboardButton("🛠 Техподдержка", callback_data="support")],
            [InlineKeyboardButton("📊 Мой статус", callback_data="status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=query.message.message_id,
            text="🔒 *Приватный VPN*\n\n• Обход блокировок\n• Скорость до 1 Гбит/с\n• 50+ стран\n• Без логов\n• 256-битное шифрование\n\nВыберите нужный раздел:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    elif data.startswith("tariff_"):
        tariff_key = data.split("_")[1]
        t = tariffs[tariff_key]
        savings_text = f"\n💎 {t['savings']}" if "savings" in t else ""
        keyboard = [
            [InlineKeyboardButton("💳 Оплатить", callback_data=f"select_{tariff_key}")],
            [InlineKeyboardButton("🔙 К тарифам", callback_data="tariffs")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=query.message.message_id,
            text=f"{t['name']}\n\n💰 *Цена:* {t['price']}\n⏱ *Период:* {t['period']}{savings_text}\n\n_{t['desc']}_",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    elif data.startswith("select_"):
        tariff_key = data.split("_")[1]
        t = tariffs[tariff_key]
        
        user_name = query.from_user.first_name
        username = f"@{query.from_user.username}" if query.from_user.username else "нет username"
        user_id = query.from_user.id
        
        notification_text = (
            f"🛒 *Новая заявка на покупку!*\n\n"
            f"👤 Пользователь: {user_name}\n"
            f"🔗 Telegram: {username}\n"
            f"🆔 ID: {user_id}\n\n"
            f"📋 Тариф: {t['name']}\n"
            f"💰 Сумма: {t['price']}"
        )
        
        if ADMIN_CHAT_ID:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=notification_text, parse_mode="Markdown")
        
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=query.message.message_id,
            text=f"✅ *Запрос на оплату отправлен!*\n\nТариф: {t['name']}\nЦена: {t['price']}\n\n📱 Менеджер свяжется с вами в ближайшее время.\n\n❓ Возникли вопросы? @llsdrl",
            parse_mode="Markdown"
        )

async def main():
    try:
        app = Application.builder().token("8749332624:AAFyhffF1GElZxVBSdU-cb-GFmkSfdcDKkg").build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("setadmin", setadmin_command))
        app.add_handler(CommandHandler("tariffs", tariffs_menu))
        app.add_handler(CommandHandler("info", info_command))
        app.add_handler(CommandHandler("support", support_command))
        app.add_handler(CommandHandler("status", status_command))
        app.add_handler(CallbackQueryHandler(button_callback))

        print("Бот запущен...")
        await app.run_polling()
    except Exception as e:
        print(f"Ошибка: {e}")
        raise

if __name__ == "__main__":
    loop.create_task(main())
    loop.run_forever()