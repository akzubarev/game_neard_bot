from datetime import datetime, date, timedelta

# strf_format = '%d.%m.%Y %H:%M'
STRF_DATE_TIME = '%d.%m %H:%M'
STRF_TIME = '%H:%M'
STRF_WEEKDAY = '%A %d.%m'

days_dict = {
    "Monday": "Понедельник",
    "Tuesday": "Вторник",
    "Wednesday": "Среда",
    "Thursday": "Четверг",
    "Friday": "Пятница",
    "Saturday": "Суббота",
    "Sunday": "Воскресенье",
}


def ru_date(date_obj: date):
    weekday, time = date_obj.strftime(STRF_WEEKDAY).split(" ")
    return f"{days_dict.get(weekday)} {time}"


def ru_weekday(date_obj: date):
    weekday, _ = date_obj.strftime(STRF_WEEKDAY).split(" ")
    return days_dict.get(weekday)


def readable_time(time: datetime | date | timedelta,
                  show_date=False, seconds=True):
    res = ""
    if isinstance(time, datetime):
        date_str = "%d.%m.%Y, " if show_date is True else ""
        seconds_str = ":%S" if seconds is True else ""
        format_string = f'{date_str}%H:%M{seconds_str}'
        res = time.strftime(format_string)
    elif isinstance(time, date):
        date_str = "%d.%m.%Y"
        res = time.strftime(date_str)
    elif isinstance(time, timedelta):
        res = readable_timedelta(time, ago=False)
    return res


def readable_timedelta(time_delta: datetime | timedelta, ago=True):
    if isinstance(time_delta, datetime):
        time_delta = datetime.now() - time_delta
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    days = f"{time_delta.days} days, " if time_delta.days > 0 else ""
    if hours < 10: hours = f"0{hours}"
    if minutes < 10: minutes = f"0{minutes}"
    if seconds < 10: seconds = f"0{seconds}"

    if time_delta.seconds == 0:
        seconds += f'.{str(time_delta.microseconds)[:2]}'

    ago = " ago" if ago is True else ""
    res = f'{days}{hours}:{minutes}:{seconds}{ago}'
    # res = f'{str(now() - time).split(".", 2)[0]} ago'
    return res
