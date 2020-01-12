import logging

from app.config import oapi, app_api, redis, LAST_MENTION_ID
from app.fetcher import fetch
from app.utils import compile_tweet_link, process_tweet_text, get_most_similar_tweets, send_tweet, \
    get_action, ActionType, send_no_reference_tweet

import tweepy


logging.basicConfig(filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def run():
    logging.info('Starting session')
    last_mention_id = redis.get('id') or LAST_MENTION_ID
    logging.info(f'Last mention id: {last_mention_id}')

    if last_mention_id:
        mentions = oapi.mentions_timeline(int(last_mention_id))[::-1]
    else:
        mentions = oapi.mentions_timeline()[::-1]

    for mention in mentions:
        # Get mention details
        mentioner = mention.author.screen_name
        mention_id = mention.id
        mention_text = mention.text

        # Check if mention is a call to action
        action = get_action(mention_text)
        if not action:
            redis.set('id', mention_id)
            logging.info(f'{mention_text} by {mentioner} is not valid')
            continue

        # Get tweet details
        redis.set('id', mention_id)
        logging.info(f'{mention_text} by {mentioner} is valid')
        try:
            tweet = app_api.get_status(mention.in_reply_to_status_id, tweet_mode='extended')
        except tweepy.error.TweepError as e:
            logging.error(e, exc_info=True)
            if e.args[0][0]['code'] == 144:
                send_no_reference_tweet(mentioner, mention_id)
            continue

        tweet_id = tweet.id
        tweet_datetime = tweet.created_at
        tweet_date = tweet_datetime.strftime('%Y-%m-%d')

        # Check if clone has been requested of tweet before
        if redis.get(tweet_id):
            sent_tweet = redis.get(f'{action}: {tweet_id}')
            send_tweet(mentioner, mention_id, None, sent_tweet)
            continue

        tweet_text = process_tweet_text(tweet.full_text)
        tweet_details = {'text': tweet_text, 'id': tweet_id}

        if action == ActionType.old.value:
            fetched_tweets = fetch(tweet_text, action, tweet_date, tweet_datetime)
        elif action == ActionType.new.value:
            fetched_tweets = fetch(tweet_text, action, tweet_date, tweet_datetime)
        else:
            fetched_tweets = fetch(tweet_text, action)

        similar_tweets = get_most_similar_tweets(fetched_tweets, tweet_details, 3)

        links = []

        for similar_tweet in similar_tweets:
            link = compile_tweet_link(similar_tweet)
            links.append(link)

        try:
            sent_tweet = send_tweet(mentioner, mention_id, links)
            cached_tweet_timeout = 60 * 60
            redis.set(f'{action}: {tweet_id}', sent_tweet, ex=cached_tweet_timeout)
            logging.info(f'Tweet Sent to @{mentioner}')
        except tweepy.error.TweepError as e:
            logging.error(e, exc_info=True)
