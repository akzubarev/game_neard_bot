#      ___   ___  ____
#     / _ | / _ \/  _/
#    / __ |/ ___// /
#   /_/ |_/_/ _/___/
#   __ ______/ /__
#  / // / __/ (_-<
#  \_,_/_/ /_/___/

from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns = staticfiles_urlpatterns() + urlpatterns
