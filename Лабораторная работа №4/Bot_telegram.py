import os

# Отключаем прокси для Python
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)


import logging
import requests
from datetime import datetime, date
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest


load_dotenv("API.env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

keyboard = ReplyKeyboardMarkup(
    [
        ["📅 Ввести дату рождения"],
        ["ℹ️ Помощь"]
    ],
    resize_keyboard=True
)


def get_current_datetime() -> datetime:
    try:
        response = requests.get(
            "https://worldtimeapi.org/api/timezone/Europe/Moscow",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return datetime.fromisoformat(data["datetime"])
    except Exception:
        return datetime.now()


def parse_birth_date(text: str) -> date | None:
    formats = ["%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"]

    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    return None


def calculate_lived(birth_date: date) -> dict:
    now = get_current_datetime()
    today = now.date()

    if birth_date > today:
        raise ValueError("Дата рождения не может быть в будущем.")

    diff = relativedelta(today, birth_date)

    lived_days = (today - birth_date).days
    lived_weeks = lived_days // 7
    lived_seconds = int(
        (
            now.replace(tzinfo=None)
            - datetime.combine(birth_date, datetime.min.time())
        ).total_seconds()
    )

    total_months = diff.years * 12 + diff.months

    return {
        "years": diff.years,
        "months": total_months,
        "weeks": lived_weeks,
        "days": lived_days,
        "seconds": lived_seconds,
    }


async def send_admin_log(context: ContextTypes.DEFAULT_TYPE, update: Update, message: str):
    if not ADMIN_ID:
        return

    user = update.effective_user

    username = f"@{user.username}" if user.username else "нет username"

    log_text = (
        "📝 Лог пользователя\n\n"
        f"Имя: {user.full_name}\n"
        f"Username: {username}\n"
        f"ID: {user.id}\n"
        f"Ввод: {message}"
    )

    logging.info(log_text)

    try:
        await context.bot.send_message(
            chat_id=int(ADMIN_ID),
            text=log_text
        )
    except Exception as e:
        logging.error(f"Ошибка отправки лога администратору: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name

    await update.message.reply_text(
        f"Привет, {name}! 👋\n\n"
        "Я бот «Сколько прожито».\n"
        "Я посчитаю, сколько ты уже прожил лет, месяцев, недель, дней и секунд.",
        reply_markup=keyboard
    )

    await send_admin_log(context, update, "/start")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Помощь\n\n"
        "Нажми кнопку «📅 Ввести дату рождения».\n"
        "Затем отправь дату рождения в одном из форматов:\n\n"
        "• 25.12.2005\n"
        "• 25/12/2005\n"
        "• 2005-12-25\n\n"
        "После этого я покажу, сколько времени ты уже прожил.",
        reply_markup=keyboard
    )

    await send_admin_log(context, update, "/help")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    name = update.effective_user.first_name

    await send_admin_log(context, update, text)

    if text == "ℹ️ Помощь":
        await help_command(update, context)
        return

    if text == "📅 Ввести дату рождения":
        await update.message.reply_text(
            f"{name}, введи дату рождения.\n"
            "Например: 25.12.2005"
        )
        return

    birth_date = parse_birth_date(text)

    if birth_date is None:
        await update.message.reply_text(
            "Не понял дату 😅\n\n"
            "Введи дату рождения в формате:\n"
            "ДД.ММ.ГГГГ\n\n"
            "Например: 25.12.2005",
            reply_markup=keyboard
        )
        return

    try:
        result = calculate_lived(birth_date)
    except ValueError as e:
        await update.message.reply_text(str(e), reply_markup=keyboard)
        return

    await update.message.reply_text(
        f"{name}, ты прожил:\n\n"
        f"🎂 Лет: {result['years']}\n"
        f"📆 Месяцев: {result['months']}\n"
        f"🗓 Недель: {result['weeks']}\n"
        f"🌍 Дней: {result['days']}\n"
        f"⏱ Секунд: {result['seconds']}",
        reply_markup=keyboard
    )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не найден в файле API.env")

    request = HTTPXRequest(
        connect_timeout=60,
        read_timeout=60,
        write_timeout=60,
        pool_timeout=60,
    )

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(request)
        .get_updates_request(request)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()