class QueryFetcher:
    def __init__(self, text, recency=None):
        self.text = text
        self.recency = recency
        self.queries = []

    def create_entire_phrase_query(self):
        if self.recency:
            query = f'"{self.text.lower()}"' + f'%3A{self.recency}' + "-filter:retweets"
        else:
            query = f'"{self.text.lower()}"' + "-filter:retweets"

        self.queries.append(query)

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

        if self.recency:
            query = query + f'%3A{self.recency}' + "-filter:retweets"
        else:
            query = query + "-filter:retweets"

        self.queries.append(query)

    def create_words_query(self):
        pos = ['PROPN', 'NOUN', 'ADJ']
        dep = ['compound', 'nsubj', 'ROOT']

        query = []

        for word in self.text:
            if word.dep_ in dep or word.pos_ in pos:
                query.append(word.text.lower())

        if self.recency:
            query = "%20".join(query) + f'%3A{self.recency}' + "-filter:retweets"
        else:
            query = "%20".join(query) + "-filter:retweets"

        self.queries.append(query)