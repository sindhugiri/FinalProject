## Your name: Sindhu Giri 
## The option you've chosen: Option 2

# Put import statements you expect to need here!
import requests_oauthlib 
import webbrowser
import json
import unittest
import itertools
import collections
import tweepy
import twitter_info 
import sqlite3

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
        self.assertEqual(type(z.imbd_rating), type(9)) #Checking to see that the type of the IMBD rating instance is an integer 
    def test4(self):
        b=Movie()
        self.assertEqual(type(b.title), type("")) #Checking to see that the type of the title instance is a string 
    def test5(self):
        self.assertEqual(most_common_title("Split", "Avatar", "Totanic", "Titanic", "Titanic"),("Titanic")) #Checking to see that the most_common_title function returns the most commonly occuring movie title 
    def test6(self):
        w=Titanic.rating_info()
        self.assertEqual(type(w[0]),type("")) #Checking to see that the first element of the list is a string 
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







