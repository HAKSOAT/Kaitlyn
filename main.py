import os
import requests

from config import oapi, app_api
from fetcher import TweetFetcher
from utils import nlp, compile_tweet_link, remove_emojis, \
    remove_links, get_recency, get_most_similar_tweets, send_tweet, \
    check_eligibility

import redis
import tweepy

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)


def run():
    # if redis.get('status') == 'locked':
    #     return
    # else:
    #     redis.set('status', 'locked')
    # reload_count = redis.get('reload')
    # if int(reload_count) == 50:
    #     requests.get('https://kaitlyn-clone.herokuapp.com/')
    #     redis.set('reload', 0)
    # else:
    #     if reload_count is None:
    #         redis.set('reload', 1)
    #     else:
    #         redis.set('reload', int(reload_count) + 1)
    print('Starting session')
    last_mention_id = redis.get('id')
    if last_mention_id:
        mentions = oapi.mentions_timeline(int(last_mention_id))[::-1]
    else:
        mentions = oapi.mentions_timeline()[::-1]
    for mention in mentions:
        mentioner = mention.author.screen_name
        mention_id = mention.id
        mention_text = mention.text
        if not check_eligibility(mention_text):
            redis.set('id', mention_id)
            print(mention_text, mentioner, "Not eligible")
            continue
        redis.set('id', mention_id)
        print(mention_text, mentioner, "Eligible")
        tweet = app_api.get_status(mention.in_reply_to_status_id, tweet_mode='extended')
        tweet_id = tweet.id
        if redis.get(tweet_id):
            sent_tweet = redis.get(tweet_id)
            send_tweet(mentioner, mention_id, None, sent_tweet)
            continue
        tweet_text = remove_emojis(tweet.full_text).replace('\n', ' ')
        tweet_text = remove_links(tweet_text)
        tweet_text = nlp(tweet_text.lower())
        tweet_details = {'text': tweet_text, 'id': tweet_id}
        recency = get_recency(mention_text)
        tweet_fetcher = TweetFetcher(tweet_text, recency)
        tweet_fetcher.create_entire_phrase_query()
        tweet_fetcher.create_sentences_query()
        tweet_fetcher.create_words_query()
        fetched_tweets = tweet_fetcher.fetch_tweets()
        similar_tweets = get_most_similar_tweets(fetched_tweets, tweet_details, 3)

        links = []
        for similar_tweet in similar_tweets:
            link = compile_tweet_link(similar_tweet)
            links.append(link)
        try:
            sent_tweet = send_tweet(mentioner, mention_id, links)
            redis.set(tweet_id, sent_tweet)
            print('Tweet Sent to' + f'@{mentioner}')
        except tweepy.error.TweepError as e:
            print(e)

    # redis.set('status', 'opened')
