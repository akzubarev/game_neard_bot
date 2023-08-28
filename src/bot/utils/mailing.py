import traceback

from telegram import User
from telegram.ext import ContextTypes

import bot.const as c
import bot.database as db
from apps.games.models import EventData
from bot.utils import events_list_full, action_button


async def send_to_announces(context: ContextTypes.DEFAULT_TYPE, text,
                            keyboard, parse_mode=None) -> int | None:
    message_id = None
    try:
        message_id = (await context.bot.send_message(
            chat_id=c.TELEGRAM_MAIN_GROUP, text=text,
            reply_markup=keyboard, parse_mode=parse_mode,
            message_thread_id=c.TELEGRAM_SUPERGROUP_ID
        )).message_id
    except Exception as e:
        traceback.print_exc()
    return message_id


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


async def create_dashboard(context: ContextTypes.DEFAULT_TYPE):
    try:
        announce_id = await send_to_announces(
            context=context, parse_mode="html",
            text=await events_list_full(admin=False, group=True),
            keyboard=action_button(text="Записаться", command=c.SIGN_UP),
        )
        await db.save_announce_message(
            event_id=(await db.get_dashboard()).id,
            message_id=announce_id, admin=False
        )

    except Exception as e:
        traceback.print_exc()


async def create_dashboard_admin(context: ContextTypes.DEFAULT_TYPE):
    try:
        message_admin_id = await send_to_admin(
            context=context, keyboard=None, parse_mode="html",
            text=await events_list_full(admin=True, group=True),
        )
        await db.save_announce_message(
            event_id=(await db.get_dashboard()).id,
            message_id=message_admin_id, admin=True
        )

    except Exception as e:
        traceback.print_exc()


async def edit_dashboard(context: ContextTypes.DEFAULT_TYPE):
    try:
        dashboard = await db.get_dashboard()
        if dashboard.announce_message is None:
            await create_dashboard(context=context)
        else:
            await context.bot.edit_message_text(
                chat_id=c.TELEGRAM_MAIN_GROUP,
                message_id=dashboard.announce_message,
                text=await events_list_full(admin=False, group=True),
                reply_markup=action_button(
                    text="Записаться", command=c.SIGN_UP
                ), parse_mode="html"
            )
    except Exception as e:
        traceback.print_exc()


async def edit_dashboard_admin(context: ContextTypes.DEFAULT_TYPE):
    try:
        dashboard = await db.get_dashboard()
        if dashboard.admin_message is None:
            await create_dashboard_admin(context=context)
        else:
            await context.bot.edit_message_text(
                chat_id=c.TELEGRAM_ADMIN_GROUP,
                message_id=dashboard.admin_message,
                text=await events_list_full(admin=True, group=True),
                parse_mode="html"
            )
    except Exception as e:
        traceback.print_exc()


async def edit_announce_admin(context: ContextTypes.DEFAULT_TYPE,
                              event: EventData):
    try:
        await context.bot.edit_message_text(
            chat_id=c.TELEGRAM_ADMIN_GROUP,
            message_id=event.admin_message, text=event.announce(admin=True),
        )
    except Exception as e:
        traceback.print_exc()


async def edit_announce(context: ContextTypes.DEFAULT_TYPE, event: EventData):
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
        else:
            await context.bot.delete_message(
                chat_id=c.TELEGRAM_MAIN_GROUP,
                message_id=event.announce_message,
            )
            await db.delete_event(event.id)
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


async def handle_event_change(event: EventData, user: User, join: bool,
                              context: ContextTypes.DEFAULT_TYPE):
    try:
        await edit_announce(context=context, event=event)
        await edit_dashboard(context=context)
    except Exception as e:
        traceback.print_exc()

    try:
        await edit_announce_admin(context=context, event=event)
        await edit_dashboard_admin(context=context)
    except Exception as e:
        traceback.print_exc()

    try:
        await user_game_message(
            context=context, username=user.username, event=event, join=join
        )
    except Exception as e:
        traceback.print_exc()


async def handle_event_create(event: EventData,
                              context: ContextTypes.DEFAULT_TYPE):
    try:
        announce_id = await send_to_announces(
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

    await edit_dashboard(context=context)
    await edit_dashboard_admin(context=context)


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
