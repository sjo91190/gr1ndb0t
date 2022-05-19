"""
Main entry point to the chatbot.
Running this script will fire off a discord alert and start up the chatbot
"""

from os import getenv
from config import get_env
from bot import TwitchChatBot, DiscordAlertBot


if __name__ == "__main__":
    get_env()

    discord = DiscordAlertBot()
    discord.send_alert(discord.get_channel())

    bot = TwitchChatBot(channel=getenv("BROADCASTER"), nickname=getenv("BOT_NAME"))
    bot.run()
