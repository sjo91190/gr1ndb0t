from datetime import datetime


def time_conversion(iso_timestamp: str) -> str:

    if iso_timestamp:
        datetime_obj = datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%S%z").astimezone()
        formatted_time = datetime.strftime(datetime_obj, "%b %d %Y %I:%M%p")

        return formatted_time

    return "Not Live"


def alert_msg(data: dict) -> dict:

    alert = {
        "content": f"@everyone, {data['name']} is live now! Come hang out!",
        "embeds": [
            {
                "title": f"{data['title']}",
                "url": "https://www.twitch.tv/samgrind",
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
                    "url": f"{data['game_img']}"
                },
                "color": 1127128
            },
        ]
    }

    return alert
