from typing import List

from math import ceil, sqrt
import bot.database as db
import bot.const as c
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, \
    InlineKeyboardButton, Update


def reply_keyboard(options: List[List], placeholder: str, buttons=True):
    if buttons is True:
        keyboard = [
            [
                InlineKeyboardButton(
                    option, callback_data=str(option_id)
                )
                for option, option_id in options_sublist
            ] for options_sublist in options
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        reply_markup = ReplyKeyboardMarkup(
            options, one_time_keyboard=True,
            input_field_placeholder=placeholder
        )
    return reply_markup


def make_rectangle(lst: list, max_width=5, min_width=1):
    lst_len = len(lst)
    width = max(min(int(ceil(sqrt(lst_len))), max_width), min_width)
    height = int(ceil(lst_len / width))
    square_lst = list()
    for i in range(height):
        square_lst.append(list())
        for j in range(width):
            if i * width + j < lst_len:
                square_lst[i].append(lst[i * width + j])
    return square_lst


def make_column(lst: list):
    return [[elem] for elem in lst]


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
