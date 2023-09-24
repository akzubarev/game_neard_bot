from telegram import Update
from telegram.ext import ContextTypes

import bot.const as c
import bot.responses as r
from config.logging import LogHelper

logger = LogHelper().logger


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = str(update.message.text).lower()
    # logger.info(f"{update.message.chat.id} {message_type} {text}")
    logger.info(f"{update.message.chat.id}")
    if message_type in ["group", "supergroup"]:
        if f"@{c.BOT_USERNAME}" in text:
            new_text = text.replace(f"@{c.BOT_USERNAME}", '').strip()
            await update.message.reply_text(r.handle_response(text=new_text))
    else:
        await update.message.reply_text(r.handle_response(text=text))


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Update {update} caused error: {context.error}")
