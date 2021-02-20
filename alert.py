"""Main entry point for the AlertBot"""

from bot import AlertBot

if __name__ == "__main__":
    bot = AlertBot()
    bot.send_alert(bot.get_channel())
