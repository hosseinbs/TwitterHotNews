import nltk
import numpy as np
import Database_Handler
import preprocessor as p
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
import string

class TweetCleaner:

    def __init__(self):
        pass

    def clean_tweet(self, text):

        p.set_options(p.OPT.URL, p.OPT.EMOJI, p.OPT.NUMBER, p.OPT.MENTION, p.OPT.RESERVED)
        cleaned_text = p.clean(text.encode('utf-8'))

        res = []
        for word in cleaned_text.split():
            if word.strip().lstrip(string.punctuation).strip():
                res.append(word.lower().strip().rstrip(string.punctuation).lstrip(string.punctuation).strip())

        return ' '.join(res)


    def normalize_tweet(self, tweet):

        tweet_words = self.clean_tweet(tweet).split()

        # Remove the stop words.
        text = [word for word in tweet_words if word not in stopwords.words('english')]

        # Create the stemmer.
        stemmer = LancasterStemmer()
        return ' '.join([stemmer.stem(t) for t in text])

    def normalize_all_tweets(self,tweets_list):

        result = []
        for tweet in tweets_list:
            result.append(self.normalize_tweet(tweet))

        return result

if __name__ == "__main__":

    print "TweetCleaner Test:"

    TC = TweetCleaner()

    tweet_text = "RT @usatodaylife: Watch Casey Affleck and Kyle Chandler bicker like brothers in this deleted @MBTSMovie scene https://t.co/uYvvRfNR11 https\u2026"

    print TC.normalize_tweet(tweet_text)

    # print p.tokenize(tweet_text)
