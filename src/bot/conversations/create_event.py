import os
from datetime import datetime

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    MessageHandler, filters, CallbackQueryHandler

import bot.const as c
import bot.database as db
from bot.utils import reply_keyboard, make_rectangle, logged_in, \
    handle_event_create
from bot.utils.auth import not_group
from config.logging import LogHelper
from utils.time_str import STRF_DATE_TIME

GAME, DATETIME, JOIN, COMMENT, END = range(5)
logger = LogHelper().logger


@not_group
@logged_in
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["game"] = {
        "telegram_id": update.message.from_user.id,
        "join": True
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

    is_manager = await db.user_is_manager(tg_id=update.message.from_user.id)
    if is_manager is True:
        await update.message.reply_text(
            text=reply_text(
                next_stage=JOIN, task_data=context.user_data["game"]
            ), reply_markup=reply_keyboard(
                options=[[("Да", "Да"), ("Нет", "Нет")]],
                placeholder="Присоединиться?",
            )
        )
        return JOIN
    else:
        await save_task(context=context)
        await update.message.reply_text(
            reply_text(
                next_stage=END, task_data=context.user_data["game"]
            ), reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END


async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query_message = update.callback_query
    await query_message.answer()
    join = query_message.data.strip() == "Да"
    context.user_data["game"]["join"] = join
    await query_message.edit_message_text(
        text=reply_text(
            next_stage=COMMENT, task_data=context.user_data["game"]
        ), reply_markup=reply_keyboard(
            options=[[("Пропустить", None)]], placeholder="Комментарий",
        )
    )
    return COMMENT


async def save_image(image, name: str, context: ContextTypes.DEFAULT_TYPE):
    REPORTS_FOLDER = "static/photos"
    path = f'{REPORTS_FOLDER}/{name}-{datetime.now().strftime("%Y-%m-%d")}.png'
    if not os.path.exists(REPORTS_FOLDER):
        os.makedirs(REPORTS_FOLDER)
    await image.download_to_drive(path)
    return path


async def comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text is not None:
        comment_text = update.message.text.strip()
        context.user_data["game"]["comment"] = comment_text

    if len(update.message.photo) > 0:
        comment_text = update.message.caption.strip()
        photo_file = await update.message.photo[-1].get_file()
        context.user_data["game"]["comment"] = comment_text
        path = await save_image(
            image=photo_file, context=context,
            name=context.user_data["game"]["game_name"],
        )
        context.user_data["game"]["link"] = path

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
        user_telegram_id=task_data.get("telegram_id"),
        game_name=task_data.get("game_name"),
        date_time=task_data.get("date_time"),
        comment=task_data.get("comment", None),
        link=task_data.get("link", None),
        join=task_data.get("join", None),
    )

    is_manager = await db.user_is_manager(tg_id=task_data.get("telegram_id"))
    await handle_event_create(
        event=event, context=context, is_manager=is_manager
    )


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

    if next_stage == JOIN:
        reply_str.append(f"Вы хотите сами присоединиться к игре?")

    if next_stage == COMMENT:
        reply_str.append(
            "Введите комментарий (можно прикрепить 1 картинку) или /skip чтобы пропустить")
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
            JOIN: [CallbackQueryHandler(join_game)],
            COMMENT: [
                CallbackQueryHandler(skip_comment),
                MessageHandler(not_command | filters.PHOTO, comment),
                CommandHandler("skip", skip_comment)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=c.CONVERSATION_TIMOUT,
        allow_reentry=True
    )
