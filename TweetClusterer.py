import nltk
import numpy as np
import Database_Handler
import TweetCleaner
import preprocessor as p
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
import string
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime, timedelta
import math
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class TweetClusterer:

    def __init__(self):

        self.tfidf = TfidfVectorizer()
        self.THRESHOLD = 0.1
        self.SIGMA = 2000
        self.current_list_of_clusters = []

    def initialize_clusterer(self, tweets_text_list):
        # cluster_numbers = np.zeros(len(tweets_text_list))
        self.tfidf.fit_transform(tweets_text_list)

    def create_update_clusters(self, tweets_dict):

        tc = TweetCleaner.TweetCleaner()
        tweets_text_list = []
        for tweet_time, Tweet_info  in tweets_dict.items():
            tweets_text_list.append(tc.normalize_tweet(Tweet_info[0]))

        if len(self.current_list_of_clusters) == 0:
            self.initialize_clusterer(tweets_text_list)  # initialize the clusterer module

        # cluster_numbers = np.zeros(len(tweets_text_list))
        tfs = self.tfidf.transform(tweets_text_list)

        for tweet_index, tweet_time in enumerate(tweets_dict.keys()):

            tfidf = tfs[tweet_index]
            n_likes = int(tweets_dict[tweet_time][1])
            n_retweets = int(tweets_dict[tweet_time][2])

            if len(self.current_list_of_clusters) == 0:
                new_cluster = Cluster(tfidf, tweet_time, n_retweets, n_likes, 1, tweets_dict[tweet_time])
                self.current_list_of_clusters.append(new_cluster)
                # cluster_numbers[tweet_index] = 0
            else:
                distances_list = np.zeros(len(self.current_list_of_clusters))
                for cluster_index, cluster in enumerate(self.current_list_of_clusters):
                    distances_list[cluster_index] = (self.calc_similaarity(cluster, tfidf, tweet_time))

                max_index = np.argmax(distances_list)
                if np.max(distances_list) > self.THRESHOLD:
                    self.current_list_of_clusters[max_index].update_cluster(tfidf, tweet_time,
                                                                            n_retweets, n_likes, tweets_dict[tweet_time])

                else:
                    self.current_list_of_clusters.append(Cluster(tfidf, tweet_time, n_retweets,
                                                                 n_likes, 1, tweets_dict[tweet_time]))

        self.remove_inactive_clusters()

    def remove_inactive_clusters(self):

        tobe_removed = np.zeros(len(self.current_list_of_clusters))
        for cluster_index, cluster in enumerate(self.current_list_of_clusters):
            if (datetime.now() - cluster.get_cluster_time_center()).seconds > 86400:
                tobe_removed[cluster_index] = 1

        current_list_backup = self.current_list_of_clusters
        self.current_list_of_clusters = []
        for index in np.where(tobe_removed==0)[0]:
            self.current_list_of_clusters.append(current_list_backup[index])


    def get_most_important_clusters(self):
    #return the two most important clusters

        cluster_importance_list = np.zeros(shape=len(self.current_list_of_clusters))
        for cluster_index, cluster in enumerate(self.current_list_of_clusters):
            cluster_importance_list[cluster_index] = cluster.get_cluster_importance()

        indices = np.argsort(-cluster_importance_list)


        most_important_cluster_index = indices[0]
        second_most_important_cluster_index = indices[1]


        return [self.current_list_of_clusters[most_important_cluster_index],
                self.current_list_of_clusters[second_most_important_cluster_index]]


    def calc_similaarity(self, cluster, new_sample_tfidf, new_sample_time):

        delta = cosine_similarity(cluster.get_cluster_center_tfidf(), new_sample_tfidf)[0][0]

        time_delta = math.exp( - (new_sample_time - cluster.get_cluster_time_center()).total_seconds() ** 2
        / (2 * self.SIGMA**2))

        return time_delta*delta


class Cluster:

    def __init__(self, tfidf, date, n_retweets, n_likes, n_times_tweeted, tweet):
    #n_times_tweeted captures the number of times this tweet or similar ones have been tweeted by different websites

        self.tfidf = tfidf
        self.initial_date = date
        self.n_retweets = n_retweets
        self.n_likes = n_likes
        self.n_times_tweeted = n_times_tweeted
        self.date_dif_list = [0]
        self.tweet_list = [tweet]

    def update_cluster(self, tfidf, date, n_retweets, n_likes, tweet):

        self.tfidf = self.tfidf + tfidf
        self.date_dif_list.append((date - self.initial_date).total_seconds())
        self.n_retweets += n_retweets
        self.n_likes += n_likes
        self.n_times_tweeted += 1
        self.tweet_list.append(tweet)

    def get_cluster_center_tfidf(self):

        return self.tfidf/self.n_times_tweeted

    def get_cluster_time_center(self):

        return self.initial_date + timedelta(0, sum(self.date_dif_list)/ self.n_times_tweeted)


    def get_cluster_importance(self):

        return (self.n_retweets + self.n_likes)

    def should_be_removed(self):

        if (datetime.now() - self.get_cluster_time_center()).seconds > 86400:
            return True
        else:
            return False

    def get_most_important_tweet(self):

        tweets_importance_list = np.zeros(shape=len(self.tweet_list))
        for tweet_index, tweet in enumerate(self.tweet_list):
            tweets_importance_list[tweet_index] = tweet[1] + tweet[2]

        most_important_index = np.argmax(tweets_importance_list)

        return self.tweet_list[most_important_index]

if __name__ == "__main__":

    print "TweetClusterer Test:"

    TC = TweetClusterer()
    db = Database_Handler.Database_Handler()
    tweet_cleaner = TweetCleaner.TweetCleaner()

    tweets_dict = db.read_all_database()

    TC.create_update_clusters(tweets_dict)
