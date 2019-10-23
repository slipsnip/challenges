from collections import namedtuple
from pathlib import Path
import csv
import os

import tweepy

from config import CONSUMER_KEY, CONSUMER_SECRET
from config import ACCESS_TOKEN, ACCESS_SECRET

DEST_DIR = 'data'
EXT = 'csv'
MAX_TWEETS = 100


class CsvCache(object):
    def __init__(self, user, max_id=-1):
        self._filename = Path(DEST_DIR, user.get('id_str') + EXT)
        self._tweets = []
        # number of tweets user has
        num_tweets_of_user = user.get('statuses_count')
        # number of tweets to get, maximum MAX_TWEETS
        self._num_tweets = (num_tweets_of_user, MAX_TWEETS)[
            num_tweets_of_user >= MAX_TWEETS]
        self._max_id = max_id  # recieve no tweets past this tweet_id
        self._user_id = user.get('id')
        # do the OAuth dance
        self._auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self._auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        # get ourselfs an api
        self._api = tweepy(self._auth)

    @property
    def data(self):
        if self._tweets:
            return self._tweets

        # attribute names we are interested in from tweet object
        attribute_names = 'id_str created_at text'.split()
        with open(self._filename, '+', newline='') as cache_file:
            # how many tweets to begin grabbing
            count = (self._num_tweets, 20)[self._num_tweets >= 20]
            # if no tweet data get it from api
            if self._filename.stat().st_size == 0:
                recieved_count = 0
                _id = self._user.id
                # get user timeline, loop untill we recieve _num_tweets
                while(recieved_count < self._num_tweets):
                    if self._max_id:
                        self._tweets.extend(self._api.user_timeline(_id,
                                                                    max_id=self._max_id,
                                                                    count=count))
                    else:
                        self._tweets.extend(self._api.user_timeline(_id,
                                                                    count=count))
                    recieved_count += count
                    remainder = self._num_tweets - recieved_count
                    count = (remainder, 20)[remainder >= 20]

                self.data = self._tweets

            else:
                # there exists cached tweets, get them
                csv_reader = csv.reader(cache_file)
                for row in csv_reader:
                    record_object = dict(zip(attribute_names, row))
                    self._tweets.append(record_object)
            return self._tweets

    @data.setter
    def data(self, tweets):
        attribute_names = 'id_str created_at text'.split()
        # create csv writer and write all tweet objects
        with open(self._filename, '+', newline='') as cache_file:
            csv_writer = csv.writer(cache_file)
            for tweet in tweets:
                record = [tweet.get(attribute) for attribute in
                          attribute_names]
                csv_writer.writerow(record)


class UserTweets(object):
    """TODOs:
    - implement len() an getitem() magic (dunder) methods"""

    def __init__(self, handle, max_id=-1):
        self._user = self._api.get_user(handle)
        # _cache reads and writes to csv files data recieved from Tweeter
        # user_timeline
        self._cache = CsvCache(self._user, max_id)
        self._tweets = self._cache.data  # list of tweet objects

    def __getitem__(self, position):
        pass

    def __len__(self):
        pass

    def cache(self):
        pass


if __name__ == "__main__":

    for handle in ('pybites', '_juliansequeira', 'bbelderbos'):
        print('--- {} ---'.format(handle))
        user = UserTweets(handle)
        for tw in user[:5]:
            print(tw)
        print()
