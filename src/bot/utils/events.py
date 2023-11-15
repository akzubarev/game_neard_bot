from datetime import timedelta, date

import bot.const as c
import bot.database as db
from utils.time_str import ru_date


async def events_list_full(admin=False, group=False):
    upcoming_range = [
        date.today() + timedelta(days=i) for i in range(c.UPCOMING_RANGE)
    ]
    events = {
        ru_date(day): [
            event.short_event_info() if admin is False
            else event.full_event_info()
            for event in await db.get_events(day=day)
            # , filter_full=not admin)
        ] for day in upcoming_range
    }

    res_text = ["Игры в ближайшее время: "]
    for day_name, day_events in events.items():
        if len(day_events) > 0:
            res_text.append(f"<b>{day_name}</b>\n" + "\n".join(day_events))

    if group is False:
        res_text.append(f"{'-' * 20}\nЗаписаться - /{c.SIGN_UP}")
    return "\n\n".join(res_text)
