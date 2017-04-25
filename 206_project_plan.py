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
from collections import defaultdict
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
movie_titles = ["Split", "The Room","Finding Dory", "Moonlight", "Her"]

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
        self.tweet_list=tweet_list
        for tweet in tweet_list:
            for movie in movie_titles:
                if movie in tweet["text"]:
                    self.search.append(movie)

            self.text= tweet["text"]
            self.tweet_id = tweet["id"]
            self.user= tweet["user"]["screen_name"]
            self.retweets = tweet["retweet_count"]
    
    def user_mentions (self):
        user_id=[]
        for x in self.tweet_list:
            for user in x["entities"]["user_mentions"]:
                user_id.append(user["screen_name"])
        return user_id
    
    def tweet_stuff(self):
        f = (self.tweet_id, self.text, self.user, self.retweets, ",".join(self.user_mentions()))
        return f

## get_user_tweets definition 

def get_user_tweets(phrase):
    text_twitter = []
    twitter_phrase = "twitter_{}".format(phrase)

    if twitter_phrase in CACHE_DICTION:
        response = CACHE_DICTION[twitter_phrase]
    else:
        api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
        public_tweets = api.get_user(id=phrase)
        CACHE_DICTION[twitter_phrase] = public_tweets
        response = public_tweets

        cache_file = open(CACHE_FNAME, 'w')
        cache_file.write(json.dumps(CACHE_DICTION))
        cache_file.close()
    
    return response

class User(object):
    def __init__(self, user_tweets):
        self.user_tweets=user_tweets

        self.user_id = self.user_tweets["id"]
        self.screen_name=self.user_tweets["screen_name"]
        self.num_favs= self.user_tweets["favourites_count"]
    
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
        r = (self.id, self.title, self.director, self.imdb_rating, self.billed_actor(), self.num_languages())
        return r

tweet_list = [get_tweets(movie) for movie in movie_titles]

tweet_instances=[Tweet(tweet_list=diction, movie_titles = movie_titles) for diction in tweet_list]

movie_list = [get_OMBDinfo(item) for item in movie_titles]

movie_instances = [Movie(diction) for diction in movie_list]

user_list=[]
for x in tweet_instances:
    for user in x.user_mentions():
        user_list.append(get_user_tweets(user))

user_instances=[User(user_tweets=diction) for diction in user_list]


## Task 2 - Creating database and loading data into database

conn = sqlite3.connect('project3_tweets.db')
cur = conn.cursor()

## Creating Tweets database 
cur.execute('DROP TABLE IF EXISTS Tweets')

table_spec1 = "CREATE TABLE IF NOT EXISTS Tweets(tweet_id INTEGER PRIMARY KEY, text TEXT, user TEXT, retweets INTEGER, user_mentions TEXT)"

cur.execute(table_spec1)

## Creating Users database 
cur.execute('DROP TABLE IF EXISTS Users')

table_spec2 = "CREATE TABLE IF NOT EXISTS Users(user TEXT PRIMARY KEY, screen_name TEXT, num_favs INTEGER)"

cur.execute(table_spec2)

## Creating Movies database 
cur.execute("DROP TABLE IF EXISTS Movies")

table_spec1 = "CREATE TABLE IF NOT EXISTS Movies (id TEXT PRIMARY KEY, title TEXT, director TEXT, imdb_rating TEXT, billed_actor TEXT, num_languages INTEGER)"

cur.execute(table_spec1)


## Loading Tweets database 
statement1 = 'INSERT or IGNORE INTO Tweets VALUES (?, ?, ?, ?, ?)'

for x in tweet_instances:

    cur.execute(statement1,x.tweet_stuff())

conn.commit()

## Loading Users database 
statement2 = "INSERT or IGNORE INTO Users VALUES(?,?,?)"

for w in user_instances:

    cur.execute(statement2, w.user_stuff())

conn.commit()

##Loading Movies database 

statement3 = "INSERT INTO Movies VALUES (?, ?, ?, ?, ?, ?)"

for w in movie_instances:
    
    cur.execute(statement3, w.omdb_stuff())

conn.commit()

##Making Queries to the databases 
two= "SELECT retweets FROM Tweets"
cur.execute(two)
retweets=cur.fetchall()

f="SELECT retweets FROM Tweets INNER JOIN Movies where imdb_rating >5"
g=cur.execute(f)
tweets_imdb= g.fetchall()

w="SELECT num_favs FROM Users"
cur.execute (w)
num_favs=cur.fetchall()
#
y="SELECT num_favs FROM Users INNER JOIN Movies where imdb_rating >5"
r= cur.execute(y)
num_favs_imdb= [x[0] for x in r.fetchall()]

f="SELECT title FROM Movies WHERE imdb_rating >5"
g=cur.execute(f)
title_imdb= g.fetchall()

f="SELECT num_languages FROM Movies WHERE imdb_rating>5"
g=cur.execute(f)
num_lang_imdb= g.fetchall()

##Manipulating data with comprehension and libraries 

#Use a Counter in the collections library 

#Pulling out the most common retweets numbers and the amount of times they occur 

u=[]
for y in retweets:
    for x in y:
        u.append(x)
most_common1= collections.Counter(u).most_common(5)
# h= {j:k for (j,k) in most_common1}
#print (most_common1)

#Pulling out the most common retweets numbers of movies that have an imdb rating greater than 5 and the amount of times they occur 

w=[]
for y in tweets_imdb:
    for x in y:
        w.append(x)
most_common2= collections.Counter(w).most_common(5)
# l={x:y for (x,y) in most_common2}
#print (most_common2)

#Pulling the most common favorites count for user and the amount of times they occur 

r=[]
for y in num_favs:
    for s in y:
        r.append(s)
most_common3= collections.Counter(r).most_common(5)
# o={y:u for (y,u) in most_common3}
#print (most_common3)

#Pulling the most common favorites count for users of movies that have an imdb rating greater than 5 and the amount of times they occur 

d=[]
for y in num_favs_imdb:
    d.append(y)
most_common4= collections.Counter(d).most_common(5)
# o={i:p for (i,p) in most_common4}


#Most common retweets--key values 
#Most common retweets with imdb rating of greater than 5--value pair 

e=[x[0] for x in most_common1]
g=[x[0] for x in most_common2]
t=zip(e,g)
retweets_vs_imdb={e:g for e,g in t}
#print (retweets_vs_imdb)

#Most common retweets amount--key values 
#Most common retweets amount with imdb rating of greater than 5--value pair 

j=[x[1] for x in most_common1]
a=[x[1] for x in most_common2]
d=zip(j,a)
retweetsamount_vs_imdb={j:a for j,a in d}
#retweetsamount_vs_imdb=list(retweetsamount_vs_imdb)
print (retweetsamount_vs_imdb)

#Most common numfavs--key values 
#Most common numfavs with imdb rating of greater than 5--value pair 

m=[x[0] for x in most_common3]
n=[x[0] for x in most_common4]
q=zip(m,n)
num_favs_vs_imdb={e:g for e,g in q}

#Most common numfavs amount--key values 
#Most common numfavs amount with imdb rating of greater than 5--value pair 

b=[x[1] for x in most_common3]
v=[x[1] for x in most_common4]
z=zip(b,v)
num_favs_amount_vs_imdb={b:v for b,v in z}

def difference_retweets():
    for j,a in retweetsamount_vs_imdb.items():
        if a> j:
            i=a-j
            return i


w=map(difference_retweets(), retweetsamount_vs_imdb)
print (w)      


def difference_num_favs():
    for b,v in num_favs_amount_vs_imdb.items():
        if v> b:
            er=v-b
            return er

u=map(difference_num_favs(), num_favs_amount_vs_imdb)



# wo=[]
# rating_influence_num_favs=[]
# for b,v in num_favs_amount_vs_imdb.items():
#     if v>b:
#         wo.append(v-j)
# for s in wo:         
#     rating_influence_num_favs.append(s)





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







