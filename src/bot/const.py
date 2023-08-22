import os

# Settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_USERNAME = f"@https://t.me/{os.getenv('TELEGRAM_BOT_USERNAME')}"
BOT_LINK = os.getenv('TELEGRAM_BOT_USERNAME')
TELEGRAM_MAIN_GROUP = os.getenv('TELEGRAM_MAIN_GROUP')
TELEGRAM_ADMIN_GROUP = os.getenv('TELEGRAM_ADMIN_GROUP')
TELEGRAM_SUPERGROUP_ID = os.getenv('TELEGRAM_SUPERGROUP_ID')
DEFAULT_PASSWORD = 'rI2UsV96txrOkaLqBlS6'
UPCOMING_RANGE = 14

# User commands
START_REGISTRATION = 'register'
SIGN_UP = 'sign_up'
GAME_LIST = 'games'
LEAVE = 'leave_game'
CREATE_GAME = 'create_game'
MY_GAMES = 'my_games'
EVENTS = 'events'

# Admin commands
DASHBOARD = "dashboard"

# Data keys
LAST_DASHBOARD_ANNOUNCES = "last_dashboard_announces"
LAST_DASHBOARD_ADMIN = "last_dashboard_admin"
LAST_ANNOUNCES_ANNOUNCES = "last_announces_announces"
LAST_ANNOUNCES_ADMIN = "last_announces_admin"

# Texts
CREATE_GAME_TEXT = f"для создания игры /{CREATE_GAME}"
SIGN_UP_TEXT = f"для записи на игру /{SIGN_UP}"
