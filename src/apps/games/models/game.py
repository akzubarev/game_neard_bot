from django.db import models

from utils.links import hlink, ready_for_links


class Game(models.Model):
    name = models.CharField(
        max_length=50, verbose_name="name"
    )

    min_players = models.IntegerField(default=2)
    max_players = models.IntegerField(default=2)
    expected_length = models.CharField(
        max_length=10, null=True, blank=True
    )
    recommended_players = models.CharField(
        max_length=10, null=True, blank=True
    )
    link = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    def expected_length_str(self):
        if self.expected_length is None:
            return "?"
        if self.expected_length.isdigit():
            length = int(self.expected_length)
        elif "-" in self.expected_length:
            length = int(self.expected_length.split("-")[-1])
        else:
            length = 100

        if length == 1:
            return f"{self.expected_length} час"
        if length < 5:
            return f"{self.expected_length} часа"
        else:
            return f"{self.expected_length} часов"

    def linked(self):
        return hlink(text=ready_for_links(self.name), link=self.link)
