"""This module contains configuration information for the bots"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv


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


def stream_logger() -> logging.Logger:
    """This function returns a logger with a console handler

    :return: Returns the logger.Logger object
    :rtype: logger.Logger
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    logger.addHandler(console)

    return logger
