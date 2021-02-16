import os
import logging
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient



class SlackRupor:
    def __init__(self, token) -> None:
        self.client = WebClient(token=token)
        self.channel = "#lavka"

    def send(self, image_path, message):
        try:
            response = self.client.chat_postMessage(channel=self.channel, text=message)
            assert response["message"]["text"] == message
            response = self.client.files_upload(channels=self.channel, file=image_path)
            logging.info(f"Channel: {self.channel} is notified!")
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            logging.error(f"Got an error: {e.response['error']}")