from django.contrib import admin

from apps.users.models import PlusOne


@admin.register(PlusOne)
class PlusOneAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'event',
        'value',
    ]
    list_display_links = ["id", "user", "event"]

    search_fields = ['user__username']
    ordering = ['id']
