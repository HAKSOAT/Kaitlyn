from config import oapi
import re
import en_core_web_sm

nlp = en_core_web_sm.load()


def remove_emojis(text):
    return text.encode('ascii', 'ignore').decode('ascii')


def remove_links(text):
    return re.sub(r'http(s)*[^ ]+', '', text)


def compile_tweet_link(tweet):
    url = "https://twitter.com/"
    link = url + tweet.author.screen_name + "/status/" + str(tweet.id)
    return link


def get_recency(mention):
    recency_match = re.search(r'\d{4}-\d{2}-\d{2}', mention)
    if recency_match:
        recency = recency_match.group()
        return recency
    else:
        return None


def send_tweet(mentioner, tweet_id, links):
    if links:
        link_count = len(links)
        tweet_text = f"@{mentioner}\nPossible clones are: \n"

        for link in links[::-1]:
            tweet_text += f"{link_count}: {link}\n"
            link_count -= 1

    else:
        tweet_text = f"@{mentioner}\nNo clone in sight!"

    oapi.update_status(tweet_text, in_reply_to_status_id = tweet_id)


def get_most_similar_tweets(fetched_tweets, tweet_details, amount):
    rankings = []
    ids = [tweet_details['id']]
    boundary = 15
    for tweet in fetched_tweets:
        if tweet.id not in ids:
            fetched_tweet_text = nlp(tweet.full_text.lower())
            if -boundary < len(tweet_details['text']) - len(fetched_tweet_text) < boundary:
                if tweet_details['text'].similarity(fetched_tweet_text) > 0.7:
                    rankings.append((tweet, tweet_details['text'].similarity(fetched_tweet_text)))
                    ids.append(tweet.id)
    rankings.sort(key=lambda x: x[1], reverse=True)
    rankings = [tweet for tweet, score in rankings[:amount]]
    return rankings


def save_last_mention_id(filepath, mention_id):
    with open(filepath, 'w') as file:
        file.write(str(mention_id))


def read_last_mention_id(filepath):
    with open(filepath, 'r') as file:
        mention_id = file.read()
        return mention_id
