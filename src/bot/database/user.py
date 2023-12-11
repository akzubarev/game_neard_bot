from asgiref.sync import sync_to_async
from django.db.models import Count

from apps.users.models import User
from bot.const import DEFAULT_PASSWORD


@sync_to_async()
def get_user(tg_id: int = None, chat_id: str = None, username: str = None):
    return get_user_sync(tg_id=tg_id, chat_id=chat_id, username=username)


@sync_to_async()
def get_users():
    return User.objects.all()


def get_user_sync(tg_id: int = None, chat_id: int = None,
                  username: str = None):
    user = None
    if tg_id is not None:
        user = User.objects.filter(telegram_id=str(tg_id)).first()
    elif username is not None:
        user = User.objects.filter(username=username).first()
    if user is not None and user.telegram_chat_id is None and chat_id is not None:
        user.telegram_chat_id = chat_id
        user.save()
    return user


@sync_to_async()
def user_is_manager(tg_id: int):
    manager = False
    user = User.objects.filter(telegram_id=str(tg_id)).first()
    if user is not None:
        manager = (
                user.is_superuser or user.is_staff or
                user.groups.filter(name="Managers").first() is not None
        )
    return manager


@sync_to_async()
def set_user_tg_id(tg_id: int, username: str):
    user = User.objects.filter(username=username).first()
    user.telegram_id = tg_id
    user.save()


@sync_to_async()
def create_user(tg_id: int, first_name: str, last_name: str, username: str):
    User.objects.create(
        first_name=first_name, last_name=last_name,
        telegram_id=tg_id, username=username,
        password=DEFAULT_PASSWORD
    )


@sync_to_async()
def get_user_event_count(tg_id: int):
    event_count = User.objects.filter(tg_id=tg_id).annotate(
        event_count=Count("games")
    ).order_by("-event_count").values("username", "event_count")[0]
    return event_count.get("event_count")


@sync_to_async()
def get_event_count(at_least_one=None):
    event_count = User.objects.all().annotate(
        event_count=Count("games")
    ).order_by("-event_count")
    if at_least_one is True:
        event_count = event_count.filter(event_count__gt=0)
    elif at_least_one is False:
        event_count = event_count.filter(event_count=0)
    return [
        (data.get("username"), data.get("event_count"))
        for data in event_count.values("username", "event_count")
    ]


@sync_to_async()
def delete_zero():
    users = User.objects.all().annotate(
        event_count=Count("games")
    ).order_by("-event_count").filter(event_count=0)
    users.delete()


@sync_to_async()
def enable_notifier(tg_id: int = None, username: str = None):
    user = get_user_sync(tg_id=tg_id, username=username)
    user.remind_enabled = True
    user.save()
    return user


@sync_to_async()
def disable_notifier(tg_id: int = None, username: str = None):
    user = get_user_sync(tg_id=tg_id, username=username)
    user.remind_enabled = False
    user.save()
    return user


@sync_to_async()
def change_remind_hours(hours: int, tg_id: int = None, username: str = None):
    user = get_user_sync(tg_id=tg_id, username=username)
    user.remind_hours = hours
    user.save()
    return user
