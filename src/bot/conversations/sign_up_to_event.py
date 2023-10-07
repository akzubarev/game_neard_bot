import traceback

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    CallbackQueryHandler, filters, MessageHandler

import bot.const as c
import bot.database as db
from bot.utils import reply_keyboard, make_rectangle, logged_in, \
    handle_event_change
from bot.utils.auth import not_group
from config.logging import LogHelper

EVENT, CONFIRM, PLUS_ONE, END = range(4)
logger = LogHelper().logger


@not_group
@logged_in
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["event"] = dict()
        events = [(event.simple_str(), event.id) for event in
                  await db.get_events(
                      filter_full=True, exclude=True,
                      telegram_id=update.message.from_user.id
                  )]
        if len(events) > 0:
            await update.message.reply_text(
                reply_text(next_stage=EVENT,
                           task_data=context.user_data["event"]),
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
    except Exception as e:
        traceback.print_exc()


async def event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query_message = update.callback_query
    event_id = int(query_message.data.strip())
    await query_message.answer()
    event_data = await db.get_event(event_id=event_id)
    context.user_data["event"]["event_id"] = event_id
    context.user_data["event"]["event_descr"] = event_data.simple_str()
    context.user_data["event"]["players"] = event_data.players_text()
    await query_message.edit_message_text(
        text=reply_text(
            next_stage=CONFIRM, task_data=context.user_data["event"]
        ), reply_markup=reply_keyboard(
            [[("Записаться одному", None),
              ("Записаться с друзьями", "PLUS_ONE")]],
            placeholder="Записаться"
        )
    )
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query_message = update.callback_query
    await query_message.answer()
    event_id = context.user_data["event"]["event_id"]
    event = await db.add_player(
        event_id=event_id, player_tg_id=query_message.from_user.id,
        plus_one=context.user_data["event"].get("plus_one", None)
    )
    context.user_data["event"]["players"] = event.players_text()
    if query_message.data.strip() == "PLUS_ONE":
        await query_message.edit_message_text(
            text=reply_text(
                next_stage=PLUS_ONE, task_data=context.user_data["event"]
            ), reply_markup=reply_keyboard(
                [[("Пропустить", None)]], placeholder="Пропустить"
            )
        )
        return PLUS_ONE
    else:
        await query_message.edit_message_text(
            text=reply_text(
                next_stage=END, task_data=context.user_data["event"]
            ), reply_markup=None
        )
        await handle_event_change(
            event=event, user=query_message.from_user,
            join=True, context=context,
        )
        return ConversationHandler.END


async def plus_one(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    num = int(update.message.text.strip())
    context.user_data["event"]["plus_one"] = num
    await update.message.reply_text(
        text=reply_text(
            next_stage=END, task_data=context.user_data["event"]
        ), reply_markup=None
    )
    event_id = context.user_data["event"]["event_id"]
    event = await db.get_event(event_id=event_id)
    await handle_event_change(
        event=event, user=user, join=True, context=context,
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

    if next_stage == PLUS_ONE:
        reply_str.extend([
            "Если с вами придут +1, напишите их количество (Пример: 2)"
        ])

    if next_stage == END:
        reply_str.extend(["-" * 20, "Записано"])
    else:
        reply_str.extend(["-" * 20, "Для отмены записи напишите /cancel"])
    return "\n".join(reply_str)


def get_sign_up_to_event_handler():
    not_command = filters.TEXT & ~filters.COMMAND
    return ConversationHandler(
        entry_points=[CommandHandler(c.SIGN_UP, start)],
        states={
            EVENT: [CallbackQueryHandler(event)],
            PLUS_ONE: [
                CallbackQueryHandler(plus_one),
                MessageHandler(not_command, plus_one),
            ],
            CONFIRM: [CallbackQueryHandler(confirm)],
            # ConversationHandler.TIMEOUT: []
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=c.CONVERSATION_TIMOUT,
        allow_reentry=True
    )
