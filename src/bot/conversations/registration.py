from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    MessageHandler, filters

import bot.const as c
import bot.database as db
from bot.utils.auth import not_group
from config.logging import LogHelper

logger = LogHelper().logger

USERNAME = 0


@not_group
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите имя и фамилию (Пример: Хидео Кодзима")
    return USERNAME


async def username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    first_name, last_name = update.message.text.strip().split(" ")
    await db.create_user(
        tg_id=update.message.from_user.id,
        first_name=first_name, last_name=last_name,
        username=update.message.from_user.username
    )
    await update.message.reply_text(
        f"Добрый день, {first_name} {last_name}, {c.SIGN_UP_TEXT}"
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Регистрация отменена", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def get_registration_handler():
    return ConversationHandler(
        entry_points=[CommandHandler(c.START_REGISTRATION, start)],
        states={
            USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, username)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=c.CONVERSATION_TIMOUT,
        allow_reentry=True
    )
