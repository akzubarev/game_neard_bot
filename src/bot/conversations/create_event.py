from datetime import datetime

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    MessageHandler, filters, CallbackQueryHandler

import bot.const as c
import bot.database as db
from bot.utils import reply_keyboard, make_rectangle, logged_in
from bot.utils.auth import not_group
from bot.utils.mailing import handle_event_create
from config.logging import LogHelper
from utils.time_str import STRF_DATE_TIME

GAME, DATETIME, COMMENT, END = range(4)
logger = LogHelper().logger


@not_group
@logged_in
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["game"] = {
        "telegram_id": update.message.from_user.id,
    }
    games = await db.get_games()
    await update.message.reply_text(
        reply_text(next_stage=GAME, task_data=context.user_data["game"]),
        reply_markup=reply_keyboard(
            options=make_rectangle(games, max_width=2),
            placeholder="Игра"
        )
    )
    return GAME


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query_message = update.callback_query
    game_id = int(query_message.data.strip())
    await query_message.answer()
    game_obj = await db.get_game(game_id=game_id)

    context.user_data["game"]["game_name"] = game_obj.name
    await query_message.edit_message_text(
        text=reply_text(
            next_stage=DATETIME, task_data=context.user_data["game"]
        ), reply_markup=None
    )
    return DATETIME


async def date_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query_message = update.message.text.strip()
    game_date_time = datetime.strptime(
        query_message, STRF_DATE_TIME
    ).replace(year=datetime.now().year)
    context.user_data["game"]["date_time"] = game_date_time
    await update.message.reply_text(
        text=reply_text(
            next_stage=COMMENT, task_data=context.user_data["game"]
        ), reply_markup=reply_keyboard(
            options=[[("Пропустить", None)]], placeholder="Комментарий",
        )
    )
    return COMMENT


async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    comment_text = update.message.text.strip()
    context.user_data["game"]["comment"] = comment_text
    await save_task(context=context)
    await update.message.reply_text(
        reply_text(
            next_stage=END, task_data=context.user_data["game"]
        ), reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def skip_comment(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["game"]["comment"] = ""
    await save_task(context=context)
    if update.callback_query is not None:
        await update.callback_query.edit_message_text(
            reply_text(
                next_stage=END, task_data=context.user_data["game"]
            ), reply_markup=None
        )
    else:
        await update.message.reply_text(
            reply_text(
                next_stage=END, task_data=context.user_data["game"]
            ), reply_markup=ReplyKeyboardRemove()
        )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        f"Запись отменена, {c.CREATE_GAME_TEXT}",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def save_task(context: ContextTypes.DEFAULT_TYPE):
    task_data = context.user_data["game"]
    event = await db.save_event(
        game_name=task_data.get("game_name"),
        date_time=task_data.get("date_time"),
        comment=task_data.get("comment"),
        user_telegram_id=task_data.get("telegram_id")
    )

    await handle_event_create(event=event, context=context)


def reply_text(next_stage: int, task_data: dict):
    reply_str = list()
    if next_stage == GAME:
        reply_str.append("Выберите игру:")
    else:
        reply_str.append(f"Игра: {task_data.get('game_name')}")

    if next_stage == DATETIME:
        time_fmt = datetime.now().strftime(STRF_DATE_TIME)
        reply_str.append(
            f"Введите время игры в формате {time_fmt}:"
        )
    elif next_stage > DATETIME:
        time_fmt = task_data.get('date_time').strftime(STRF_DATE_TIME)
        reply_str.append(f"Время игры: {time_fmt}")

    if next_stage == COMMENT:
        reply_str.append("Введите комментарий или /skip чтобы пропустить")
    elif next_stage > COMMENT:
        reply_str.append(f"Комментарий: {task_data.get('comment')}")

    if next_stage == END:
        reply_str.extend(["-" * 20, "Записано"])
    else:
        reply_str.extend(["-" * 20, "Для отмены записи напишите /cancel"])
    return "\n".join(reply_str)


def get_create_event_handler():
    not_command = filters.TEXT & ~filters.COMMAND
    return ConversationHandler(
        entry_points=[CommandHandler(c.CREATE_GAME, start)],
        states={
            GAME: [CallbackQueryHandler(game)],
            DATETIME: [MessageHandler(not_command, date_time)],
            COMMENT: [
                CallbackQueryHandler(skip_comment),
                MessageHandler(not_command, comment),
                CommandHandler("skip", skip_comment)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
