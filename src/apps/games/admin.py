from django.contrib import admin
from django.utils.html import format_html

from apps.games.models import Game, Event


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


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'game',
        'time_fmt',
        'players_fmt',
        'initiator',
        'comment',
        'announce_message',
        'admin_message',
    ]
    list_display_links = [
        'game', 'initiator'
    ]
    ordering = ["-time"]

    @admin.display(description="Players")
    def players_fmt(self, obj):
        return format_html(
            "\n<br>".join([str(player) for player in obj.players.all()])
        )

    @admin.display(description='Time', ordering='time')
    def time_fmt(self, obj):
        return obj.time_tmz.strftime("%d.%m.%Y %H:%M")  #:%S
