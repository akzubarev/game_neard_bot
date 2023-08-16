from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    CallbackQueryHandler

import bot.const as c
import bot.database as db
from bot.utils import reply_keyboard, make_rectangle, logged_in, \
    edit_dashboard, edit_dashboard_admin, edit_announce, edit_announce_admin
from bot.utils.auth import not_group
from bot.utils.mailing import user_game_message
from config.logging import LogHelper

EVENT, CONFIRM, END = range(3)
logger = LogHelper().logger


@not_group
@logged_in
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    context.user_data["event"] = {"username": username}
    events = [(event.str, event.id) for event in await db.get_events(
        filter_full=True, exclude=True, telegram_id=update.message.from_user.id
    )]
    if len(events) > 0:
        await update.message.reply_text(
            reply_text(next_stage=EVENT, task_data=context.user_data["event"]),
            reply_markup=reply_keyboard(
                options=[[events[0]], *make_rectangle(events[1:])],
                placeholder="Игра"
            )
        )
        return EVENT

    else:
        await update.message.reply_text(
            f"В данный момент нет игр, в которые можно записаться, можете создать свою (/{c.CREATE_GAME})",
            reply_markup=None
        )
        return ConversationHandler.END


async def event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query_message = update.callback_query
    event_id = int(query_message.data.strip())
    await query_message.answer()
    event_data = await db.get_event(event_id=event_id)
    context.user_data["event"]["event_id"] = event_id
    context.user_data["event"]["event_descr"] = event_data.str
    context.user_data["event"]["players"] = event_data.players_text()
    await query_message.edit_message_text(
        text=reply_text(
            next_stage=CONFIRM, task_data=context.user_data["event"]
        ), reply_markup=reply_keyboard(
            [[("Записаться", None)]], placeholder="Записаться"
        )
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query_message = update.callback_query
    await query_message.answer()
    event_id = context.user_data["event"]["event_id"]
    event = await db.add_player(
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
        event=event, join=True
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        f"Запись отменена, {c.SIGN_UP}", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def reply_text(next_stage: int, task_data: dict):
    reply_str = list()
    if next_stage == EVENT:
        reply_str.extend([
            "Выберите игру:",
            f"Если не видите, во что хотели бы поиграть, "
            f"создайте свою игру (нажмите /cancel а потом /{c.CREATE_GAME})",
        ])
    else:
        reply_str.append(f"Игра: {task_data.get('event_descr')}")

    if next_stage == CONFIRM:
        reply_str.extend([
            f"Игроки: {task_data.get('players')}", "Записываем?",
        ])
    elif next_stage > CONFIRM:
        reply_str.append(f"Игроки: {task_data.get('players')}")

    if next_stage == END:
        reply_str.extend(["-" * 20, "Записано"])
    else:
        reply_str.extend(["-" * 20, "Для отмены записи напишите /cancel"])
    return "\n".join(reply_str)


def get_sign_up_to_event_handler():
    return ConversationHandler(
        entry_points=[CommandHandler(c.SIGN_UP, start)],
        states={
            EVENT: [CallbackQueryHandler(event)],
            CONFIRM: [CallbackQueryHandler(confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
