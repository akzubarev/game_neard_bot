import datetime
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from django.db import models
from django.db.models import Sum
from django.utils.safestring import mark_safe

from config.settings import TIME_ZONE
from utils.time_str import STRF_DATE_TIME, STRF_TIME, ru_weekday


@dataclass
class EventData:
    id: int
    info: str
    comment: str
    time_tmz: datetime.datetime
    game_name: str
    players: list
    plus_ones: dict
    initiator: str
    announce_message: int
    admin_message: int
    link: str

    def simple_str(self):
        weekday = ru_weekday(date_obj=self.time_tmz)
        game_time = self.time_tmz.strftime(STRF_DATE_TIME)
        return f"{self.game_name} - {weekday} {game_time}"

    def players_text(self):
        return '\n'.join([
            f"@{username}" + (f" (+{self.plus_ones[username]})"
                              if self.plus_ones[username] > 0 else "")
            for username in self.players
        ])

    def short_event_info(self):
        return self.info

    def full_event_info(self):
        return f"{self.info}\n{self.players_text()}"

    def other_event_info(self, show_players=True):
        res = self.simple_str()
        if show_players:
            res += f"\n{self.players_text()}"
        return res

    def announce(self, admin=False, is_manager=False):
        if admin is True:
            return f"@{self.initiator} создал игру {self.full_event_info()}"
        else:
            if self.comment is not None:
                if is_manager is False:
                    return "\n\n".join([
                        self.comment,
                        f"@{self.initiator} создал игру {self.short_event_info()}",
                    ])
                else:
                    return "\n\n".join([
                        self.comment, self.short_event_info()
                    ])
            else:
                if is_manager is False:
                    return f"@{self.initiator} создал игру {self.short_event_info()}"
                else:
                    return self.short_event_info()

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
        blank=True
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

    def get_player_count(self):
        plus_ones = self.plus_ones.aggregate(res=Sum("value")).get(
            "res", None
        ) or 0
        return self.players.count() + plus_ones

    def is_full(self):
        return self.get_player_count() == self.game.max_players

    @property
    def time_tmz(self):
        return self.time.astimezone(ZoneInfo(TIME_ZONE))

    def info(self, date=True, show_weekday=True):
        name = self.game.name
        weekday = ru_weekday(date_obj=self.time_tmz)
        game_time = self.time_tmz.strftime(
            STRF_DATE_TIME if date is True else STRF_TIME
        )
        length = f"(~{self.game.expected_length_str()})"
        players = f"{self.get_player_count()}/{self.game.max_players} игроков"
        if date is True:
            if show_weekday is True:
                game_time = f"{weekday} {game_time}"
            res = f"{name} {game_time} {length} {players}"
        else:
            res = f"{game_time} {name} {players} {length}"
        return res

    def get_players(self):
        return [player.username for player in self.players.all()]

    def get_plus_ones(self):
        return {
            player.username: plus_one.value
            if (plus_one := player.plus_ones.filter(
                event_id=self.id
            ).first()) is not None else 0
            for player in self.players.all()
        }

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
            plus_ones=self.get_plus_ones(),
            initiator=self.initiator.username,
            game_name=self.game.name,
            time_tmz=self.time_tmz,
            announce_message=self.announce_message,
            admin_message=self.admin_message,
            link=self.image_link,
            comment=self.comment,
        )
