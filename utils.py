import re
import random

import en_core_web_sm

from config import oapi

nlp = en_core_web_sm.load()

no_clone_replies = ['No clone Found', 'E be like say clone no dey', 'The tweet looks original',
                    'Error 404: Clone not found', 'No copies yet', 'Nothing in sight',
                    'I couldn\'t find clones', 'Clean for now, but the future is not certain',
                    'It\'s as clean as Arsenal\'s trophy cabinet', 'I found nothing', 'I\'m at peace with this tweet',
                    'No clones at this time', 'I\'ve not seen any tweet of this kind', 'No clone in sight',
                    'Aye! Master! It looks clean'
                    ]

clone_list_introductions = ['Possible clones are: \n\n', 'These tweets look similar: \n\n',
                            'I find these results interesting: \n\n', 'The results: \n\n', 'Clones found: \n\n',
                            'I don see some clones: \n\n', 'There are some matches: \n\n',
                            'I think I have seen this before. \n\nLook: \n\n', 'I found something: \n\n',
                            'Some copies found: \n\n', 'Finding these clones gave me joy: \n\n',
                            'These tweets look like clones: \n\n', 'Aye! Master! \n\nLook what I found: \n\n',
                            'Sorry I kept you waiting. \n\nHere you go: \n\n', 'These are possible duplicates: \n\n'
                            ]

clone_list_conclusions = ['\n\nThanks for trusting me', '\n\nThe results may not be very accurate',
                          '\n\nThat\'s all I have for now', '\n\nI\'m glad I was helpful',
                          '\n\nI feel rusty, but those results look "good"', '\n\nI love my job',
                          '\n\nOriginality counts', '\n\nCredits to @HAKSOAT',
                          '\n\nOff-topic, but I want to work at Netflix someday',
                          '\n\nLife is too short, not to be original', '\n\nThe results are nothing but approximates',
                          '\n\nMy AI is just a bunch of if statements', '\n\nKindly, don\'t reply this tweet',
                          '\n\nIt\'s time to go back to sleep'
                          ]

no_reference_replies = ['I can\'t find a reference tweet', 'Wrong usage. There\'s no tweet to find clones for',
                        'Please don\'t at me directly', 'There\'s no target tweet here']


def check_eligibility(mention_text):
    directive = re.search(r'go[ ]*@findclones', mention_text.lower())
    if not directive:
        return False
    return True


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


def send_no_reference_tweet(mentioner):
    tweet_text = random.choice(no_reference_replies)
    oapi.update_status(f'@{mentioner} ' + tweet_text)


def send_tweet(mentioner, mention_id, links, sent_tweet=None):

    if sent_tweet:
        tweet_text = sent_tweet
        oapi.update_status(f'@{mentioner} ' + tweet_text, in_reply_to_status_id=mention_id)
        return tweet_text

    if links:
        link_count = len(links)
        tweet_text = random.choice(clone_list_introductions)

        for link in links[::-1]:
            tweet_text += f"{link_count}: {link}\n"
            link_count -= 1

        tweet_text += random.choice(clone_list_conclusions)

    else:
        tweet_text = random.choice(no_clone_replies)

    if type(tweet_text).__name__ == 'bytes':
        tweet_text = tweet_text.decode('utf-8')
    oapi.update_status(f'@{mentioner} ' + tweet_text, in_reply_to_status_id=mention_id)
    return tweet_text


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
