"""This module contains configuration information for the bots"""
import os
import time
import logging
from pathlib import Path
from dotenv import load_dotenv


def greet_data():
    greet_users = ['ultimatesebs', 'shumamofo', 'critterjason', 'youreonthephone', 'samgrind', 'misteryogapants']
    greet_status = {k: False for k in greet_users}

    greet_msg = {'ultimatesebs': 'Sup sebs, you gonna mod today or am I going to do all the work?',
                 'shumamofo': 'Everyone be on your best behavior, Shuma is here!!',
                 'youreonthephone': '@youreonthephone So ur with ur honey and yur making out wen the phone rigns. U anser it n the vioce is "wut r u doing wit my daughter?" U tell ur girl n she say "my dad is ded". THEN WHO WAS PHONE?',
                 'critterjason': '@critterjason jesus christ you scared the shit outta me',
                 'samgrind': 'KEKW streamer writing in his own chat KEKL',
                 'misteryogapants': '@misteryogapants is here? what an INSANE announcement <3'}

    greeter = {"status": greet_status, "msg": greet_msg}

    return greeter


def get_env() -> None:
    """This function reads in your .env file and sets the environment variables

    :return: None
    :rtype: None
    :raises FileNotFoundError: When the .env cannot be located or isn't present
    """

    env_path = Path(os.path.split(__file__)[0], ".env")
    if os.path.isfile(env_path):
        load_dotenv(dotenv_path=env_path)

        return None

    raise FileNotFoundError("Could not locate .env file")


class CreateLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.formatter = logging.Formatter("%(asctime)s - %(message)s", "%m/%d/%Y %I:%M:%S %p %Z")

    def console_stream(self):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        console_handler.setFormatter(self.formatter)

        self.logger.addHandler(console_handler)

        return self.logger

    def file_stream(self):
        now = time.strftime("%Y-%m-%d_%I-%M-%S%p", time.localtime(time.time()))

        file_handler = logging.FileHandler(f"StreamLogs/StreamLogs_{now}.log")
        file_handler.setLevel(logging.INFO)

        file_handler.setFormatter(self.formatter)

        self.logger.addHandler(file_handler)

        return self.logger

    def file_console_stream(self):
        now = time.strftime("%Y-%m-%d_%I-%M-%S%p", time.localtime(time.time()))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        file_handler = logging.FileHandler(f"StreamLogs/StreamLogs_{now}.log")
        file_handler.setLevel(logging.INFO)

        console_handler.setFormatter(self.formatter)
        file_handler.setFormatter(self.formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

        return self.logger

