from os import getenv
from config import get_env
from bot import TwitchChatBot


if __name__ == "__main__":
    get_env()
    bot = TwitchChatBot(channel=getenv("BROADCASTER"), nickname=getenv("BOT_NAME"))
    bot.run()
