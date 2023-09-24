from django.contrib import admin
from apps.games.models import Game


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'min_players',
        'max_players',
        'recommended_players',
        'expected_length',
        'link',
    ]
    ordering = ["id"]
