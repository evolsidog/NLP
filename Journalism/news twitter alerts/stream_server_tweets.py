import tweepy
from tweepy.auth import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamingClient
import socket
import json
import yaml

# https://medium.com/analytics-vidhya/exploring-twitter-streaming-data-using-python-and-spark-3f4f189ec660

# tweepy v4.12

# Credentials and connectors
with open('credentials.yaml') as f:
    twitter_credentials = yaml.load(f, Loader=yaml.loader.SafeLoader)

api_key = twitter_credentials['API Key']
api_key_secret = twitter_credentials['Api Key Secret']
bearer_token = twitter_credentials['Bearer Token']

# v1.1 API
auth = tweepy.OAuth2BearerHandler(bearer_token)
api = tweepy.API(auth)

# v2.0 API
client = tweepy.Client(bearer_token=bearer_token)

class TweetsClient(StreamingClient):

    def __init__(self, bearer_token, csocket):
        super().__init__(bearer_token=bearer_token)
        self.client_socket = csocket

    # override
    def on_data(self, data):
        try:
            message = json.loads(data)
            print(message['data']['text'].encode('utf-8'))
            self.client_socket.send(message['data']['text'].encode('utf-8'))
            
            return True
        except BaseException as e:
            print(f"Error on_data: {e}")
        return True

    def on_errors(self, status):
        print(status)
        return True

def send_tweets(c_socket, topic):
    twitter_stream = TweetsClient(bearer_token=bearer_token,csocket=c_socket)
    twitter_stream.add_rules(tweepy.StreamRule(topic)) #we are interested in this topic.
    twitter_stream.filter()

if __name__ == "__main__":
    new_skt = socket.socket()
    host = "127.0.0.1"
    port = 5555
    new_skt.bind((host, port))

    print(f"Now listening on port: {port}")

    new_skt.listen(5) # 5 unaccepted connections permited before refusing new connections
    c, addr = new_skt.accept() # establish connection with client. It return socket object and address

    print(f"Received request from: {addr}")
    send_tweets(c, topic="football")