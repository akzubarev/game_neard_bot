import traceback

from telegram.ext import ContextTypes

from apps.games.models import EventData
from bot import const as c, database as db
from bot.utils import action_button
from .admin import send_to_admin


async def send_to_chat(context: ContextTypes.DEFAULT_TYPE, text,
                       keyboard, parse_mode=None) -> int | None:
    message_id = None
    try:
        message_id = (await context.bot.send_message(
            chat_id=c.TELEGRAM_MAIN_GROUP, text=text,
            reply_markup=keyboard, parse_mode=parse_mode,
            # message_thread_id=None
        )).message_id
    except Exception as e:
        traceback.print_exc()
    return message_id


async def create_announce(event: EventData,
                          context: ContextTypes.DEFAULT_TYPE):
    try:
        announce_id = await send_to_chat(
            context=context, text=event.announce(admin=False),
            keyboard=action_button(
                text="Записаться", command=c.SIGN_UP, key=event.id
            )
        )
        await db.save_announce_message(
            event_id=event.id, message_id=announce_id, admin=False
        )
    except Exception as e:
        traceback.print_exc()

    try:
        admin_message_id = await send_to_admin(
            context=context, text=event.announce(admin=True), keyboard=None
        )
        await db.save_announce_message(
            event_id=event.id, message_id=admin_message_id, admin=True
        )
    except Exception as e:
        traceback.print_exc()


async def edit_announce(event: EventData, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(event.players) > 0:
            await context.bot.edit_message_text(
                chat_id=c.TELEGRAM_MAIN_GROUP,
                message_id=event.announce_message,
                text=event.announce(admin=False),
                reply_markup=action_button(
                    text="Записаться", command=c.SIGN_UP
                ),
            )
        elif event.announce_message is not None:
            await context.bot.delete_message(
                chat_id=c.TELEGRAM_MAIN_GROUP,
                message_id=event.announce_message,
            )
            await db.delete_event(event.id)
    except Exception as e:
        traceback.print_exc()

    try:
        await context.bot.edit_message_text(
            chat_id=c.TELEGRAM_ADMIN_GROUP,
            message_id=event.admin_message,
            text=event.announce(admin=True),
        )
    except Exception as e:
        traceback.print_exc()
