from datetime import datetime, date
from typing import List

from asgiref.sync import sync_to_async
from django.utils.timezone import make_aware

from apps.games.models import Game, Event
from apps.games.models.event import EventData
from apps.users.models import User, PlusOne
from utils.days import day_range


@sync_to_async()
def save_event(game_name: str, date_time: datetime, join: bool,
               comment: str, user_telegram_id: str, link: str):
    return save_event_sync(
        game_name=game_name, date_time=date_time, comment=comment,
        user_telegram_id=user_telegram_id, link=link, join=join
    )


def save_event_sync(game_name: str, date_time: datetime, join: bool,
                    comment: str, user_telegram_id: str, link: str):
    user = User.objects.filter(telegram_id=user_telegram_id).first()
    game = Game.objects.filter(name=game_name).first()
    event = Event.objects.create(
        game=game, time=date_time, initiator=user,
        comment=comment, image_link=link
    )
    if join is True:
        event.players.add(user)
    return event.data()


@sync_to_async()
def get_events(telegram_id: id = None, filter_full=False, exclude=False,
               day: date = None) -> List[EventData]:
    now = make_aware(datetime.now())
    events = Event.objects.filter(time__gte=now).order_by("time")
    if telegram_id is not None:
        if exclude is True:
            events = events.exclude(players__telegram_id=telegram_id)
        else:
            events = events.filter(players__telegram_id=telegram_id)
    if day is not None:
        events = events.filter(time__range=day_range(day))
    return [
        event.data(date=date) for event in events
        if filter_full is False or not event.is_full()
    ]


@sync_to_async()
def get_event(event_id: int) -> EventData:
    return Event.objects.filter(id=event_id).first().data()


@sync_to_async()
def delete_event(event_id: int) -> bool:
    event = Event.objects.filter(id=event_id).first()
    if event.players.count() == 0:
        event.delete()
        return True
    return False


@sync_to_async()
def get_dashboard() -> EventData:
    return Event.objects.filter(id=1).first().data()


@sync_to_async()
def add_player(event_id: str, player_tg_id: int, plus_one: int | None = None):
    event = Event.objects.filter(id=event_id).first()
    player = User.objects.filter(telegram_id=player_tg_id).first()
    event.players.add(player)
    if plus_one is not None:
        PlusOne.objects.create(event=event, user=player, value=plus_one)
    return event.data()


@sync_to_async()
def remove_player(event_id: str, player_tg_id: int):
    event = Event.objects.filter(id=event_id).first()
    player = User.objects.filter(telegram_id=player_tg_id).first()
    event.players.remove(player)
    plus_one = event.plus_ones.filter(user__id=player.id).first()
    if plus_one is not None:
        plus_one.delete()
    return event.data()


@sync_to_async()
def save_announce_message(event_id: int, message_id: int, admin=False):
    event = Event.objects.filter(id=event_id).first()
    if admin is True:
        event.admin_message = message_id
    else:
        event.announce_message = message_id
    event.save()
