import traceback

from telegram.ext import ContextTypes

from apps.games.models import EventData
from bot import const as c, database as db


async def send_to_admin(context: ContextTypes.DEFAULT_TYPE, text, keyboard,
                        parse_mode=None) -> int | None:
    message_id = None
    try:
        message_id = (await context.bot.send_message(
            chat_id=c.TELEGRAM_ADMIN_GROUP, text=text,
            reply_markup=keyboard, parse_mode=parse_mode
        )).message_id

    except Exception as e:
        traceback.print_exc()
    return message_id


async def user_game_message(context: ContextTypes.DEFAULT_TYPE, username: str,
                            event: EventData, join: bool):
    try:
        if join is True:
            # f"@{username} записался на {event.simple_str()}"
            pass
        else:
            await context.bot.send_message(
                chat_id=c.TELEGRAM_ADMIN_GROUP,
                text=f"@{username} вышел из {event.simple_str()}"
            )
    except Exception as e:
        traceback.print_exc()


async def send_reminder(event: EventData, context: ContextTypes.DEFAULT_TYPE):
    for username in event.players:
        user = await db.get_user(username=username)
        await context.bot.send_message(
            chat_id=user.telegram_id,
            text="\n".join([
                f"Напоминаем, что вы записаны на {event.simple_str()}",
                f"Если планы изменились, покиньте игру с помощью /{c.LEAVE}"
            ]),  # reply_markup=keyboard
        )
