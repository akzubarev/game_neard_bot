from zoneinfo import ZoneInfo

from django.db import models

from config.settings import TIME_ZONE
from utils.time_str import STRF_DATE_TIME, STRF_TIME


class Event(models.Model):
    time = models.DateTimeField()
    comment = models.TextField(blank=True, null=True, default="")

    game = models.ForeignKey(
        to="games.Game", related_name="events",
        on_delete=models.CASCADE,
    )

    initiator = models.ForeignKey(
        to="users.User", related_name="initiated_games",
        on_delete=models.SET_NULL, blank=True, null=True
    )

    players = models.ManyToManyField(
        to="users.User", related_name="games"
    )

    def is_full(self):
        return self.players.count() == self.game.max_players

    @property
    def time_tmz(self):
        return self.time.astimezone(ZoneInfo(TIME_ZONE))

    def info(self, date=True):
        name = self.game.name
        game_time = self.time_tmz.strftime(
            STRF_DATE_TIME if date is True else STRF_TIME
        )
        length = f"(~{self.game.expected_length_str()})"
        players = f"{self.players.count()}/{self.game.max_players} игроков"
        if date is True:
            res = f"{name} {game_time} {length} {players}"
        else:
            res = f"{game_time} {name} {players} {length}"
        return res

    def __str__(self):
        game_time = self.time_tmz.strftime(STRF_DATE_TIME)
        return f"{self.game.name} {game_time}"
