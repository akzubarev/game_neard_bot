import os

# Settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME')
TELEGRAM_MAIN_GROUP = os.getenv('TELEGRAM_MAIN_GROUP')  # Настолошная
TELEGRAM_ADMIN_GROUP = os.getenv('TELEGRAM_ADMIN_GROUP')  # Админка
TELEGRAM_SUPERGROUP_ID = os.getenv('TELEGRAM_SUPERGROUP_ID')  # Анонсы
TELEGRAM_ABOUT_SUB_ID = os.getenv('TELEGRAM_ABOUT_SUB_ID')  # О нас
DEFAULT_PASSWORD = 'rI2UsV96txrOkaLqBlS6'
UPCOMING_RANGE = 14
CONVERSATION_TIMOUT = 60 * 60

# User commands
START_REGISTRATION = 'register'
SIGN_UP = 'sign_up'
GAME_LIST = 'games'
LEAVE = 'leave_game'
CREATE_GAME = 'create_game'
MY_GAMES = 'my_games'
EVENTS = 'events'
EDIT_NOTIFICATIONS = 'edit_notifications'

# Admin commands
DASHBOARD = "dashboard"
EVENT_COUNT = "event_count"
DELETE_ABSENT = "delete_absent"

# Texts
CREATE_GAME_TEXT = f"для создания игры /{CREATE_GAME}"
SIGN_UP_TEXT = f"для записи на игру /{SIGN_UP}"
