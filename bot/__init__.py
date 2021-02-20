import os
import requests
from utils import time_conversion, alert_msg


class AlertBot:
    twitch_auth = os.environ.get("AUTH_URL")
    twitch_channel = os.environ.get("CHANNEL_DETAILS") + '"samgrind"'
    twitch_game = os.environ.get("GAME")

    def __init__(self):
        self.__client_id = os.environ.get("TWITCH_ID")
        self.__client_secret = os.environ.get("TWITCH_SECRET")
        self.__discord_hook = os.environ.get("DISCORD_WEBHOOK")

        self.__token = self.__get_token()
        self.__twitch = {}

    def __get_token(self):
        auth_payload = {"client_id": self.__client_id, "client_secret": self.__client_secret,
                        "grant_type": "client_credentials"}
        auth_request = requests.post(url=self.twitch_auth, json=auth_payload)
        print(f"AUTH: {auth_request.status_code}")
        return auth_request.json()['access_token']

    def get_channel(self):
        get_headers = {"client-id": self.__client_id, "Authorization": f"Bearer {self.__token}"}

        channel_request = requests.get(url=self.twitch_channel, headers=get_headers)
        print(f"CHANNEL: {channel_request.status_code}")
        channel_details = channel_request.json()['data'][0]

        game_url = self.twitch_game + channel_details.get("game_id")
        game_request = requests.get(url=game_url, headers=get_headers)
        print(f"GAME: {game_request.status_code}")

        game_details = game_request.json()['data'][0]

        self.__twitch['live'] = channel_details.get("is_live")
        self.__twitch['name'] = channel_details.get('display_name')
        self.__twitch['title'] = channel_details.get('title')
        self.__twitch['begin'] = time_conversion(channel_details.get('started_at'))
        self.__twitch['game'] = game_details.get('name')
        self.__twitch['game_img'] = game_details.get("box_art_url").replace("{width}x{height}", "130x170")

    def send_alert(self):
        post = requests.post(url=self.__discord_hook, json=alert_msg(data=self.__twitch))
        print(f"DISCORD: {post.status_code}")
