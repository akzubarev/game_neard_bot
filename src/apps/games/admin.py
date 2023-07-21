from django.contrib import admin

from apps.games.models import Game, Event


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'min_players',
        'max_players',
        'recommended_players',
        'link',
    ]
    ordering = ["id"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'game',
        'time_fmt',
        'players_fmt',
        'initiator',
        'comment',
    ]
    ordering = ["time"]

    @admin.display(description="Players")
    def players_fmt(self, obj):
        return "\n ".join([str(player) for player in obj.players.all()])

    @admin.display(description='Time', ordering='time')
    def time_fmt(self, obj):
        return obj.time_tmz.strftime("%d.%m.%Y %H:%M")  #:%S
