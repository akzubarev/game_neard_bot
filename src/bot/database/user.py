from asgiref.sync import sync_to_async

from apps.users.models import User
from bot.const import DEFAULT_PASSWORD


@sync_to_async()
def get_user(tg_id: int = None, username: str = None):
    user = None
    if tg_id is not None:
        user = User.objects.filter(telegram_id=str(tg_id)).first()
    elif username is not None:
        user = User.objects.filter(username=username).first()
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
