import logging


BOT_TOKEN = "token"


logging.basicConfig(
    level=logging.DEBUG,
    format='[{asctime}] #{levelname:8} {filename}: {lineno} - {name} - {message}',
    style='{'
)
