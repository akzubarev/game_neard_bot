import datetime
import traceback

import bot.database as db
import bot.const as c
from django.utils.timezone import make_aware
from telegram.ext import ContextTypes
from apps.games.models import EventData


async def notify_user(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    user = await db.get_user(tg_id=job.user_id)
    events = await db.get_events(telegram_id=job.user_id)
    upcoming_events = [
        e for e in events if user.remind_hours * 60 >= (
                e.time_tmz - make_aware(datetime.datetime.now())
        ).seconds // 60 >= user.remind_hours * 60 - 30
    ]
    for event in upcoming_events:
        await context.bot.send_message(
            job.chat_id,
            text="\n\n".join([
                "Напоминаем о том, что вы записаны на игру",
                event.other_event_info(),
                f"Чтобы отключить или изменить время напоминаний - /{c.EDIT_NOTIFICATIONS}"
            ])
        )


def remove_job_if_exists(name: str,
                         context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def remove_jobs_for_user(chat_id: str,
                         context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.jobs()
    if not current_jobs:
        return False
    for job in [j for j in current_jobs if j.chat_id == chat_id]:
        job.schedule_removal()
    return True


async def remove_reminder(chat_id, event_id,
                          context: ContextTypes.DEFAULT_TYPE) -> bool:
    job_removed = remove_job_if_exists(f"{chat_id}_{event_id}", context)
    return job_removed


async def remove_reminders(chat_id,
                           context: ContextTypes.DEFAULT_TYPE) -> bool:
    job_removed = remove_jobs_for_user(chat_id=chat_id, context=context)
    return job_removed


async def set_reminder(chat_id, user_id, event: EventData, delay: int,
                       context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(
            callback=notify_user, name=str(f"{chat_id}_{event.id}"),
            when=event.time_tmz.replace(
                hour=event.time_tmz.hour - delay,
                # minute=0, second=0, microsecond=0
            ), chat_id=chat_id, user_id=user_id,
        )
    except Exception as e:
        traceback.print_exc()
