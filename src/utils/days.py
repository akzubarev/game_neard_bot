from datetime import datetime, date

from django.utils.timezone import make_aware


def date_to_datetime(day: date, end=False):
    time = datetime.min.time() if end is False else datetime.max.time()
    return make_aware(datetime.combine(date=day, time=time))


def day_range(day: date = date.today()):
    day_start = date_to_datetime(day)
    day_end = date_to_datetime(day, end=True)
    return day_start, day_end
