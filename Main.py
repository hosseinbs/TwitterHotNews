
import TweetDownloader as TD
import Database_Handler as DBH
import TweetClusterer as TC
import time
from datetime import datetime
import os
import json

def write_to_file(FINAL_RESULTS_FILE, given_cluster):

    tweet = given_cluster.get_most_important_tweet()[0]
    n_retweets = given_cluster.get_most_important_tweet()[1]
    n_likes = given_cluster.get_most_important_tweet()[2]
    news_agency = given_cluster.get_most_important_tweet()[3]

    result = {}

    result[given_cluster.get_cluster_time_center().strftime("%Y-%m-%d %H:%M")] \
        = {'Tweet':tweet, 'N_retweets':n_retweets, 'N_likes':n_likes, 'Agency':news_agency}
    if os.path.exists(FINAL_RESULTS_FILE):
        with open(FINAL_RESULTS_FILE, "a") as file:
            json.dump(result, file)
            file.write('\n')
    else:
        with open(FINAL_RESULTS_FILE, "w") as file:
            json.dump(result, file)
            file.write('\n')


def reset_file(file_name):

    if(os.path.exists(file_name)):
        os.remove(file_name)

def how_many_left(file_name):
    if not os.path.exists(file_name):
        return 2
    else:
        with open(file_name,'r') as f:
            lines = f.readlines()
            return 2 - len(lines)

if __name__ == '__main__':

    FINAL_RESULTS_FILE = "results.txt"
    IMPORTANCE_THRESHOLD = 25000
    PUSHED_BREAKING_NEWS = False
    datetime.now()

    downloader = TD.TweetDownloader()
    database = DBH.Database_Handler()
    clusterer = TC.TweetClusterer()

    while True:

        current_time = datetime.now()
        if (current_time - current_time.replace(hour=0, minute=0, second=0)).seconds < 1800:
        # the first half an hour after the midnight don't disturb the user, reset the results file
            reset_file(FINAL_RESULTS_FILE)

        last_updated_times = database.get_last_updated_times()

        new_tweets = downloader.download_tweets(last_updated_times)
        print "Downloaded New data!"

        database.update_db(new_tweets)
        print "Updated Database!"

        clusterer.create_update_clusters(database.read_new_tweets())
        print "Updated Clusters!"
        #This involves removing inactive clusters and adding new tweets to the clusters

        important_clusters = clusterer.get_most_important_clusters()
        ##########################
        print "Important news 1: " + important_clusters[0].get_most_important_tweet()[0]
        print "Important news 2: " + important_clusters[1].get_most_important_tweet()[0]
        ##########################


        if(important_clusters[0].get_cluster_importance() > IMPORTANCE_THRESHOLD) \
                and how_many_left(FINAL_RESULTS_FILE) > 0:
            print "A hot news found!!"
            n_tweets_written = write_to_file(FINAL_RESULTS_FILE, important_clusters[0])

        if (important_clusters[1].get_cluster_importance() > IMPORTANCE_THRESHOLD)\
                and how_many_left(FINAL_RESULTS_FILE) > 0:
            print "Another hot news found!!"
            write_to_file(FINAL_RESULTS_FILE, important_clusters[1])

        if (current_time.replace(day=current_time.day+1,hour=0, minute=0, second=0) - current_time).seconds < 3600\
                and how_many_left(FINAL_RESULTS_FILE) > 0:
                # One hour before the midnight, if we haven't yet founf hot news for that day, fill out the file
            reset_file(FINAL_RESULTS_FILE)



        time.sleep(600) # sleep for five minutes



