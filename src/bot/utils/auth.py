from telegram import Update
from telegram.ext import ContextTypes

import bot.const as c
import bot.database as db


def is_manager(func, *args, **kwargs):
    async def wrapper(update: Update, *args, **kwargs):
        manager = await db.user_is_manager(tg_id=update.message.from_user.id)
        if manager is True:
            return await func(update, *args, **kwargs)
        else:
            return await update.message.reply_text(
                "У вас недостаточно прав чтобы использовать эту команду"
            )

    return wrapper


def logged_in(func, *args, **kwargs):
    async def wrapper(update: Update, *args, **kwargs):
        user = await db.get_user(
            tg_id=update.message.from_user.id, chat_id=update.message.chat_id
        )
        if user is not None:
            return await func(update, *args, **kwargs)
        else:
            return await update.message.reply_text(
                f"Вас нет в нашей базе, для регистрации: /start"
            )

    return wrapper


def not_group(func, *args, **kwargs):
    async def wrapper(update: Update, *args, **kwargs):
        if update.message.chat.type == "group":
            return await update.message.reply_text(
                f"Команду нельзя использовать в групповом чате"
            )
        else:
            return await func(update, *args, **kwargs)

    return wrapper


def banned(func, *args, **kwargs):
    async def wrapper(update: Update, *args, **kwargs):
        if update.message is not None:
            user = await db.get_user(
                tg_id=update.message.from_user.id,
                chat_id=update.message.chat_id
            )
        else:
            query_message = update.callback_query
            user = await db.get_user(
                tg_id=query_message.from_user.id,
                chat_id=query_message.message.chat_id
            )
        if user is not None:
            if user.ban is False:
                return await func(update, *args, **kwargs)
            # else:
            # return await update.message.reply_text(
            #     f"Вы были забанены за подозрительное поведение, команды для вас недоступны"
            # )
        else:
            return await update.message.reply_text(
                f"Вас нет в нашей базе, для регистрации: /start"
            )

    return wrapper


async def can_see_players(user_id, context: ContextTypes.DEFAULT_TYPE):
    user = await db.get_user(tg_id=user_id)
    return (not user.banned) and context.user_data["user"][
        "games"] > c.ENTRY_POINT

