"""This module houses bot classes"""
import re
import os
import sys
import socket
import requests
from config import get_env, CreateLogger
from utils import time_conversion, alert_msg

get_env()


class DiscordAlertBot:
    """This class sends an alert to discord with Twitch stream information"""

    twitch_auth = os.getenv("AUTH_URL")
    twitch_channel = os.getenv("CHANNEL_DETAILS") + f'"{os.getenv("USERNAME")}"'
    twitch_game = os.getenv("GAME")

    def __init__(self):
        self.logger = CreateLogger().console_stream()

        self.__client_id = os.getenv("TWITCH_ID")
        self.__client_secret = os.getenv("TWITCH_SECRET")
        self.__discord_hook = os.getenv("DISCORD_WEBHOOK")

        self.__token = self.__get_token()

    def __get_token(self) -> str:
        """This method gets an OAuth token from Twitch to use in authenticated requests
        :return: Returns the OAuth token as a string
        :rtype: str
        """

        auth_payload = {"client_id": self.__client_id, "client_secret": self.__client_secret,
                        "grant_type": "client_credentials"}
        auth_request = requests.post(url=self.twitch_auth, json=auth_payload)
        auth_request.raise_for_status()

        self.logger.info("AUTH: %i", auth_request.status_code)

        return auth_request.json()['access_token']

    def get_channel(self) -> dict:
        """This method gathers information about your Twitch channel and stream

        :return: Returns a dictionary containing key elements from your Twitch channel
        :rtype: dict
        """

        get_headers = {"client-id": self.__client_id, "Authorization": f"Bearer {self.__token}"}

        channel_request = requests.get(url=self.twitch_channel, headers=get_headers)
        channel_request.raise_for_status()

        self.logger.info("CHANNEL: %i", channel_request.status_code)

        channel_details = channel_request.json()['data'][0]

        game_url = self.twitch_game + channel_details.get("game_id")
        game_request = requests.get(url=game_url, headers=get_headers)
        game_request.raise_for_status()

        self.logger.info("GAME: %i", game_request.status_code)

        game_details = game_request.json()['data'][0]
        game_img = game_details.get("box_art_url").replace("{width}x{height}", "130x170")
        game_img = game_img.replace("/./", "/")

        twitch = {'live': channel_details.get("is_live"),
                  'name': channel_details.get('display_name'),
                  'title': channel_details.get('title'),
                  'begin': time_conversion(channel_details.get('started_at')),
                  'game': game_details.get('name'),
                  'img': game_img}

        return twitch

    def send_alert(self, twitch_data: dict) -> None:
        """This method sends the alert with your Twitch info to Discord

        :param twitch_data: The data generated from get_channel
        :type: dict
        """
        post = requests.post(url=self.__discord_hook, json=alert_msg(data=twitch_data))
        post.raise_for_status()

        self.logger.info("DISCORD: %i", post.status_code)


class TwitchChatBot:
    def __init__(self, channel, nickname):
        self.logger = CreateLogger().file_console_stream()
        self.channel = channel
        self.nickname = nickname

        self.server = 'irc.chat.twitch.tv'
        self.port = 6667
        self.__token = os.getenv("TWITCH_CHAT_TOKEN")

        self.sock = socket.socket()
        self.sock.connect((self.server, self.port))

        self.sock.send(f"PASS {self.__token}\r\n".encode("utf-8"))
        self.sock.send(f"NICK {self.nickname}\r\n".encode("utf-8"))
        self.sock.send(f"JOIN #{self.channel}\r\n".encode("utf-8"))
        self.sock.send("CAP REQ :twitch.tv/membership\r\n".encode("utf-8"))
        self.sock.send("CAP REQ :twitch.tv/tags\r\n".encode("utf-8"))
        self.sock.send("CAP REQ :twitch.tv/commands\r\n".encode("utf-8"))

        self.prefix = f"PRIVMSG #{self.channel} :"

    def send_pong(self, msg: str) -> int:
        if msg.startswith("PING"):
            self.sock.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
            self.logger.info("SERVER MSG - PONG SENT")

            return 0

    def del_message(self, msg: str, sender: str, msg_id: str):
        if "!delete" in msg:
            self.sock.send(f"{self.prefix}/delete {msg_id}\r\n".encode("utf-8"))
            self.sock.send(f"{self.prefix}{sender}: MESSAGE DELETED\r\n".encode("utf-8"))

    def ouija_command(self, msg: str, sender: str) -> int:
        if "!ouija" in msg:
            ouija_phrase = msg.split("!ouija")[1].strip()
            self.logger.info(f"COMMAND RECEIVED - !ouija - Sender: {sender}, Phrase: {ouija_phrase}")
            self.sock.send(f"{self.prefix}{sender} submitted phrase: {ouija_phrase}\r\n".encode('utf-8'))

            return 0

    def run(self):
        while True:
            try:
                msg = self.sock.recv(2048).decode("utf-8")
                self.logger.info(msg.strip())
                self.send_pong(msg=msg)

                if "JOIN" in msg:
                    joiner = re.search(":(.*?)!", msg)
                    if joiner:
                        joiner = joiner.group(1)
                        self.logger.info(f"CHANNEL JOIN - {joiner}")

                if "PART" in msg:
                    parter = re.search(":(.*?)!", msg)
                    if parter:
                        parter = parter.group(1)
                        self.logger.info(f"CHANNEL PART - {parter}")

                full_message = re.search("badge-info=;badges=(.*?)/.*;id=(.*?);.*:(.*?)!.*@.*.tmi.twitch.tv PRIVMSG #(.*) :(.*)", msg)

                if full_message:
                    badge = full_message.group(1)
                    msg_id = full_message.group(2)
                    username = full_message.group(3)
                    channel = full_message.group(4)
                    message = full_message.group(5).strip()

                    self.logger.info(f"USER MSG - Username: {username}, Message: {message}")

                    self.ouija_command(msg=message, sender=username)

            except KeyboardInterrupt:
                self.sock.close()
                sys.exit(0)
