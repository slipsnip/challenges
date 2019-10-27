from collections import namedtuple
from pathlib import Path
import csv
import tweepy

from config import CONSUMER_KEY, CONSUMER_SECRET
from config import ACCESS_TOKEN, ACCESS_SECRET

DEST_DIR = 'data'
EXT = 'csv'
MAX_TWEETS = 100

Tweet = namedtuple('Tweet', 'id_str created_at text')


class API():
    # allow only one instance of Wrapper
    class __API(tweepy.API):

        def __init__(self, auth):
            super().__init__(auth)

    def __new__(cls):
        if not hasattr(cls, 'api'):
            oauth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            oauth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
            API.api = cls.__API(oauth)
        return API.api


class TweepyCache(object):
    def __init__(self, user_handle, max_id=-1):
        self._api = API()
        user = self._api.get_user(user_handle)
        self._user_id = user.id

        self._filename = Path(DEST_DIR, user.id_str + EXT)
        self._tweets = []
        # number of tweets user has
        num_tweets_of_user = user.statuses_count
        # number of tweets to get, maximum MAX_TWEETS
        self._num_tweets = (num_tweets_of_user, MAX_TWEETS)[
            num_tweets_of_user >= MAX_TWEETS]
        self._max_id = max_id  # recieve no tweets past this tweet_id

    @property
    def data(self):
        if self._tweets:
            return self._tweets

        with open(self._filename, 'a+', newline='') as cache_file:
            cache_file.seek(0)
            # how many tweets to begin grabbing
            # count = (self._num_tweets, 20)[self._num_tweets >= 20]
            # if no tweet data get it from api
            if self._filename.stat().st_size == 0:
                _id = self._user_id
                # get user timeline, loop untill we recieve _num_tweets
                cursor = (tweepy.Cursor(self._api.user_timeline, _id),
                          tweepy.Cursor(self._api.user_timeline, _id,
                                        max_id=self._max_id))[self._max_id]

                for tweet in [tweet for tweet in cursor.items(MAX_TWEETS)]:
                    self._tweets.append(Tweet(tweet.id_str, tweet.created_at,
                                        tweet.text))


                self.data = self._tweets

            else:
                # there exists cached tweets, get them
                csv_reader = csv.reader(cache_file)
                for row in csv_reader:
                    # record_object = dict(zip(attribute_names, row))
                    tweet = Tweet(*row)
                    self._tweets.append(tweet)
            return self._tweets

    @data.setter
    def data(self, tweets):
        # create csv writer and write all tweet objects
        with open(self._filename, 'a+', newline='') as cache_file:
            cache_file.seek(0)
            csv_writer = csv.writer(cache_file)
            for tweet in tweets:
                record = [*tweet, ]  # convert namedtuple to list for csv
                csv_writer.writerow(record)


class UserTweets(object):
    """TODOs:
    - implement len() an getitem() magic (dunder) methods"""

    def __init__(self, handle, max_id=-1):
        # _cache reads and writes to csv files data recieved from Tweeter
        # user_timeline
        self._cache = TweepyCache(handle, max_id)
        self._tweets = self._cache.data  # list of tweet objects

    def __getitem__(self, key):
        return self._tweets[key]

    def __len__(self):
        return len(self._tweets)

    def cache(self):
        pass


if __name__ == "__main__":

    for handle in ('pybites', '_juliansequeira', 'bbelderbos'):
        print('--- {} ---'.format(handle))
        user = UserTweets(handle)
        for tw in user[:5]:
            print(tw)
        print()
