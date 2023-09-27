from datetime import datetime


def notify(bot, job):
    pass


def daily_job(bot, update, job_queue):
    """ Running on Mon, Tue, Wed, Thu, Fri = tuple(range(5)) """
    bot.send_message(chat_id=1, text='Setting a daily notifications!')
    t = datetime.time(10, 00, 00, 000000)
    job_queue.run_daily(notify, t, days=tuple(range(5)), context=update)

# updater.dispatcher.add_handler(CommandHandler('notify', daily_job, pass_job_queue=True))
