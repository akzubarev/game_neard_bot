from datetime import datetime, date, timedelta

from asgiref.sync import sync_to_async
from django.utils.timezone import make_aware

from apps.games.models import Game, Event
from apps.users.models import User
from utils.days import day_range


@sync_to_async()
def save_event(game_name: str, date_time: datetime,
               comment: str, user_username: str):
    save_event_sync(
        game_name=game_name, date_time=date_time, comment=comment,
        user_username=user_username
    )


def save_event_sync(game_name: str, date_time: datetime,
                    comment: str, user_username: str):
    user = User.objects.filter(username=user_username).first()
    game = Game.objects.filter(name=game_name).first()
    event = Event.objects.create(
        game=game, time=date_time, initiator=user,
        comment=comment
    )
    event.players.add(user)


@sync_to_async()
def get_events(username: str = None, filter_full=False, exclude=False,
               day: date = None):
    now = make_aware(datetime.now())
    events = Event.objects.filter(time__gte=now).order_by("time")
    if username is not None:
        if exclude is True:
            events = events.exclude(players__username=username)
        else:
            events = events.filter(players__username=username)
    if day is not None:
        events = events.filter(time__range=day_range(day))
    return [
        (event.info(date=day is None), event.id) for event in events
        if filter_full is False or not event.is_full()
    ]


@sync_to_async()
def get_event(event_id: int):
    return Event.objects.filter(id=event_id).first()


@sync_to_async()
def get_event_str(event_id: int):
    return str(Event.objects.filter(id=event_id).first())


@sync_to_async()
def get_event_players(event_id: int):
    event = Event.objects.filter(id=event_id).first()
    return [f"@{player.username}" for player in event.players.all()]


@sync_to_async()
def add_player(event_id: str, player_username: str):
    event = Event.objects.filter(id=event_id).first()
    player = User.objects.filter(username=player_username).first()
    event.players.add(player)


@sync_to_async()
def remove_player(event_id: str, player_username: str):
    event = Event.objects.filter(id=event_id).first()
    player = User.objects.filter(username=player_username).first()
    event.players.remove(player)
