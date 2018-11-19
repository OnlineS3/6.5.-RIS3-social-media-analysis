import tweepy
from tweepy import OAuthHandler
import pymongo
from pymongo import MongoClient
from pybloom import BloomFilter
from collections import defaultdict
import operator
import datetime
import json
import sys
sys.path.insert(0, 'C://keys.py')
import keys

conn = pymongo.MongoClient('mongodb://localhost:27017/local')
db = conn['test']
user=db['users']
collected_tweets=db['tweets']


CONSUMER_KEY = keys['consumer_key']
CONSUMER_SECRET = keys['consumer_secret']
ACCESS_TOKEN = keys['access_token']
ACCESS_TOKEN_SECRET = keys['access_token_secret']

def get_tweepy():
    CONSUMER_KEY = keys['consumer_key']
    CONSUMER_SECRET = keys['consumer_secret']
    ACCESS_TOKEN = keys['access_token']
    ACCESS_TOKEN_SECRET = keys['access_token_secret']
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
    return api

# def bloomer(userid):
#     i=identified.find({'user_id' : userid}).count()
#     j=past.find({'user_id' : userid}).count()
#     capacity=i+j
#     f = BloomFilter(capacity, error_rate=0.001)
#     id_iter=identified.find({'user_id' : userid})
#     for ided in id_iter:
#         f.add(ided['tweetid'])
#     past_iter=past.find({'user_id' : userid})
#     for p in past_iter:
#         f.add(p['id_str'])
#     return f

def get_all_user_info_from_screen_name(name):
    api = get_tweepy()
    user= api.get_user(screen_name = name)
    return user
#print get_all_user_info_from_screen_name('AthenaVakali')


def get_last_200_tweets_from_screen_name(name):
    api = get_tweepy()
    past = api.user_timeline(screen_name=name, count = 200, include_rts = True)
    return past

#print get_last_200_tweets_from_screen_name('AthenaVakali')

def insert_tweets_in_mongo(tweets):
    for tweet in tweets:
        collected_tweets.insert_one(tweet._json)

#tweets=get_last_200_tweets_from_screen_name('AthenaVakali')
#insert_tweets_in_mongo(tweets)


#getting the number of followers/friends of a user by the tweets we have already stored in the database
def get_number_of_followers(name):
    match=collected_tweets.find_one({'user.screen_name':name})
    fol_count=match['user']['followers_count']
    return fol_count

def get_number_of_friends():
    match=collected_tweets.find_one({'user.screen_name':name})
    friends_count=match['user']['friends_count']
    return friends_count

#getting the ids of the followers/friends using twitters API
def get_followers_ids(name):
    ids = []
    api = get_tweepy()
    page_count = 0
    for page in tweepy.Cursor(api.followers_ids, screen_name=name, count=5000).pages():
        page_count += 1
        print 'Getting page {} for followers ids'.format(page_count)
        ids.extend(page)
    s1 = set(ids)
    return s1

def get_friends_ids():
    ids = []
    api = get_tweepy()
    page_count = 0
    for page in tweepy.Cursor(api.friends_ids, user_id=userid, count=5000).pages():
        page_count += 1
        print 'Getting page {} for friends ids'.format(page_count)
        ids.extend(page)
    s2 = set(ids)
    return s2

def get_best_friends():
    friends=get_friends_ids(userid)
    followers=get_followers_ids(userid)
    bestfriends=set.intersection(friends,followers)
    return bestfriends

#gets the names and the id of the user's mentions
def get_mentions(name):
    api = get_tweepy()
    iterat = collected_tweets.find({'user.screen_name' : name})
    mention_names =set()
    mention_ids=set()
    if iterat.count()>0:
        for t in iterat:
            if 'entities' in t:
                entities=t['entities']
                if 'user_mentions' in entities:
                    mentions=entities['user_mentions']
                    for i in range(0,len(mentions)):
                        mention_id=mentions[i]['id_str']
                        mention_name=mentions[i]['screen_name']
                        mention_names.add(mention_name)
                        mention_ids.add(mention_id)
    return mention_names,mention_ids


#print get_mentions('AthenaVakali')


#returns the number of the tweets that have been favorited and a dict with the tweet's id and the number of likes (if any) - collected tweets
def get_tweet_likes(name):
    likes={}
    twt_iterator=collected_tweets.find({'user.screen_name' : name})
    i=0
    for t in twt_iterator:
        tweet_id=t['id']
        num_of_likes=t['favorite_count']
        if num_of_likes>0:
            likes[tweet_id]=num_of_likes
            i+=1
    return i,likes

#returns the number of tweets that have been retweeted and a dict with the tweet's id and the number of retweets - collected tweets
def get_retweet_stats(name):
    rtwts={}
    twt_iterator=collected_tweets.find({'user.screen_name' : name})
    i=0
    for t in twt_iterator:
        tweet_id=t['id']
        num_of_rts=t['retweet_count']
        if num_of_rts>0:
            rtwts[tweet_id]=num_of_rts
            i+=1
    return i,rtwts

#print get_retweet_stats('AthenaVakali')

#function that replaces the created_at string in mongo, with the actual date. Useful to get statistics per day
def fixTime():
    for obj in collected_tweets.find():
        if obj['created_at']:
            print ('found')
            if type(obj['created_at']) is not datetime:
                print ('not date')
                time = datetime.datetime.strptime(obj['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
                print (time)
                coll.update({'_id':obj['_id']},{'$set':{'created_at' : time}})
