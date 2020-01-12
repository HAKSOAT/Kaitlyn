import operator
import logging

from config import app_api
from utils import ActionType, SearchType

import tweepy

logging.basicConfig(filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class TweetFetcher:
    def __init__(self, text, mode, tweet_date=None, tweet_datetime=None):
        self.text = text
        self.mode = mode
        self.tweet_date = tweet_date
        self.tweet_datetime = tweet_datetime
        self.queries = []
        self.tweets = []

    def format_query(self, query):
        if self.tweet_date and self.mode == ActionType.old.value:
            query = f'"{query}"' + f'until%3A{self.tweet_date}' + "-filter:retweets"
        elif self.tweet_date and self.mode == ActionType.new.value:
            query = f'"{query}"' + f'since%3A{self.tweet_date}' + "-filter:retweets"
        else:
            query = f'"{query}"' + "-filter:retweets"

        return query

    def create_entire_phrase_query(self):
        query = self.text.text.lower()
        formatted_query = self.format_query(query)
        self.queries.append(formatted_query)

    def create_sentences_query(self):
        sentences = []
        for sentence in list(self.text.sents):
            sentences.append(sentence)

        query = ''
        sentences_left = len(sentences)
        for sentence in sentences:
            sentences_left -= 1
            query += f'"{sentence.text.lower()}"'
            if sentences_left > 0:
                query += "%20OR%20"

        query = "(" + query + ")"

        formatted_query = self.format_query(query)
        self.queries.append(formatted_query)

    def create_words_query(self):
        pos = ['PROPN', 'NOUN', 'ADJ']
        dep = ['compound', 'nsubj', 'ROOT']

        query = []

        for word in self.text:
            if word.dep_ in dep or word.pos_ in pos:
                query.append(word.text.lower())

        query = "%20".join(query)

        formatted_query = self.format_query(query)
        self.queries.append(formatted_query)

    def filter_tweets_by_time(self, tweets, comparison):
        filtered_tweets = []
        for tweet in tweets:
            if comparison(self.tweet_datetime, tweet.created_at):
                filtered_tweets.append(tweet)

        return filtered_tweets

    @staticmethod
    def search(queries, search_type):
        tweets = []
        for query in queries:
            try:
                tweets += app_api.search(q=query, include_entities=False, count=100,
                                         result_type=search_type, tweet_mode='extended')
            except tweepy.error.TweepError as e:
                logging.error(e, exc_info=True)

        return tweets

    def fetch_tweets(self):
        if self.mode == ActionType.old.value:
            tweets = TweetFetcher.search(self.queries, SearchType.mixed.value)
            self.tweets = self.filter_tweets_by_time(tweets, operator.gt)

        elif self.mode == ActionType.new.value:
            tweets = TweetFetcher.search(self.queries, SearchType.recent.value)
            self.tweets = self.filter_tweets_by_time(tweets, operator.lt)

        else:
            tweets = TweetFetcher.search(self.queries, SearchType.mixed.value)
            self.tweets = tweets

        return self.tweets


def fetch(tweet_text, mode, tweet_date=None, tweet_datetime=None):
    tweet_fetcher = TweetFetcher(tweet_text, mode, tweet_date, tweet_datetime)
    tweet_fetcher.create_entire_phrase_query()
    tweet_fetcher.create_sentences_query()
    tweet_fetcher.create_words_query()
    fetched_tweets = tweet_fetcher.fetch_tweets()
    return fetched_tweets
