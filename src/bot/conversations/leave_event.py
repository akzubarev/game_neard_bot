from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    CallbackQueryHandler

import bot.const as c
import bot.database as db
from bot.utils import reply_keyboard, make_rectangle, logged_in, edit_announce, \
    edit_announce_admin, edit_dashboard, edit_dashboard_admin
from bot.utils.auth import not_group
from bot.utils.mailing import user_game_message
from config.logging import LogHelper

EVENT, CONFIRM, END = range(3)
logger = LogHelper().logger

strf_format = '%d.%m.%Y %H:%M'


@not_group
@logged_in
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    context.user_data["event"] = {"username": username}
    events = [
        (event.str, event.id) for event in
        await db.get_events(telegram_id=update.message.from_user.id)
    ]
    if len(events) == 0:
        await update.message.reply_text(
            "Вы не записаны на игры", reply_markup=None
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            reply_text(next_stage=EVENT, task_data=context.user_data["event"]),
            reply_markup=reply_keyboard(
                options=[*make_rectangle(events)], placeholder="Игра"
            )
        )
    return EVENT


async def event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query_message = update.callback_query
    event_id = int(query_message.data.strip())
    await query_message.answer()
    event_str = (await db.events.get_event(event_id=event_id)).str
    context.user_data["event"]["event_id"] = event_id
    context.user_data["event"]["event_descr"] = event_str
    context.user_data["event"]["players"] = "\n".join(
        (await db.events.get_event(event_id=event_id)).players
    )
    await query_message.edit_message_text(
        text=reply_text(
            next_stage=CONFIRM, task_data=context.user_data["event"]
        ), reply_markup=reply_keyboard(
            [[("Покинуть игру", None)]], placeholder="Покинуть игру"
        )
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query_message = update.callback_query
    await query_message.answer()
    event_id = context.user_data["event"]["event_id"]
    event = await db.events.remove_player(
        event_id=event_id, player_tg_id=query_message.from_user.id
    )
    context.user_data["event"]["players"] = event.players_text()

    await query_message.edit_message_text(
        text=reply_text(
            next_stage=END, task_data=context.user_data["event"]
        ), reply_markup=None
    )

    await edit_announce(
        context=context, message_id=event.announce_message, event=event
    )
    await edit_dashboard(context=context)

    await edit_announce_admin(
        context=context, message_id=event.admin_message, event=event
    )
    await edit_dashboard_admin(context=context)
    await user_game_message(
        context=context, username=query_message.from_user.username,
        event=event, join=False
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        f"Выход из игры отменен, {c.SIGN_UP_TEXT}",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def reply_text(next_stage: int, task_data: dict):
    reply_str = list()
    if next_stage == EVENT:
        reply_str.append("Выберите игру:")
    else:
        reply_str.append(f"Игра: {task_data.get('event_descr')}")

    if next_stage == CONFIRM:
        reply_str.extend([
            f"Игроки: {task_data.get('players')}",
            "Покинуть игру?",
        ])
    elif next_stage > CONFIRM:
        reply_str.append(f"Игроки: {task_data.get('players')}")

    if next_stage == END:
        reply_str.extend(["-" * 20, "Вы покинули игру"])
    else:
        reply_str.extend(
            ["-" * 20, "Для отмены выхода из игры нажмите /cancel"])
    return "\n".join(reply_str)


def get_leave_event_handler():
    return ConversationHandler(
        entry_points=[CommandHandler(c.LEAVE, start)],
        states={
            EVENT: [CallbackQueryHandler(event)],
            CONFIRM: [CallbackQueryHandler(confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
