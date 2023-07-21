from telegram import Update
from telegram.ext import ContextTypes

import bot.const as c
import bot.responses as r
from config.logging import LogHelper

logger = LogHelper().logger


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = str(update.message.text).lower()
    logger.info(f"{update.message.chat.id} {message_type} {text}")
    # response = await responses.handle_response(text)
    logger.info(f"{update.message.chat.id}")
    if message_type == "group":
        if c.BOT_USERNAME in text:
            new_text = text.replace(c.BOT_USERNAME, '').strip()
            response = r.handle_response(text=new_text)
        else:
            return
    else:
        response = r.handle_response(text=text)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Update {update} caused error: {context.error}")
