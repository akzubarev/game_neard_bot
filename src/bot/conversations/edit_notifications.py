from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, \
    CallbackQueryHandler, MessageHandler, filters

import bot.const as c
import bot.database as db
import bot.jobs as j
from bot.utils import reply_keyboard, logged_in
from bot.utils.auth import not_group, banned
from config.logging import LogHelper

ACTION, ADDITIONAL, END = range(3)
logger = LogHelper().logger

strf_format = '%d.%m.%Y %H:%M'


@banned
@not_group
@logged_in
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await db.get_user(tg_id=update.message.from_user.id)
    await update.message.reply_text(
        reply_text(user), reply_markup=reply_keyboard(
            [
                [('Включить уведомления', 1) if not user.remind_enabled else
                 ('Отключить уведомления', 2)],
                [("Изменить время уведомлений", 3)]
            ], placeholder="Покинуть игру"
        ))
    return ACTION


async def action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query_message = update.callback_query
    action = int(query_message.data.strip())
    await query_message.answer()

    match action:
        case 1:
            user = await enable_notifications(update=update, context=context)
            await query_message.edit_message_text(reply_text(user))
            return ConversationHandler.END
        case 2:
            user = await disable_notifications(update=update, context=context)
            await query_message.edit_message_text(reply_text(user))
            return ConversationHandler.END
        case 3:
            await query_message.edit_message_text(
                "За сколько часов до игры вам напоминать? (введите целое число)"
            )
            return ADDITIONAL


async def additional(update: Update,
                     context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        hours = int(update.message.text)
    except Exception as e:
        await update.message.reply_text("Это не целое число")
        return ADDITIONAL

    user = await db.change_remind_hours(
        tg_id=update.message.from_user.id, hours=hours
    )
    await update.message.reply_text(reply_text(user))
    return ConversationHandler.END


async def disable_notifications(update: Update,
                                context: ContextTypes.DEFAULT_TYPE):
    message = update.callback_query if update.callback_query is not None else update.message
    tg_id = message.from_user.id
    user = await db.disable_notifier(tg_id=tg_id)
    await j.remove_reminders(chat_id=tg_id, context=context)
    return user


async def enable_notifications(update: Update,
                               context: ContextTypes.DEFAULT_TYPE):
    message = update.callback_query if update.callback_query is not None else update.message
    tg_id = message.from_user.id
    user = await db.enable_notifier(tg_id=tg_id)
    for event in await db.get_events(telegram_id=tg_id):
        await j.set_reminder(
            user_id=tg_id, event=event, delay=user.remind_hours,
            chat_id=tg_id, context=context
        )
    return user


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        f"Изменения уведомлений отменены",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def reply_text(user):
    h_str = 'чаcов' if user.remind_hours > 5 else (
        'чаcа' if user.remind_hours > 1 else 'час'
    )
    return f"Уведомления за {user.remind_hours} {h_str} до игры {'включены' if user.remind_enabled else 'отключены'}"


def get_edit_notifications_handler():
    not_command = filters.TEXT & ~filters.COMMAND
    return ConversationHandler(
        entry_points=[CommandHandler(c.EDIT_NOTIFICATIONS, start)],
        states={
            ACTION: [CallbackQueryHandler(action)],
            ADDITIONAL: [MessageHandler(not_command, additional)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=c.CONVERSATION_TIMOUT,
        allow_reentry=True
    )
