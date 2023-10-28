from django.db import models


class PlusOne(models.Model):
    user = models.ForeignKey(
        to="users.User", related_name="plus_ones",
        on_delete=models.SET_NULL, blank=True, null=True
    )

    event = models.ForeignKey(
        to="games.Event", related_name="plus_ones",
        on_delete=models.SET_NULL, blank=True, null=True
    )

    value = models.SmallIntegerField()

    def __str__(self):
        return f"+{self.value} ({self.user.username})"
