import traceback

from telegram.ext import ContextTypes

import bot.const as c
import bot.database as db
from apps.games.models import EventData
from bot.utils import events_list_full, action_button


async def send_to_announces(context: ContextTypes.DEFAULT_TYPE, text,
                            keyboard, parse_mode=None):
    return await context.bot.send_message(
        chat_id=c.TELEGRAM_MAIN_GROUP, text=text,
        reply_markup=keyboard, parse_mode=parse_mode
    )


async def send_to_admin(context: ContextTypes.DEFAULT_TYPE, text, keyboard,
                        parse_mode=None):
    return await context.bot.send_message(
        chat_id=c.TELEGRAM_ADMIN_GROUP, text=text,
        reply_markup=keyboard, parse_mode=parse_mode
    )


async def create_dashboard(context: ContextTypes.DEFAULT_TYPE):
    try:
        announce = await send_to_announces(
            context=context, parse_mode="html",
            text=await events_list_full(admin=False, group=True),
            keyboard=action_button(text="Записаться", command=c.SIGN_UP),
        )
        context.bot_data[c.LAST_DASHBOARD_ANNOUNCES] = announce.message_id

    except Exception as e:
        traceback.print_exc()


async def create_dashboard_admin(context: ContextTypes.DEFAULT_TYPE):
    try:
        message_admin = await send_to_admin(
            context=context, keyboard=None, parse_mode="html",
            text=await events_list_full(admin=True, group=True),
        )
        context.bot_data[c.LAST_DASHBOARD_ADMIN] = message_admin.message_id

    except Exception as e:
        traceback.print_exc()


async def edit_dashboard(context: ContextTypes.DEFAULT_TYPE):
    if c.LAST_DASHBOARD_ANNOUNCES not in context.bot_data:
        await create_dashboard(context=context)
    else:
        await context.bot.edit_message_text(
            chat_id=c.TELEGRAM_MAIN_GROUP,
            message_id=context.bot_data[c.LAST_DASHBOARD_ANNOUNCES],
            text=await events_list_full(admin=False, group=True),
            parse_mode="html"
        )


async def edit_dashboard_admin(context: ContextTypes.DEFAULT_TYPE):
    if c.LAST_DASHBOARD_ADMIN not in context.bot_data:
        await create_dashboard_admin(context=context)
    else:
        await context.bot.edit_message_text(
            chat_id=c.TELEGRAM_ADMIN_GROUP,
            message_id=context.bot_data[c.LAST_DASHBOARD_ADMIN],
            text=await events_list_full(admin=True, group=True),
            parse_mode="html"
        )


async def edit_announce_admin(context: ContextTypes.DEFAULT_TYPE,
                              message_id: int, event: EventData):
    try:
        await context.bot.edit_message_text(
            chat_id=c.TELEGRAM_ADMIN_GROUP, message_id=message_id,
            text=event.announce(admin=True)
        )
    except Exception as e:
        traceback.print_exc()


async def edit_announce(context: ContextTypes.DEFAULT_TYPE, message_id: int,
                        event: EventData):
    try:
        await context.bot.edit_message_text(
            chat_id=c.TELEGRAM_MAIN_GROUP, message_id=message_id,
            text=event.announce(admin=False)
        )
    except Exception as e:
        traceback.print_exc()


async def user_game_message(context: ContextTypes.DEFAULT_TYPE, username: str,
                            event: EventData, join: bool):
    try:
        await context.bot.send_message(
            chat_id=c.TELEGRAM_ADMIN_GROUP,
            text=f"@{username} записался на {event.str}" if join is True
            else f"@{username} вышел из {event.str}"
        )
    except Exception as e:
        traceback.print_exc()


async def send_reminder(event: EventData, context: ContextTypes.DEFAULT_TYPE):
    for username in event.players:
        user = await db.get_user(username=username)
        await context.bot.send_message(
            chat_id=user.telegram_id,
            text="\n".join([
                f"Напоминаем, что вы записаны на {event.str}",
                f"Если планы изменились, покиньте игру с помощью /{c.LEAVE}"
            ]),  # reply_markup=keyboard
        )
