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
    twitter_phrase = "twitter_"+str(phrase)
    tweets = []

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


    tweeter = response_text["statuses"]
    for tweet in tweeter:
        tweets.append(tweet)
    return tweets

class Tweet(object):

    def __init__(self, tweet_list, movie_titles):
        self.search=[]
        for tweet in tweet_list:
            for movie in movie_titles:
                if movie in tweet["text"]:
                    self.search.append(movie)
            self.text= tweet["text"]
            self.tweet_id = tweet["id"]
            self.user_id= tweet["user"]["screen_name"]
            self.retweets = tweet["retweet_count"]

    def tweet_list(self):
        f = (self.text, self.tweet_id, self.user_id, self.retweets)
        return f

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

class User(object):
    def __init__(self,user, tweet_list):
        self.search=[]
        for tweet in tweet_list:
            for user in user_list:
                if user["id"] in tweet[["entities"]["user_mentions"]:
                    self.search.append(user["id"])
            self.user_id=user["id"]
            self.screen_name=user["screen_name"]
            self.num_favs=user["favourites_count"]
        
    def user_stuff(self):
        m = (self.user_id, self.screen_name, self.num_favs)
        return m

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
        self.imdb_rating = movie_diction["imdbRating"]
        self.actors = movie_diction["Actors"]
        self.languages = movie_diction["Language"]

    def lst_actors(self):
        return self.actors.split(",")
    def num_languages(self):
        return len(self.languages.split(","))
    def billed_actor(self):
        return self.lst_actors()[0]

    def omdb_stuff(self):
        r = (self.id, self.title, self.director, self.languages, self.imdb_rating, self.actors)
        return r

tweet_list = [get_tweets(movie) for movie in movie_titles]

tweet_instances=[Tweet(tweet_list=diction, movie_titles = movie_titles) for diction in tweet_list]

movie_list = [get_OMBDinfo(item) for item in movie_titles]

movie_instances = [Movie(diction) for diction in movie_list]

user_list=[get_user_tweets(user) for user in movie_titles]

user_instances=[User(user=diction, tweet_list=tweet_list) for diction in user_list]



## Task 2 - Creating database and loading data into database

conn = sqlite3.connect('project3_tweets.db')
cur = conn.cursor()

## Creating Tweets database 
cur.execute('DROP TABLE IF EXISTS Tweets')

table_spec1 = "CREATE TABLE IF NOT EXISTS Tweets(text TEXT PRIMARY KEY, tweet_id INTEGER, user_id TEXT, retweets INTEGER)"

cur.execute(table_spec1)

## Creating Users database 
cur.execute('DROP TABLE IF EXISTS Users')

table_spec2 = "CREATE TABLE IF NOT EXISTS Users(user_id TEXT PRIMARY KEY, screen_name TEXT, num_favs INTEGER)"

cur.execute(table_spec2)

## Creating Movies database 
cur.execute("DROP TABLE IF EXISTS Movies")

table_spec1 = "CREATE TABLE IF NOT EXISTS Movies (id TEXT PRIMARY KEY, title TEXT, director TEXT, imdb_rating TEXT, billed_actor TEXT, num_languages INTEGER)"

cur.execute(table_spec1)


## Loading Tweets database 
statement1 = 'INSERT or IGNORE INTO Tweets VALUES (?, ?, ?, ?)'

for x in tweet_instances:

    cur.execute(statement1,x.tweet_list())

## Loading Users database 
statement2 = "INSERT or IGNORE INTO Users VALUES(?,?,?)"

for w in user_instances:

    cur.execute(statement2, w.user_stuff())

##Loading Movies database 

statement3 = "INSERT INTO Movies VALUES (?, ?, ?, ?, ?, ?)"

for w in movie_instances:
    
    cur.execute(statement3, w.omdb_stuff())

conn.commit()
conn.close()


##Making Queries to the databases 

# two="SELECT *FROM Tweets WHERE retweets>5"
# cur.execute(two)
# more_than_25_rts=cur.fetchall()

# f="SELECT text FROM Tweets INNER JOIN Movie where IMDB_rating >5"
# g=cur.execute(f)
# joined_result= g.fetchall()
#best_movies= [list(x) for x in joined_result]
#best_movies=str(best_movies[0][0])

# w=SELECT *FROM Users WHERE num_favs>5"
# cur.execute (w)
#more_than_5_num_favs=cur.fetchall()
#
# y="SELECT screen_name FROM Users INNER JOIN Movie where IMDB_rating >5"
# r= cur.execute(y)
# screen_names= [x[0] for x in r.fetchall()]

# f="SELECT *FROM Movies WHERE imdb_rating >5"
# g=cur.execute(f)
# joined_result1= g.fetchall()

# f="SELECT director FROM Movies WHERE imdb_rating >5"
# g=cur.execute(f)
# joined_result2= g.fetchall()

#r = map (joined_result2,joined_result1)

##Manipulating data with comprehension and libraries 
# p=[]
# for x in descriptions_fav_users:
#     p.append(x.split())

# u=[]
# for y in p:
#     for r in y:
#         u.append(r)

# description_words = set(x for x in u)

# ##Use a Counter in the collections library 
# p=[]
# for x in descriptions_fav_users:
#     p.append(x.split())

# u=[]
# for y in p:
#     for r in y:
#         for s in r:
#             u.append(s)

# most_common= collections.Counter(u).most_common(1)

# most_common_char = most_common[0][0]


##I also want to rework my instance variables in my classes to reflect my original plans 
##While continuing with this project, I still write specific queries to develop connections between the three tables
##I also plan on using data manioulation techniques such as list comphrehensions/Counters in the collections library 
##I want to list out the statistics of the data collected in a text file and then use a csv file to make a data visualization 

# import csv
# outfile = open("twittervsOMDB.csv", "w")
# outfile.write("Name, CreatedTime, IDNumber\n")
# for item in post_insts:
#     outfile.write('{}, {}, {}\n'.format(item.getname(), item.getcreated_time(), item.getid()))
# outfile.close()

f = open('summarystats.txt', 'w')
f.write(json.dumps(CACHE_DICTION))
f.close()


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







