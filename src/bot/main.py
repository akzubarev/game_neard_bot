import os
import sys

import django
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, \
    Updater

sys.path[0] += '/..'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import bot.const as c
import bot.other as o
import bot.commands as comm
import bot.conversations as convo
from config.logging import LogHelper

logger = LogHelper().logger


def main():
    logger.info("Bot starting")
    app = Application.builder().token(c.TELEGRAM_BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", comm.start))
    app.add_handler(CommandHandler("help", comm.help_prompt))
    app.add_handler(CommandHandler(c.MY_GAMES, comm.my_games))
    app.add_handler(CommandHandler(c.GAME_LIST, comm.games_list))
    app.add_handler(CommandHandler(c.EVENTS, comm.events_list))
    app.add_handler(CommandHandler(c.EVENTS, comm.enable_notifications))
    app.add_handler(CommandHandler(c.EVENTS, comm.disable_notifications))

    # Admin commands
    app.add_handler(CommandHandler(c.DASHBOARD, comm.send_dashboard))
    app.add_handler(CommandHandler(c.EVENT_COUNT, comm.show_event_count))
    app.add_handler(CommandHandler(c.DELETE_ABSENT, comm.delete_absent))

    # Conversation
    app.add_handler(convo.get_sign_up_to_event_handler(), group=1)
    app.add_handler(convo.get_create_event_handler(), group=2)
    app.add_handler(convo.get_leave_event_handler(), group=3)
    app.add_handler(convo.get_registration_handler(), group=4)

    # Messages
    # for group in range(1, 5):
    #     app.add_handler(
    #         MessageHandler(filters.TEXT, o.handle_message), group=group
    #     )

    # Errors
    app.add_error_handler(o.error)
    # Polls
    logger.info("Polling...")
    app.run_polling(poll_interval=1, allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
