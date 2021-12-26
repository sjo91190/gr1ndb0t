"""This module houses bot classes"""
import re
import os
import sys
import socket
import requests
from config import get_env, CreateLogger
from utils import time_conversion, alert_msg, initiate_connection
from bot.commands import AllCommands


get_env()
SERVER_CMDS = ["CLEARCHAT", "CLEARMSG", "HOSTTARGET", "NOTICE", "RECONNECT", "ROOMSTATE", "USERNOTICE", "USERSTATE"]


class DiscordAlertBot:
    """This class sends an alert to discord with Twitch stream information"""

    twitch_auth = os.getenv("AUTH_URL")
    twitch_channel = f"https://api.twitch.tv/helix/channels?broadcaster_id={os.getenv('USER_ID')}"

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
                  'name': channel_details.get('broadcaster_name'),
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
        self.greeted = False

        self.server = os.getenv("IRC_SERVER")
        self.port = int(os.getenv("IRC_PORT"))
        self.__token = os.getenv("TWITCH_CHAT_TOKEN")

        self.sock = socket.socket()
        self.sock.connect((self.server, self.port))

        initiate_connection(sock=self.sock, token=self.__token, nickname=nickname, channel=self.channel)

        self.cmds = AllCommands(logger=self.logger, sock=self.sock, channel=self.channel)

    def send_pong(self) -> bool:
        self.sock.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
        self.logger.info("SERVER MSG - PONG SENT")

        return True

    def run(self):
        while True:
            try:
                msg = self.sock.recv(2048).decode("utf-8")

                full_message = re.search(".*;display-name=(.*?);.*;id=(.*?);.*mod=(.*?);.*.tmi.twitch.tv PRIVMSG #(.*) :(.*)", msg)
                reward_id = re.search(";custom-reward-id=(.*?);", msg)

                if reward_id:
                    reward_id = reward_id.group(1)

                if any(cmd in msg for cmd in SERVER_CMDS):
                    self.logger.info(f"SERVER COMMAND - {msg.strip()}")

                elif msg.startswith("PING"):
                    self.logger.info(f"SERVER MSG - {msg.strip()}")
                    self.send_pong()

                elif "JOIN" in msg:
                    joiner = re.search(":(.*?)!", msg)
                    if joiner:
                        joiner = joiner.group(1)
                        self.logger.info(f"CHANNEL JOIN - {joiner}")

                elif "PART" in msg:
                    parter = re.search(":(.*?)!", msg)
                    if parter:
                        parter = parter.group(1)
                        self.logger.info(f"CHANNEL PART - {parter}")

                elif full_message:
                    username = full_message.group(1).strip()
                    msg_id = full_message.group(2).strip()
                    mod_status = full_message.group(3).strip()
                    channel = full_message.group(4).strip()
                    message = full_message.group(5).strip()

                    self.logger.info(f"USER MSG - Channel: {channel} | Mod Status: {mod_status} | Username: {username} | Message: {message}")

                    if not self.greeted:
                        self.cmds.greet(target="ultimatesebs", username=username.lower())
                        self.greeted = True

                    channel_point_reward = self.cmds.get_reward(reward_uuid=reward_id)
                    if channel_point_reward:
                        channel_point_reward(msg=message, sender=username)

                    self.cmds.lurker(msg=message, sender=username)
                    self.cmds.switch_code(msg=message, sender=username)
                    self.cmds.updog(msg=message, sender=username)

                else:
                    self.logger.info(f"UNCATEGORIZED - {msg.strip()}")

            except KeyboardInterrupt:
                self.sock.close()
                sys.exit(0)
