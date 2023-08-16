from telegram import Update

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
        user = await db.get_user(tg_id=update.message.from_user.id)
        if user is not None:
            return await func(update, *args, **kwargs)
        else:
            return await update.message.reply_text(
                f"Вас нет в нашей базе, для регистрации: /{c.START_REGISTRATION}"
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
