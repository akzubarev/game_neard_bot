import os

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME')

START_REGISTRATION = 'register'
SIGN_UP = 'sign_up'
GAME_LIST = 'games'
LEAVE = 'leave_game'
CREATE_GAME = 'create_game'
MY_GAMES = 'my_games'
EVENTS = 'events'
DEFAULT_PASSWORD = 'rI2UsV96txrOkaLqBlS6'
CREATE_GAME_TEXT = f"для создания игры /{CREATE_GAME}"
SIGN_UP_TEXT = f"для записи на игру /{SIGN_UP}"
