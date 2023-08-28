from typing import List

from math import ceil, sqrt
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, \
    InlineKeyboardButton

import bot.const as c


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


def action_button(text: str, command: str, key=None):
    match command:
        case c.SIGN_UP:
            link = f"https://t.me/{c.BOT_USERNAME}"  # /?start={c.SIGN_UP}"
        # case c.SIGN_UP:
        #     link = f"t.me//{c.BOT_USERNAME}/?start={key if key is not None else ''}"
        case _:
            link = ""
    keyboard = [[InlineKeyboardButton(text, url=link)]]
    return InlineKeyboardMarkup(keyboard)


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
