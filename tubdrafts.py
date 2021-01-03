import json
import tweepy
import time

config = json.load(open("config.json", "r"))

auth = tweepy.OAuthHandler(config['api_key'], config['api_secret'])
auth.set_access_token(config['access_token'], config['access_secret'])

twitter = tweepy.API(auth)

class Listener:
    def __init__(self, twitter):
        self.api = twitter
        
        self.followers = []
        self.seen = []
        self.listening = False

        self.update_followers()
        self.update_seen_messages()

    def get_rate_info(self):
        status = self.api.rate_limit_status()
        info = status['resources']['direct_messages']['/direct_messages/events/list']

        return {
            'remaining': info['remaining'],
            'reset': info['reset'] - time.time()
        }

    def update_followers(self):
        try:
            self.followers = twitter.friends()
        except tweepy.error.RateLimitError:
            print('Follower update rate limit reached, skipping')
    
    def is_follower(self, user_id):
        for user in self.followers:
            if str(user_id) == str(user.id):
                return True
        return False

    def update_seen_messages(self):
        with open(config['message_list'], 'r') as f:
            self.seen = f.read().split('\n')

    def mark_seen(self, *msgs):
        with open(config['message_list'], 'a') as f:
            for msg in msgs:
                if msg not in self.seen:
                    f.write(msg + '\n')
                    self.seen.append(msg)

    def get_new_messages(self):
        msgs = self.api.list_direct_messages()
        to_return = []
        
        for msg in msgs:
            sender = msg.message_create['sender_id']
            follower = self.is_follower(sender)
            if follower and msg.id not in self.seen:
                to_return.append(msg)

        self.mark_seen(*[ m.id for m in msgs ])
        return [ m.message_create['message_data']['text'] for m in to_return ]

    def listen(self):
        self.listening = True
        while self.listening:
            try:
                new = self.get_new_messages()

                rate = self.get_rate_info() # dynamic timing based on rate limit
                timeout = rate['reset'] / rate['remaining']

                print('Tweeting new messages:', new)

                for msg in new:
                    self.api.update_status(msg)

                print('Sleeping for %s seconds (%s calls)' % (timeout, rate['remaining']))

                time.sleep(timeout)
                self.update_followers()
            except tweepy.error.RateLimitError:
                print('DM rate limited reached, sleeping for 10 seconds')
                time.sleep(10)

listener = Listener(twitter)
listener.listen()