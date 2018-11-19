from django.views.generic import TemplateView, FormView, View
from django.http import HttpResponseRedirect
from SocialMediaAnalysis.settings import _MONGODB_DATABASE_HOST
from SMAapp.models import User
from SMAapp.forms import SearchUserForm, CompareUsersForm
from mongoengine import *
from django.core.urlresolvers import reverse_lazy
from collections import OrderedDict
import tweepy
import pymongo
import datetime
import re


class IndexView(TemplateView):
    template_name = 'SMAapp/index.html'

    def get_context_data(self, **kwargs):
        """gets the context data"""
        context = super(IndexView, self).get_context_data(**kwargs)
        search_user_form = SearchUserForm
        compare_users_form = CompareUsersForm
        context['search_user_form'] = search_user_form
        context['compare_users_form'] = compare_users_form
        return context


class SearchFormRedirectView(FormView):
    """view acting as an intermediate between the index page and the other pages
        Because we have 2 different forms, we need 2 intermediate views that grab
        the post request and redirects the user based on the form submitted
    """
    form_class = SearchUserForm

    def post(self, request, *args, **kwargs):
        """method triggered when the view gets a POST request from a the Search Form"""
        name = request.POST['username_input']
        username = User.objects.get(name=name).screen_name
        return HttpResponseRedirect(reverse_lazy('smaapp:user_details', kwargs={'username': username}))


class CompareFormRedirectView(FormView):
    """Intermediate view for Compare Form"""
    form_class = CompareUsersForm

    def post(self, request, *args, **kwargs):
        """method triggered when the view gets a POST request from a the Compare Form"""
        first_name = request.POST['first_username']
        second_name = request.POST['second_username']
        first_username = User.objects.get(name=first_name).screen_name
        second_username = User.objects.get(name=second_name).screen_name
        return HttpResponseRedirect(reverse_lazy('smaapp:compare_users', kwargs={'first_username': first_username,
                                                                                 'second_username': second_username}))


class CompareView(TemplateView):
    template_name = 'SMAapp/compare_layout.html'

    def get_context_data(self, **kwargs):
        context = super(CompareView, self).get_context_data(**kwargs)
        username1 = kwargs['first_username']
        username2 = kwargs['second_username']

        # updates the tweets of username
        conn = pymongo.MongoClient(_MONGODB_DATABASE_HOST)
        db = conn['eusma']
        users = db['users']

        if twitter_user_exists(users, username1) and twitter_user_exists(users, username2):
            query_and_save_last_200_tweets(users, username1)
            query_and_save_last_200_tweets(users, username2)

            connect('eusma')
            usr1 = User.objects.get(screen_name=username1)
            tweets1 = usr1.tweets

            usr2 = User.objects.get(screen_name=username2)
            tweets2 = usr2.tweets

            favorites_per_day1 = OrderedDict()
            favorites_per_day2 = OrderedDict()
            retweets_per_day1 = OrderedDict()
            retweets_per_day2 = OrderedDict()
            activity_per_day1 = initialize_days_dictionary()
            activity_per_day2 = initialize_days_dictionary()

            for tweet in tweets1:
                favorites_per_day1 = update_favorites(tweet, favorites_per_day1)
                retweets_per_day1 = update_retweets(tweet, retweets_per_day1)
                activity_per_day1 = update_activity_per_day(tweet.created_at, activity_per_day1)

            for tweet in tweets2:
                favorites_per_day2 = update_favorites(tweet, favorites_per_day2)
                retweets_per_day2 = update_retweets(tweet, retweets_per_day2)
                activity_per_day2 = update_activity_per_day(tweet.created_at, activity_per_day2)



            context['user1'] = usr1
            context['user2'] = usr2
            context['favorites_per_day1'] = favorites_per_day1
            context['favorites_per_day2'] = favorites_per_day2
            context['retweets_per_day1'] = retweets_per_day1
            context['retweets_per_day2'] = retweets_per_day2
            context['activity_per_day1'] = activity_per_day1
            context['activity_per_day2'] = activity_per_day2

        return context


class UserDetailsView(TemplateView):
    template_name = 'SMAapp/layout.html'

    def get_template_names(self):
        """adds a new template if the user does not exist"""
        template_names = []
        username = self.kwargs['username']   # gets the asked username from url

        if not db_user_exists(username):
            template_names.append('SMAapp/user404.html')
        else:
            template_names.append('SMAapp/layout.html')

        return template_names

    def get_context_data(self, **kwargs):
        context = super(UserDetailsView, self).get_context_data(**kwargs)
        username = kwargs['username']   # gets the asked username from url

        # updates the tweets of username
        conn = pymongo.MongoClient(_MONGODB_DATABASE_HOST)
        db = conn['eusma']
        users = db['users']
        if twitter_user_exists(users, username):

            #query_and_save_last_200_tweets(users, username)

            connect('eusma')
            user = User.objects.get(screen_name=username)
            tweets = user.tweets
            latest_tweet = tweets[0]

            # sorts the tweets by favorite_count
            realTweets = [t for t in tweets if not is_retweet(t)]
            tweets_ordered_by_favorite = sorted(realTweets, key=lambda x: x.favorite_count, reverse=True)
            first_favorite = tweets_ordered_by_favorite[0]
            second_favorite = tweets_ordered_by_favorite[1]
            third_favorite = tweets_ordered_by_favorite[2]

            # variable initialization
            count_of_tweet = 0
            count_of_retweet = 0
            activity_per_day = initialize_days_dictionary()
            favorites_per_day = OrderedDict()
            retweets_per_day = OrderedDict()
            word_frequency = {}

            wordlist = [unicode('ID,'),unicode('favorite_count,'),unicode('retweet_count,'),unicode('created_at,'),unicode('hashtags,'),unicode('urls,'),unicode('user_mentions,'),unicode('is_retweet,'),unicode('text'),unicode("\\n")]
            for tweet in tweets:
                # calculates the dictionaries for the statistics
                activity_per_day = update_activity_per_day(tweet.created_at, activity_per_day)
                favorites_per_day = update_favorites(tweet, favorites_per_day)
                retweets_per_day = update_retweets(tweet, retweets_per_day)
                word_frequency = update_hashtag_frequency(tweet, word_frequency)

                wordlist.extend([unicode(str(tweet.tweet_id)),unicode(','),unicode(str(tweet.favorite_count)),unicode(','),unicode(str(tweet.retweet_count)),unicode(','),unicode(str(tweet.created_at)),unicode(',')])

                for hashtag in tweet.entities['hashtags']:
                    wordlist.append(unicode('[' + hashtag.text + ']' ))
                wordlist.append(unicode(','))

                for url in tweet.entities['urls']:
                    wordlist.append(unicode('[' + url.expanded_url + ']' ))
                wordlist.append(unicode(','))

                for mention in tweet.entities['user_mentions']:
                    wordlist.append(unicode('[' + mention.screen_name + ']' ))
                wordlist.append(unicode(','))

                # counts the ratios
                if is_retweet(tweet):
                    wordlist.append(unicode('True'))
                    count_of_retweet += 1
                else:
                    wordlist.append(unicode('False'))
                    count_of_tweet += 1
                wordlist.append(unicode(','))

                wordlist.append(re.escape(tweet.text))
                wordlist.append(unicode("\\n"))


            # word cloud
            list = []
            for key, value in word_frequency.items():
                list.append(tuple((key,value)))

            list = sorted(list, key=lambda tup: tup[1], reverse=True)
            list[10:] = []
            list2 = []
            flag = True
            multiplier = 1
            for (key,value) in list:
                if flag:
                    multiplier = 80 / value
                value = value*multiplier
                flag = False
                list2.append(tuple((key,value)))

            word_frequency = {}
            for (key, value) in list2:
                word_frequency[key] = value

            if count_of_tweet == 0:
                tweet_ratio = 0
            else:
                tweet_ratio = round(float(count_of_tweet) / float(count_of_retweet+count_of_tweet)*100, 0)

            if count_of_retweet == 0:
                retweet_ratio = 0
            else:
                retweet_ratio = round(float(count_of_retweet) / float(count_of_retweet+count_of_tweet)*100, 0)


            context['user'] = user
            context['latest_tweet'] = latest_tweet
            context['first_favorite'] = first_favorite
            context['second_favorite'] = second_favorite
            context['third_favorite'] = third_favorite

            context['tweets_to_csv'] = ''.join(wordlist)
            # charts context
            context['activity_per_day'] = activity_per_day
            context['favorites_per_day'] = favorites_per_day
            context['word_frequency'] = word_frequency
            context['tweet_ratio'] = tweet_ratio
            context['retweet_ratio'] = retweet_ratio
            context['retweets_per_day'] = retweets_per_day

        return context


def update_hashtag_frequency(tweet, word_frequency):
    """updates the dictionary of word frequency"""
    words = tweet.entities['hashtags']
    for dict in words:
        word = dict['text']
        # if the word is already contained
        if word in word_frequency:
            word_frequency[word] += 1
        else:
            word_frequency[word] = 1
    return word_frequency


def update_retweets(tweet, retweets_per_day):
    """updates the dictionary of 'year' => count of favorites"""
    day = tweet.created_at.day
    month = tweet.created_at.month
    year = tweet.created_at.year
    year = str(year) + '-' + str(month) + '-' + str(day)

    if not is_retweet(tweet):
        # if the year is already initialized
        if year in retweets_per_day:
            retweets_per_day[year] += tweet.retweet_count
        else:
            retweets_per_day[year] = tweet.retweet_count

    return retweets_per_day


def update_favorites(tweet, favorites_per_day):
    """updates the dictionary of 'year' => count of favorites"""
    day = tweet.created_at.day
    month = tweet.created_at.month
    year = tweet.created_at.year
    year = str(year)+'-'+str(month)+'-'+str(day)

    # if the year is already initialized
    if year in favorites_per_day:
        favorites_per_day[year] += tweet.favorite_count
    else:
        favorites_per_day[year] = tweet.favorite_count
    return favorites_per_day


def update_activity_per_day(date_of_tweet, activity_per_day):
    """updates the dictionary of 'day'=> count of tweets"""
    day_of_week = date_of_tweet.weekday()  # gets the day of week
    day = index_to_day(day_of_week)
    activity_per_day[day] += 1  # increments by 1
    return activity_per_day


def get_tweepy():
    consumer_key = "i7luZOMXkaqvMvtxPuil2Pjbl"
    consumer_secret = "In2ANHHRpYqiF5L8yPdh4BBeHjbVkg7O62ULdi5gnogdLBgQ19"
    access_key = "50138668-E7FoJ1lTUwTaLWHQixDkTZZ5t8qLT5kqKB1WMcfz9"
    access_secret = "aJ1gcBMLrralPSmbhhTgz1EFJxwgNtrpACU0sCD1eboCu"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api


def twitter_user_exists(users, name):
    """checks if a Twitter user exists"""
    iterator = users.find({'screen_name': str(name)})
    if iterator.count() > 0:
        return True
    else:
        return False


def db_user_exists(screen_name):
    """checks if the username exists in the DB"""
    result = User.objects(screen_name=screen_name)
    # user does not exist
    if not result:
        return False
    else:
        return True


def query_and_save_last_200_tweets(users, name):
    # create tweepy i
    api = get_tweepy()
    # get the last 200 tweets of a user with user name  -> "name" - includes retweets
    past = api.user_timeline(screen_name=name, count=200, include_rts=True)
    # check if the user has any tweets, if len(past)>0 there is at least one tweet
    if len(past) > 0:
        tweet = past[0]._json
        # check if user exists in database, if not the user is inserted
        if twitter_user_exists(users, name) is False:
            print ('user does not exist')
            if 'user' in tweet:
                tweet['user']['created_at'] = datetime.datetime.strptime(tweet['user']['created_at'],
                                                                         '%a %b %d %H:%M:%S +0000 %Y')
                user = tweet['user']
                users.insert(user)
            for p in past:
                p=p._json
                if 'created_at' in p:
                    p['created_at'] = datetime.datetime.strptime(p['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                    users.update({"screen_name": name}, {"$addToSet": {"tweets": p}}, upsert=True)
        # if the user is already inserted in the database, we insert only the tweets that have not been yet stored
        else:
            # collect the ids of already stored tweets
            info = users.find_one({'screen_name': name})
            twt_ids = set()
            stored_twts=info['tweets']
            for i in range(0, len(stored_twts)-1):
                t_id = stored_twts[i]['id']
                twt_ids.add(t_id)
            for p in past:
                p = p._json
                new_id = p['id']
                fav = p['favorite_count']
                if 'retweet_count' in p:
                    rt_count = p['retweet_count']
                else:
                    rt_count = 0
                if new_id not in twt_ids:
                    if 'created_at' in p:
                        p['created_at']=datetime.datetime.strptime(p['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                        users.update({"screen_name": name}, {"$addToSet": {"tweets": p}}, upsert=True)
                else:
                    users.update({"screen_name": name, "tweets.id": new_id}, {"$set": {"tweets.$.favorite_count": fav, "tweets.$.retweet_count" : rt_count}})


def initialize_days_dictionary():
    """initializes a dictionary of days so that the days will be in a specific order"""
    return OrderedDict([('Monday', 0),
                        ('Tuesday', 0),
                        ('Wednesday', 0),
                        ('Thursday', 0),
                        ('Friday', 0),
                        ('Saturday', 0),
                        ('Sunday', 0)])


def index_to_day(index):
    """gets an index and returns the name of the day"""
    if index == 0:
        return "Monday"
    elif index == 1:
        return "Tuesday"
    elif index == 2:
        return "Wednesday"
    elif index == 3:
        return "Thursday"
    elif index == 4:
        return "Friday"
    elif index == 5:
        return "Saturday"
    else:
        return "Sunday"


def is_retweet(tweet):
    """checks if the tweet is a retweet"""
    if unicode(tweet.text).startswith("RT"):
        return True
    else:
        return False
