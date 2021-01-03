import json
import tweepy
import time

config = json.load(open("config.json", "r"))

# auth = tweepy.OAuthHandler(config['api_key'], config['api_secret'])
# auth.set_access_token(config['access_token'], config['access_secret'])

from twitivity import Event

class StreamEvent(Event):
    CALLBACK_URL: str = "https://yourdomain.com/listener"

    def on_data(self, data: json) -> None:
        print(data)

stream_events = StreamEvent()
stream_events.listen()