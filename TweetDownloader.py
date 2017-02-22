import tweepy, datetime, time
import json
import Database_Handler

class TweetDownloader:


    def __init__(self):
        consumer_key="euA148hGtCuxJ5IkTgpFPmZan"
        consumer_secret="aJf7IWgn5CX1EVFUCjyhmwqX548238CcL9BQRew4hX9GkC6Tp3"
        access_token="102069999-PYltQY4nJIS4DjjaSx1XUUE9f0v42IeuX1y8cMgL"
        access_token_secret="MELDhLJmAgEbdukeZBMOb7uYhlaL7jj1x1VNn6op5mcKZ"

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        self.api = tweepy.API(auth)

    def download_tweets(self, last_updated_times):
    # download initial data

        all_initial_data = {}
        # website_dic = TweetDownloader.read_website_list()

        for key, value in last_updated_times.items():

            initial_dataset = self.download_news_single_website(key, value)
            all_initial_data[key] = initial_dataset

        return all_initial_data


    def download_news_single_website(self, news_agency, last_time_updated):
    #This is to create the initial dataset for each news website

        last_day_downloaded = False
        all_tweets = []
        for page in tweepy.Cursor(self.api.user_timeline, id=news_agency).pages():
            if last_day_downloaded:
                break
            for tweet in page:

                if not last_time_updated:
                    time_dif = datetime.datetime.now() - tweet.created_at
                    if (time_dif).seconds > 7200 and time_dif.days != -1:
                        return all_tweets

                else:

                    time_dif = tweet.created_at - last_time_updated
                    if time_dif.days == -1 or time_dif == 0:
                        return all_tweets

                all_tweets.insert(0,tweet._json)

        return all_tweets


    def download_news_all_websites(self):

        all_initial_data = []
        website_dic = TweetDownloader.read_website_list()
        # already_downloaded = TweetDownloader.initial_downloaded_website_list()
        for key, value in website_dic.items():

            # if value not in already_downloaded:
            initial_dataset = self.download_news_single_website(value)
            all_initial_data = all_initial_data + initial_dataset


        db = Database_Handler.Database_Handler()
        db.insert(all_initial_data)


if __name__ == "__main__":

    td = TweetDownloader()
    last_updated_dcit = {u'msnuk': None,
                         u'bbcnews': None, u'ap': None}

    print td.download_tweets()
    # TweetDownloader.read_website_list()
