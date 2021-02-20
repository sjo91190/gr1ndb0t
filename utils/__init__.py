"""This module contains various utility functions"""
from datetime import datetime


def time_conversion(iso_timestamp: str) -> str:
    """This function converts an ISO timestamp to an easier format to read

    input: '2021-02-19T00:56:50Z'
    output: 'Feb 18 2021 05:56PM'

    :param iso_timestamp: Input ISO timestamp string
    :type: str
    :return: Returns the formatted timestamp
    :rtype: str
    """

    if iso_timestamp:
        datetime_obj = datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%S%z").astimezone()
        formatted_time = datetime.strftime(datetime_obj, "%b %d %Y %I:%M%p")

        return formatted_time

    return "Not Live"


def alert_msg(data: dict) -> dict:
    """This function builds the embedded link to be sent to Discord

    :param data: A dictionary of data provided from method get_channel
    within class AlertBot
    :type: dict
    :return: Returns a dict payload of formatted data for the embedded link
    :rtype: dict
    """

    alert = {
        "content": f"@everyone, {data['name']} is live now! Come hang out!",
        "embeds": [
            {
                "title": f"{data['title']}",
                "url": f"https://www.twitch.tv/{data['name']}",
                "author": {
                    "name": f"{data['name']} is now streaming"
                },
                "fields": [
                    {
                        "name": "Playing",
                        "value": f"{data['game']}",
                        "inline": False
                    },
                    {
                        "name": "Stream Started (Mountain Time)",
                        "value": f"{data['begin']}",
                        "inline": False
                    },
                ],
                "image": {
                    "url": f"{data['img']}"
                },
                "color": 1127128
            },
        ]
    }

    return alert
