import os
import re

import en_core_web_sm
import tweepy

nlp = en_core_web_sm.load()

CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')

app_auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
oauth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
oauth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

app_api = tweepy.API(app_auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
oapi = tweepy.API(oauth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)



