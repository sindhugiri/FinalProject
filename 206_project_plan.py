## Your name: Sindhu Giri 
## The option you've chosen: Option 2

# Put import statements you expect to need here!
import tweepy
import twitter_info
import unittest
import json
import sqlite3
import re
import collections
import itertools
from itertools import chain
import requests
import csv
import webbrowser
from pprint import pprint
import sys
import codecs

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer) 


##### TWEEPY SETUP CODE:
# Authentication information should be in a twitter_info file...
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Set up library to grab stuff from twitter with your authentication, and return it in a JSON format 
movie_titles = ["Split", "The Room","Finding Dory"]

##### END TWEEPY SETUP CODE

## Task 1 - Gathering data
##Caching set-up

CACHE_FNAME = "SI206_finalproj_cache.json"

try:
    cache_file = open(CACHE_FNAME,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}

##get_user_tweets definition 

def get_tweets(phrase):
    text_twitter = []
    twitter_phrase ="twitter_"+str(phrase)

    if twitter_phrase in CACHE_DICTION:
        response_text = CACHE_DICTION[twitter_phrase]
        
    else:
        api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
        public_tweets = api.search(q=phrase)

        CACHE_DICTION[twitter_phrase] = public_tweets
        response_text = public_tweets


        cache_file = open(CACHE_FNAME, 'w')
        cache_file.write(json.dumps(CACHE_DICTION))
        cache_file.close()
    
    y= response_text["statuses"]
    for x in y:
        text_twitter.append(x)
    return text_twitter

## get_user_tweets definition 

def get_user_tweets(phrase):
    text_twitter = []
    twitter_phrase = "twitter_{}".format(phrase)

    if twitter_phrase in CACHE_DICTION:
        response = CACHE_DICTION[twitter_phrase]
        
    else:
        api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
        public_tweets = api.user_timeline(id=phrase)
        CACHE_DICTION[twitter_phrase] = public_tweets
        response = public_tweets


        cache_file = open(CACHE_FNAME, 'w')
        cache_file.write(json.dumps(CACHE_DICTION))
        cache_file.close()

    for tweet in response:
            text_twitter.append(tweet)
        
    return text_twitter


umich_tweets= get_user_tweets("umich")

##get_movie_info definition 

def get_OMBDinfo(phrase):
    base_url="http://www.omdbapi.com/?"
    movie_phrase = "omdb_"+str(phrase)
    
    if movie_phrase in CACHE_DICTION:
        response = CACHE_DICTION[movie_phrase]

    else: 
        response= requests.get(base_url, params = {"t":phrase, "type":"movie"}).text 
        ombd_RETURN= json.loads(response)
        CACHE_DICTION[movie_phrase]=ombd_RETURN
        response=ombd_RETURN

        cache_file = open(CACHE_FNAME, 'w')
        cache_file.write(json.dumps(CACHE_DICTION))
        cache_file.close()

    return response

class Movie(object):
    def __init__(self, movie_diction):
        self.id = movie_diction["imdbID"]
        self.title = movie_diction["Title"]
        self.director = movie_diction["Director"]
        self.rating = movie_diction["imdbRating"]
        self.actors = movie_diction["Actors"] 
        self.languages = movie_diction["Language"] 

    def lst_actors(self):
        return self.actors.split(",")
    def num_languages(self):
        return len(self.languages.split(","))
    def num_one_actor(self):
        return self.lst_actors()[0]

    def tuple_generate(self): ##Remember the order used here, make sure it's correct with what the database table row order is
        tup = (self.id, self.title, self.director, self.rating, self.num_one_actor(), self.num_languages())
        return tup

class Tweet(object):

    def __init__(self, tweet_list, movie_titles):
        self.search = []
        self.text = []
        self.id = []
        self.user = []
        self.favorites = []
        self.retweets = []
        for tweet in tweet_list:
            for movie in movie_titles:
                if movie in tweet["text"]:
                    self.search.append(movie)
            self.text.append(tweet["text"])
            self.id.append(tweet["id"])
            self.user.append(tweet["user"]["screen_name"])
            self.favorites.append(tweet["favorite_count"])
            self.retweets.append(tweet["retweet_count"])

    def zip_lists(self):
        m = zip(self.search, self.text, self.id, self.user, self.favorites, self.retweets)
        w = list(m)
        return w

tweet_list = []
for movie in movie_titles:
    tweet_list.append(get_tweets(movie))

tweet_instances=[]
for diction in tweet_list:
    tweet_instances.append(Tweet(tweet_list=diction, movie_titles = movie_titles))

movie_list = []
for item in movie_titles:
    movie_list.append(get_OMBDinfo(item))

movie_instances = []
for diction in movie_list:
    movie_instances.append(Movie(diction))

## Task 2 - Creating database and loading data into database

conn = sqlite3.connect('project3_tweets.db')
cur = conn.cursor()

## Creating Tweets database 
cur.execute('DROP TABLE IF EXISTS Tweets')

table_spec1 = "CREATE TABLE IF NOT EXISTS Tweets(text TEXT PRIMARY KEY, tweet_id INTEGER, user_id TEXT, time_posted TIMESTAMP, retweets INTEGER)"

cur.execute(table_spec1)

## Creating Users database 
cur.execute('DROP TABLE IF EXISTS Users')

table_spec2 = "CREATE TABLE IF NOT EXISTS Users(user_id TEXT PRIMARY KEY, screen_name TEXT, num_favs INTEGER)"

cur.execute(table_spec2)

## Creating Movies database 
cur.execute("DROP TABLE IF EXISTS Movies")

table_spec1 = "CREATE TABLE IF NOT EXISTS Movies (movie_ID TEXT PRIMARY KEY, title TEXT, director TEXT, IMDB_rating TEXT, top_actor TEXT, num_of_languages INTEGER)"

cur.execute(table_spec1)


## Loading Tweets database 
statement1 = 'INSERT or IGNORE INTO Tweets VALUES (?, ?, ?, ?, ?)'

for x in umich_tweets:

    text=x["text"]
    tweet_id=x["id_str"]
    user_id=x["user"]["screen_name"]
    time_posted=x["created_at"]
    retweets=x["retweet_count"]

    total_tweet=(tweet_id, text, user_id, time_posted, retweets)

    cur.execute(statement1,total_tweet)



## Loading Users database 
statement2 = "INSERT or IGNORE INTO Users VALUES(?,?,?)"

user_ids = []
for tweet in umich_tweets:
    for user in tweet["entities"]["user_mentions"]:
        user_ids.append(user["screen_name"])

user_ids.insert(0, '@umich')

for user in user_ids:
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    user = api.get_user(user)
    user_id = user["id"]
    screen_name=user["screen_name"]
    num_favs= user["favourites_count"]

    total_tweet=(user_id, screen_name, num_favs)

    cur.execute(statement2,total_tweet)


##Loading Movies database 

mov_statement = "INSERT INTO Movies VALUES (?, ?, ?, ?, ?, ?)"

for inst in movie_instances:
    cur.execute(mov_statement, inst.tuple_generate())

conn.commit()

# Write your test cases here.
class Tests(unittest.TestCase):
    def test1(self):
        cache=open("finalproject.json", "r").read()
        self.assertEqual(type(cache), type({})) #Checking to see that the CACHE_DICTION is an empty dictionary 
    def test2(self):
        cache=open("finalproject.json", "r").read()
        self.assertTrue("Split" in cache) #Checking to see that the movie title I chose is in the cache
    def test3(self):
        z=Movie()
        self.assertEqual(type(z.ratings), type(9)) #Checking to see that the type of the IMBD rating instance is an integer 
    def test4(self):
        b=Movie()
        self.assertEqual(type(b.title), type("")) #Checking to see that the type of the title instance is a string 
    def test5(self):
        self.assertEqual(most_common_title("Split", "Avatar", "Totanic", "Titanic", "Titanic"),("Titanic")) #Checking to see that the most_common_title function returns the most commonly occuring movie title 
    def test6(self):
        w=Titanic.__str__()
        self.assertEqual(type(w),type("")) #Checking to see that the first element of the list is a string 
    def test7(self):
        x= Movies("Titanic", "James Cameron")
        self.assertEqual(x.title, "Titanic") #Checking to see that the instance variable returns the title that I have provided 
    def test8(self):
        f= Movies("Titanic", "James Cameron")
        self.assertEqual(f.director, "James Cameron") #Checking to see that the instance variable returns the director that I have provided 

if __name__ == "__main__":
    unittest.main(verbosity=2)

## Remember to invoke all your tests..
test_1()
test_2() 
test_3()
test_4()
test_5()
test_6()
test_7()
test_8()







