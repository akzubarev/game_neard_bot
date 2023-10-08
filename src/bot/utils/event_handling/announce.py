import traceback

from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from apps.games.models import EventData
from bot import const as c, database as db
from bot.utils import action_button
from .admin import send_to_admin


async def create_announce(event: EventData,
                          context: ContextTypes.DEFAULT_TYPE,
                          is_manager: bool):
    try:
        if event.link is not None:
            message = await context.bot.send_photo(
                chat_id=c.TELEGRAM_MAIN_GROUP,
                photo=open(event.link, 'rb'),
                caption=event.announce(admin=False),
                reply_markup=action_button(
                    text="Записаться", command=c.SIGN_UP, key=event.id
                ), parse_mode=ParseMode.HTML,
                message_thread_id=c.TELEGRAM_SUPERGROUP_ID
            )
        else:
            message = await context.bot.send_message(
                chat_id=c.TELEGRAM_MAIN_GROUP,
                text=event.announce(admin=False),
                reply_markup=action_button(
                    text="Записаться", command=c.SIGN_UP, key=event.id
                ), parse_mode=ParseMode.HTML,
                message_thread_id=c.TELEGRAM_SUPERGROUP_ID
            )
        await db.save_announce_message(
            event_id=event.id, message_id=message.message_id, admin=False
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
            if event.link is None:
                await context.bot.edit_message_text(
                    chat_id=c.TELEGRAM_MAIN_GROUP,
                    message_id=event.announce_message,
                    text=event.announce(admin=False),
                    reply_markup=action_button(
                        text="Записаться", command=c.SIGN_UP
                    ),
                )
            else:
                await context.bot.edit_message_caption(
                    chat_id=c.TELEGRAM_MAIN_GROUP,
                    message_id=event.announce_message,
                    caption=event.announce(admin=False),
                    reply_markup=action_button(
                        text="Записаться", command=c.SIGN_UP
                    ),
                )
        elif event.announce_message is not None:
            try:
                await context.bot.delete_message(
                    chat_id=c.TELEGRAM_MAIN_GROUP,
                    message_id=event.announce_message,
                )
            except Exception as e:
                traceback.print_exc()
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
