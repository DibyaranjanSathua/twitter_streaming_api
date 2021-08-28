"""
File:           config.py
Author:         Dibyaranjan Sathua
Created on:     22/08/21, 3:23 pm
"""
from typing import Dict
import json
import os
from pathlib import Path
from src.exceptions import TwitterStreamingAPIError


def load_secret_file() -> Dict:
    """ Load secret file """
    secret_file = os.environ.get("TWITTER_STREAMING_API_SECRETS")
    if secret_file is None:
        raise TwitterStreamingAPIError("TWITTER_STREAMING_API_SECRETS env var not set")
    secret_file = Path(secret_file)
    if not secret_file.is_file():
        raise TwitterStreamingAPIError(f"Secret file {secret_file} does not exist")
    with open(secret_file, mode="r") as filehandler:
        return json.load(filehandler)


class TwitterConfig:
    """ Load twitter config data from secrets.json file """
    __config_loaded: bool = False
    BEARER: str = ""

    @classmethod
    def init(cls):
        # Avoid loading secret file multiple times
        if cls.__config_loaded:
            return None
        secret_data = load_secret_file()
        twitter_data = secret_data.get("twitter")
        if twitter_data is None:
            raise TwitterStreamingAPIError(f"twitter key is missing in secret file")
        cls.BEARER = twitter_data.get("bearer_token")
        if cls.BEARER is None:
            raise TwitterStreamingAPIError(f"bearer_token is missing in twitter data")
        cls.__config_loaded = True
