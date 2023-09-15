import traceback

from telegram.ext import ContextTypes

from bot import const as c, database as db
from bot.utils import events_list_full, action_button
from .admin import send_to_admin


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


async def edit_dashboard(context: ContextTypes.DEFAULT_TYPE, new_game=False):
    try:
        dashboard = await db.get_dashboard()
        if dashboard.announce_message is None or new_game is True:
            if dashboard.announce_message is not None:
                try:
                    await context.bot.delete_message(
                        chat_id=c.TELEGRAM_MAIN_GROUP,
                        message_id=dashboard.announce_message
                    )
                except Exception as e:
                    traceback.print_exc()
            await create_dashboard(context=context)
        else:
            try:
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
            try:
                await context.bot.edit_message_text(
                    chat_id=c.TELEGRAM_ADMIN_GROUP,
                    message_id=dashboard.admin_message,
                    text=await events_list_full(admin=True, group=True),
                    parse_mode="html"
                )
            except Exception as e:
                traceback.print_exc()
    except Exception as e:
        traceback.print_exc()
