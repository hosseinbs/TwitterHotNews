import TweetCleaner
import json
import os
from datetime import datetime, timedelta
import collections

class Database_Handler:

    def __init__(self):

        self.website_list_file = "Database/website_list"
        self.last_datetime = None

    def insert(self, status_list):
    #write initial dataset to file

        with open(self.initial_data_fileName, mode='w') as f:
            json.dump(status_list, f)


    def get_last_updated_times(self):

        last_updated_times = {}
        website_list = json.load(open(self.website_list_file))
        for website, twitter_name in website_list.items():
            last_updated_times[twitter_name] = self.get_last_updated_time_for_website(twitter_name)

        return last_updated_times

    def get_last_updated_time_for_website(self, twitter_name):
    #find the last time we updated the tweets for this website, assuming tweets are stored in a sorted order

        file_name = self.get_database_address(twitter_name)
        if not os.path.exists(file_name):
            return False

        last_line = None
        with open(file_name) as f:
            for line in f:
                last_line = json.loads(line)

        date_elements = last_line['created_at'].split()
        date = datetime.strptime(' '.join(date_elements[0:-2]) + ' ' + date_elements[-1],
                                 '%a %b %d %H:%M:%S %Y')

        return date

    def get_database_address(self, website):
        return "Database/" + website

    def update_db(self, tweets_dict):

        for website, tweets in tweets_dict.items():
            file_name = self.get_database_address(website)
            if len(tweets) == 0:
                continue
            if not os.path.exists(file_name):
                self.dump_json_list_to_file(file_name, tweets, 'w')
            else:
                self.dump_json_list_to_file(file_name, tweets, "a")


    def dump_json_list_to_file(self, file_name, tweets, write_mode):

        with open(file_name, mode=write_mode) as f:
            for tweet in tweets:
                json.dump(tweet, f)
                f.write('\n')

    def read_all_tweets(self):
    #read all tweets from the file

        all_tweets_dict = self.read_all_database()
        sorted_tweets_list = collections.OrderedDict(sorted(all_tweets_dict.items()))

        self.last_datetime = sorted_tweets_list.keys()[-1]
        return sorted_tweets_list

    def read_new_tweets(self):

        all_tweets_dict = self.read_all_database()
        sorted_tweets_list = collections.OrderedDict(sorted(all_tweets_dict.items()))

        if self.last_datetime:

            previous_last_datetime = self.last_datetime
            for key in sorted_tweets_list.keys():
                if key < previous_last_datetime:
                    sorted_tweets_list.pop(key)

        self.last_datetime = sorted_tweets_list.keys()[-1]
        return sorted_tweets_list


    def read_all_database(self):

        all_tweets_dict = {}
        website_list = json.load(open(self.website_list_file))
        for website, twitter_name in website_list.items():
            file_name = self.get_database_address(website)
            if os.path.exists(file_name):
                with open(file_name) as f:
                    for line in f:
                        tweet = json.loads(line)
                        date_elements = tweet['created_at'].split()

                        date = datetime.strptime(' '.join(date_elements[0:-2]) + ' ' + date_elements[-1],
                                                 '%a %b %d %H:%M:%S %Y')

                        all_tweets_dict[date] = ([tweet['text'], tweet['favorite_count'],
                                                  tweet['retweet_count'], tweet['user']['screen_name']])

        return all_tweets_dict

if __name__ == "__main__":

    db = Database_Handler()

    print db.read_all_database()