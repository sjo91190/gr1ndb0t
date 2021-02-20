"""This module houses bot classes"""
import os
import requests
from config import get_env, stream_logger
from utils import time_conversion, alert_msg

logger = stream_logger()


class AlertBot:
    """This class sends an alert to discord with Twitch stream information"""
    get_env()

    twitch_auth = os.getenv("AUTH_URL")
    twitch_channel = os.getenv("CHANNEL_DETAILS") + f'"{os.getenv("USERNAME")}"'
    twitch_game = os.getenv("GAME")

    def __init__(self):

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

        logger.info("AUTH: %i", auth_request.status_code)

        return auth_request.json()['access_token']

    def get_channel(self) -> dict:
        """This method gathers information about your Twitch channel and stream

        :return: Returns a dictionary containing key elements from your Twitch channel
        :rtype: dict
        """

        get_headers = {"client-id": self.__client_id, "Authorization": f"Bearer {self.__token}"}

        channel_request = requests.get(url=self.twitch_channel, headers=get_headers)
        channel_request.raise_for_status()

        logger.info("CHANNEL: %i", channel_request.status_code)

        channel_details = channel_request.json()['data'][0]

        game_url = self.twitch_game + channel_details.get("game_id")
        game_request = requests.get(url=game_url, headers=get_headers)
        game_request.raise_for_status()

        logger.info("GAME: %i", game_request.status_code)

        game_details = game_request.json()['data'][0]

        twitch = {'live': channel_details.get("is_live"),
                  'name': channel_details.get('display_name'),
                  'title': channel_details.get('title'),
                  'begin': time_conversion(channel_details.get('started_at')),
                  'game': game_details.get('name'),
                  'img': game_details.get("box_art_url").replace("{width}x{height}", "130x170")}

        return twitch

    def send_alert(self, twitch_data: dict) -> None:
        """This method sends the alert with your Twitch info to Discord

        :param twitch_data: The data generated from get_channel
        :type: dict
        """
        post = requests.post(url=self.__discord_hook, json=alert_msg(data=twitch_data))
        post.raise_for_status()

        logger.info("DISCORD: %i", post.status_code)
