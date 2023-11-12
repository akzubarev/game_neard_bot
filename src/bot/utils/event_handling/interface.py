import traceback
import bot.database as db
import bot.jobs as j
from telegram import User
from telegram.ext import ContextTypes

from apps.games.models import EventData
from .admin import user_game_message
from .announce import edit_announce, create_announce
from .dashboard import edit_dashboard


async def handle_event_change(event: EventData, user: User, join: bool,
                              chat_id, context: ContextTypes.DEFAULT_TYPE):
    try:
        await edit_announce(context=context, event=event)
    except Exception as e:
        traceback.print_exc()

    try:
        await edit_dashboard(context=context)
    except Exception as e:
        traceback.print_exc()

    try:
        await user_game_message(
            context=context, username=user.username, event=event, join=join
        )
    except Exception as e:
        traceback.print_exc()

    try:
        await handle_user_reminder(
            chat_id=chat_id, event=event, user=user, join=join, context=context
        )
    except Exception as e:
        traceback.print_exc()


async def handle_user_reminder(event, user, chat_id, context, join: bool):
    user_obj = await db.get_user(tg_id=user.id, chat_id=chat_id)
    try:
        if user_obj.remind_enabled:
            if join is True:
                await j.set_reminder(
                    event=event, context=context, delay=user_obj.remind_hours,
                    user_id=user.id, chat_id=chat_id,
                )
            else:
                await j.remove_reminder(
                    chat_id=chat_id, event_id=event.id, context=context
                )

    except Exception as e:
        traceback.print_exc()


async def handle_event_create(event: EventData,
                              context: ContextTypes.DEFAULT_TYPE,
                              is_manager: bool):
    try:
        await create_announce(
            event=event, context=context, is_manager=is_manager
        )
    except Exception as e:
        traceback.print_exc()

    try:
        await edit_dashboard(context=context, new_game=True)
    except Exception as e:
        traceback.print_exc()
