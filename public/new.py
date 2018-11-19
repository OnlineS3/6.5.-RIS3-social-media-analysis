# -*- coding: utf-8 -*-
"""
@author: Ilias
"""

import tweepy
from tweepy import OAuthHandler
import pymongo
from pymongo import MongoClient
from collections import defaultdict
import datetime
import json

conn = pymongo.MongoClient('')
db = conn['']
users=db['']
#users2=db['users_copy']





def get_tweepy():
    consumer_key = ""
    consumer_secret = ""
    access_key = ""
    access_secret = ""

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
    return api

def user_exists(name):
    iterator = users.find({'screen_name':name})
    if iterator.count()>0:
        return True
    else:
        return False

def get_last_200_tweets_from_screen_name(name):
    #create tweepy i
    api = get_tweepy()
    #get the last 200 tweets of a user with user name  -> "name" - includes retweets
    past = api.user_timeline(screen_name=name, count = 200, include_rts = True)
    #check if the user has any tweets, if len(past)>0 there is at least one tweet
    if len(past)>0:
        tweet=past[0]._json
        #check if user exists in database, if not the user is inserted
        if user_exists(name)==False:
            print ('user does not exist')
            if 'user' in tweet:
                tweet['user']['created_at']=datetime.datetime.strptime(tweet['user']['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
                user=tweet['user']
                users.insert_one(user)
            for p in past:
                p=p._json
                if 'created_at' in p:
                    p['created_at']=datetime.datetime.strptime(p['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
                    users.update_one({ "screen_name":name },{ "$addToSet":{"tweets":p} },upsert= True)

        #if the user is already inserted in the database, we insert only the tweets that have not been yet stored
        else:
            print ('user exists')
            #collect the ids of already stored tweets
            info=users.find_one({'screen_name':name})
            twt_ids=set()
            stored_twts=info['tweets']
            for i in range(0,len(stored_twts)-1):
                t_id=stored_twts[i]['id']
                twt_ids.add(t_id)
            for p in past:
                p=p._json
                new_id=p['id']
                if new_id not in twt_ids:
                    if 'created_at' in p:
                        p['created_at']=datetime.datetime.strptime(p['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
                        users.update_one({ "screen_name":name },{ "$addToSet":{"tweets":p} },upsert= True)



#print user_exists('AthenaVakali')
#get_last_200_tweets_from_screen_name('AthenaVakali')




'''
def get_account_information(name):
    info={}
    iterator = users.find({'screen_name':name})
    t=iterator[0]
    info['friends']=t['friends_count']
    info['followers']=t['followers_count']
    info['total_tweets']=t['statuses_count']
    info=json.dumps(info, ensure_ascii=False)
    return info

def get_tweet_info(name):
    user = users2.find({'screen_name':name})
    pipeline=[{ '$sort': { 'tweets.created_at': order } }]
    iterator = db.users2.aggregate(pipeline)
    print ((len(iterator))



get_tweet_info('AthenaVakali')


def get_most_popular_tweets(name):
    iterator=tweets.find({'user.screen_name':name}).sort('favorite_count',-1)
    for i in iterator:
        tweet_info[str(i['created_at'])]=i['favorite_count']
    info=json.dumps(info, ensure_ascii=False)
    tweet_info=json.dumps(tweet_info, ensure_ascii=False)
    return info,tweet_info
'''
#get_last_200_tweets_from_screen_name('AthenaVakali')
#print (get_account_information('AthenaVakali'))