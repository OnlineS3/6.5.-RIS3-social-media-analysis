# -*- coding: utf-8 -*-
from mongoengine import *


class User(Document):
    """class representing a Twitter user"""
    name = StringField(max_length=100, required=True, db_field='name')
    screen_name = StringField(max_length=100, required=True, db_field='screen_name')
    location = StringField(max_length=100, db_field='location')
    followers_count = IntField(db_field='followers_count')
    friends_count = IntField(db_field='friends_count')
    created_at = DateTimeField(db_field='created_ad')
    statuses_count = IntField(db_field='statuses_count')
    profile_image_url = URLField(db_field='profile_image_url')
    description = StringField(db_field='description')
    lang = StringField(db_field='lang')
    tweets = ListField(EmbeddedDocumentField('Tweet'))

    meta = {'collection': 'users'}

    def __unicode__(self):
        return '%s (@%s)' % (self.name, self.screen_name)


class Entity(Document):
    """class representing an entity of a tweet"""
    hashtags = ListField(EmbeddedDocumentField('Hashtag'))
    user_mentions = ListField(EmbeddedDocumentField('UserMention'))
    urls = ListField(EmbeddedDocumentField('URL'))


class Tweet(Document):
    """Class representing a tweet made by a user"""
    created_at = DateTimeField(db_field='created_at')
    tweet_id = LongField(db_field='id')
    text = StringField(db_field='text')
    retweet_count = IntField(db_field='retweet_count')
    favorite_count = IntField(db_field='favorite_count')
    entities = EmbeddedDocumentField('Entity')


class Hashtag(Document):
    """class representing a hashtag which is an entity"""
    text = StringField(db_field='text')
    indices = ListField(db_field='indices')


class UserMention(Document):
    """class representing a user mention which is part of an entity"""
    screen_name = StringField(db_field='screen_name')
    name = StringField(db_field='name')
    mention_id = StringField(db_field='id_str')
    indices = ListField(db_field='indices')


class URL(Document):
    """class representing which is part of an entity"""
    url = URLField(db_field='url')
    expanded_url = URLField(db_field='expanded_url')
    display_url = URLField(db_field='display_url')
    indices = ListField(db_field='indices')
