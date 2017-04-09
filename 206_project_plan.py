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
    def test_1(self):
        self.assertEqual(type(CACHED_DICTION), type({}))
    def test_2(self):
        b=Titanic.rating_info()
        self.assertEqual(len(b)>0, True)
    def test_3(self):
        self.assertEqual(most_common_title("Split", "Avatar", "Totanic", "Titanic", "Titanic"),("Titanic"))
    def test4(self):
        w=Titanic.rating_info()
        self.assertEqual(type(w[0]),type(""))
    def test5(self):
        y=Titanic.__str__()
        self.assertEqual(len(y)> 0, True)
    def test6(self):
        z=Titanic.__str__()
        self.assertEqual(type(z), type(""))
    def test7(self):
        x= Movies("Titanic", "James Cameron")
    	self.assertEqual(x.name, "Titanic")
    def test8(self):
        f= Movies("Titanic", "James Cameron")
    	self.assertEqual(f.director, "James Cameron")

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







