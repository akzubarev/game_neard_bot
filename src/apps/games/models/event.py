import datetime
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from django.db import models
from django.utils.safestring import mark_safe

from config.settings import TIME_ZONE
from utils.time_str import STRF_DATE_TIME, STRF_TIME


@dataclass
class EventData:
    id: int
    info: str
    comment: str
    time_tmz: datetime.datetime
    game_name: str
    players: list
    initiator: str
    announce_message: int
    admin_message: int
    link: str

    def simple_str(self):
        game_time = self.time_tmz.strftime(STRF_DATE_TIME)
        return f"{self.game_name} {game_time}"

    def players_text(self):
        return '\n'.join([f"@{username}" for username in self.players])

    def short_event_info(self):
        return self.info

    def full_event_info(self):
        return f"{self.info}\n{self.players_text()}"

    def other_event_info(self):
        return f"{self.simple_str()}\n{self.players_text()}"

    def announce(self, admin=False):
        if admin is True:
            return f"@{self.initiator} создал игру {self.full_event_info()}"
        else:
            if self.comment is not None:
                return "\n\n".join([
                    self.comment,
                    f"@{self.initiator} создал игру {self.short_event_info()}",
                ])
            else:
                return f"@{self.initiator} создал игру {self.short_event_info()}"

    def photo_by_link(self):
        return mark_safe(f'<img src="/{self.link}" width="300" />')


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
        to="users.User", related_name="games",
        blank=True, null=True
    )

    announce_message = models.IntegerField(
        blank=True, null=True,
    )

    admin_message = models.IntegerField(
        blank=True, null=True,
    )

    image_link = models.CharField(
        max_length=1000,
        blank=True, null=True
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

    def get_players(self):
        return [f"{player.username}" for player in self.players.all()]

    def __str__(self):
        game_time = self.time_tmz.strftime(STRF_DATE_TIME)
        return f"{self.game.name} {game_time}"

    def photo_by_link(self):
        return mark_safe(f'<img src="/{self.image_link}" width="300" />')

    def data(self, date=True):
        return EventData(
            id=self.id,
            info=self.info(date=date),
            players=self.get_players(),
            initiator=self.initiator.username,
            game_name=self.game.name,
            time_tmz=self.time_tmz,
            announce_message=self.announce_message,
            admin_message=self.admin_message,
            link=self.image_link,
            comment=self.comment,
        )
