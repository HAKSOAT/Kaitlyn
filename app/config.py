import os
import re

import tweepy
import en_core_web_sm
from dotenv import load_dotenv
import redis

load_dotenv()

CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')

app_auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
oauth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
oauth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

app_api = tweepy.API(app_auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
oapi = tweepy.API(oauth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)

nlp = en_core_web_sm.load()

LAST_MENTION_ID = os.getenv('LAST_MENTION_ID')

