from config import oapi, app_api
from fetcher import TweetFetcher
from utils import nlp, compile_tweet_link, remove_emojis, \
    remove_links, get_recency, get_most_similar_tweets, send_tweet, \
    read_last_mention_id, save_last_mention_id

while True:
    last_mention_id = read_last_mention_id('last_mention_id.txt')
    if last_mention_id:
        mentions = oapi.mentions_timeline(int(last_mention_id))[::-1]
    else:
        mentions = oapi.mentions_timeline()[::-1]
    for mention in mentions:
        mentioner = mention.author.screen_name
        mention_id = mention.id
        mention_text = mention.text
        tweet = app_api.get_status(mention.in_reply_to_status_id, tweet_mode='extended')
        tweet_id = tweet.id
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
        similar_tweets = get_most_similar_tweets(fetched_tweets, tweet_details, 5)

        links = []
        for similar_tweet in similar_tweets:
            link = compile_tweet_link(similar_tweet)
            links.append(link)
        send_tweet(mentioner, mention_id, links)
        save_last_mention_id('last_mention_id.txt', mention_id)
