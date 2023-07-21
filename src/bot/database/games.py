from asgiref.sync import sync_to_async

from apps.games.models import Game


@sync_to_async()
def get_games():
    return [(game.name, game.id) for game in Game.objects.all().order_by("name")]


@sync_to_async()
def get_games_linked():
    return [(game.linked(), game.id) for game in Game.objects.all().order_by("name")]


@sync_to_async()
def get_game(name: str = None, game_id: int = None):
    game = None
    if name is not None:
        game = Game.objects.filter(name=name).first()
    elif game_id is not None:
        game = Game.objects.filter(id=game_id).first()
    return game
