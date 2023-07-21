import locale
import traceback
from datetime import date, timedelta

from telegram import Update
from telegram.ext import ContextTypes

import bot.const as c
import bot.database as db
from bot.utils import logged_in
from utils.links import apply_markdown
from utils.time_str import STRF_DATE_TIME, STRF_WEEKDAY, ru_date


@logged_in
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await db.get_user(tg_id=update.message.from_user.id)
    await update.message.reply_text(
        f"Добрый день, {user.first_name}, {c.SIGN_UP_TEXT}"
    )


@logged_in
async def my_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = await db.get_events(username=update.message.from_user.username)
    user_strs = {
        event_id: '\n'.join([
            username for username in
            await db.get_event_players(event_id=event_id)
        ])
        for event_str, event_id in events
    }
    await update.message.reply_text(  # apply_markdown(
        "\n\n".join([
            f"Вы записаны на следующие игры: ",
            *[f"{event_str}\n{user_strs[event_id]}"
              for event_str, event_id in events]
        ])  # ), parse_mode="MarkdownV2"
    )


async def events_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = {
        ru_date(day): [
            event_str for event_str, event_id in await db.get_events(day=day)
        ]
        for day in [date.today() + timedelta(days=i) for i in range(7)]
    }

    res_text = ["Игры в ближайшее время: "]
    for day_name, day_events in events.items():
        if len(day_events) > 0:
            res_text.append(
                f"<b>{day_name}</b>\n" + "\n".join(day_events)
            )
    res_text.append(f"{'-' * 20}\nЗаписаться - /{c.SIGN_UP}")
    await update.message.reply_text(  # apply_markdown(
        "\n\n".join(res_text), parse_mode="html"
    )


async def games_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    games = await db.get_games_linked()
    await update.message.reply_text(
        "\n".join([
            f"Список наших игр\: ",
            *[game_link for game_link, game_id in games]
        ]), parse_mode="MarkdownV2", disable_web_page_preview=True
    )


async def help_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "\n".join([
            f"/{c.START_REGISTRATION} - регистрация",
            f"/{c.GAME_LIST} - список игр",
            f"/{c.EVENTS} - список ближайших игр",
            f"/{c.SIGN_UP} - записаться на игру",
            f"/{c.CREATE_GAME} - создать игру",
            f"/{c.MY_GAMES} - мои игры",
            f"/{c.LEAVE} - покинуть игру",
            f"/help - справка",
        ])
    )
