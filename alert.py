"""Main entry point for the AlertBot"""

from bot import DiscordAlertBot

if __name__ == "__main__":
    bot = DiscordAlertBot()
    bot.send_alert(bot.get_channel())
