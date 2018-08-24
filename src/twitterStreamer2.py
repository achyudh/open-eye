'''
Created on Jun 5, 2017

@author: lbozarth
'''
import sys,itertools
import multiprocessing as mp
import numpy as np
import pandas as pd
from datetime import datetime
from nltk import word_tokenize
import os, json
import tweepy  # https://github.com/tweepy/tweepy
sys.path.append("/home/lbozarth/PycharmProjects/MSR-Garage-Hack-2018/") #change this
from lbtools import twitterAPICalls
from lbtools import ioTools
import urllib.parse

sad = ['worried', 'anxious', 'nervous', "concerned", "upset", "worked up", "uneasy", "trouble", "troubling","wary", "I feel", 'issue', 'problem', 'problems', 'headache', 'trouble', 'disappointment', 'struggle', 'struggling', 'pressure', 'pestering', 'failure', 'failed', "conflict", "debate", "disagreement", "anxiety", "harassment", "pressure", "breakdown", "crisis", "sad", "dropout", 'guilt', 'guilty', "horrible", "panic", "scare", "scared", "I want"]

happy = ['thankful', 'pleased', 'satisfied', 'achieve', 'goal', 'I hope']
issues = ["inequality", 'education', 'literacy', 'illiteracy', 'violence', 'intolerance', 'immigration', 'extremism', 'discrimination', 'gender-issues', 'gender', 'poverty', 'terrorism', 'corruption', 'hunger', 'obesity', 'hate', 'crime', 'abortion', 'racism', 'employment', 'unemployment', 'theft', 'gun', 'sjw', "alcoholism"]

keywords_lst = sad
keywords_lst = set(keywords_lst)
keywords = " OR ".join(keywords_lst)
print(keywords)

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out

def getAPI(row):
    consumer_key = row[0]
    consumer_secret = row[1]
    access_token = row[2]
    access_token_secret= row[3]
#    print("credits", consumer_key, consumer_secret, access_token, access_token_secret)

    #authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api

def run_single_user_tweets(api, userid, since_id=0):
    tweets = twitterAPICalls.get_tweets(api, userid, since_id)
    if tweets is None or len(tweets) == 0:
        return
    if isinstance(tweets, dict):
        print(tweets)
        return
    return tweets

def run_single_user_friends(api, userid):
    friends = twitterAPICalls.get_all_friends_ids_largedata(api, userid)
    if friends is None or len(friends) == 0:
        return []
    if isinstance(friends, dict):
        print(friends)
        return []
    return friends

def run_single_user_followers(api, userid):
    followers = twitterAPICalls.get_all_followers_ids_largedata(api, userid)
    if followers is None or len(followers) == 0:
        return []
    if isinstance(followers, dict):
        print(followers)
        return []
    return followers

def run_single_user(row):
    api = getAPI(row)
    userids = row[4:]
    all_tweets = []
    for userid,friendid in userids:
        try:
            tweets = run_single_user_tweets(api, friendid)
            if tweets:
                tweets = [[userid, tweet] for tweet in tweets]
                all_tweets.extend(tweets)
            break
        except Exception as e:
            print("error", e)
            continue
    return all_tweets

def get_single_api():
    # has user description; is active; has friends>=100 <=300; filled out location; is an individual (how to check)
    # Access Token	129811971-RmWTpVZnTnxawdzXKDxKdUmcGEyVkYXsWMOUSQ0d
    # Access Token Secret	cdcDY61yxzc0vfHklmyOM2hHdyY3XZQJT2e6VXPequYwQ
    # Consumer Key (API Key)	62bHdXi5Q0PcPdZuidJ8Rbduq
    # Consumer Secret (API Secret)	nvZxMQex44dMH9Hn7RrTLtX2Jb2ZgJSy2dt04Sd1nZEnoQybhE
    row = ["62bHdXi5Q0PcPdZuidJ8Rbduq", "nvZxMQex44dMH9Hn7RrTLtX2Jb2ZgJSy2dt04Sd1nZEnoQybhE", "129811971-RmWTpVZnTnxawdzXKDxKdUmcGEyVkYXsWMOUSQ0d", "cdcDY61yxzc0vfHklmyOM2hHdyY3XZQJT2e6VXPequYwQ"]
    # fn = "../../shared/data_static/twitter/credits_single.txt"
    # rows = ioTools.readFile(fn, ",")
    # row = rows[1]
    api = getAPI(row)
    return  api

def get_all_user_credit_apis():
    fn = "../../shared/data_static/twitter/credits.txt"
    rows = ioTools.readFile(fn, ",")
    rows = rows[1:]
    return rows

def gen_user_friends_tweets():
    df = pd.read_csv("../data/user_sample.csv", header=0)
    user_ids = df['id'].tolist()
    api = get_single_api()
    all_friends = []
    for user_id in user_ids:
        friends = run_single_user_friends(api, user_id)
        friends = [[user_id, friend] for friend in friends]
        all_friends.extend(friends)
    print('total friends', len(all_friends))
    print(all_friends[:2])

    apis = get_all_user_credit_apis()
    chunks = chunkIt(all_friends, len(apis))
    res = []
    for i in range(len(chunks)):
        res.append(apis[i] + chunks[i])
    print(res[0])
    p = mp.Pool(len(apis))
    ndfs = p.map(run_single_user, res)
    ndfs = list(itertools.chain(*ndfs))
    df = pd.DataFrame(ndfs, columns=['user', 'user_friend_tweet'])
    print(df.head(2))
    print(len(df.index))
    wfn = "../data/tweets.csv"
    df.to_csv(wfn, sep='\t', header=True, index=False)
    return

# generate location based profiles
def gen_users():
    api = get_single_api()
    # locations = ['Bangalore, India', "Ahmedabad, India", "Bangkok, Thailand"]
    locations = ['South Africa']
    all_users = []
    for loc in locations:
        query = urllib.parse.quote(loc)
        print(query)
        places = api.geo_search(query=query, granularity='country')
        print(loc, places)
        for pl in places:
            print(pl.id)
            place_id = pl.id
            try:
                for tweet in tweepy.Cursor(api.search, q="%s place:%s" % (keywords, place_id), tweet_mode='extended', count=100).items():
                    obj = tweet._json
                    if len(obj['user']['description']) < 10: #no user profile or short profile
                        continue
                    if len(obj['user']['location']) < 10: #no user profile or short profile
                        continue
                    if obj['user']['statuses_count'] < 100: # not very active
                        continue
                    if '2018' in obj['user']['created_at']: # account is too new
                        continue
                    if obj['user']['friends_count']<100 or obj['user']['followers_count']<100:
                        continue
                    if obj['user']['friends_count'] > 500 or obj['user']['followers_count'] > 500:
                        continue

                    # user = obj['user']
                    # # print(user)
                    # row = [loc, user['id'],user['screen_name'],user['name'],user['location'],user['description'].replace("\n", "").replace("\r", "").replace("\t", ""),user['created_at'],user['friends_count'], user['followers_count'],user['statuses_count']]
                    # print(row)
                    all_users.append(json.dumps(obj))
                    # print(obj)
                #     break
                # break
            except Exception as e:
                print(e)
                continue
            break
    # df = pd.DataFrame(all_users, columns=['loc_src', 'id', 'screen_name', 'name', 'location', 'description', 'created_at', 'friends_count', 'followers_count', 'status_count'])
    # df.to_csv("../data/users.csv", header=True, index=False)
    with open("../data/tweets_southafrica2.csv", 'w') as f:
        f.writelines("\n".join(all_users))

def read_file():
    df = pd.read_csv("../data/tweets.csv", sep="\t", header=0)
    df['user_friend_tweet'] = df['user_friend_tweet'].apply(lambda x: json.loads(x))
    df['user_friend_name'] = df['user_friend_tweet'].apply(lambda x: x['user']['name'])
    print(df.head(2))
    return

def is_concern(x):
    x = str(x).lower()
    # xlst = word_tokenize(x)
    for kw in keywords_lst:
        if kw in x:
            return True

    return False

def parse_data():
    df = pd.read_csv("../data/tweets.csv", sep="\t", header=0)
    df['user_friend_tweet'] = df['user_friend_tweet'].apply(lambda x: json.loads(x))
    df['user_friend_name'] = df['user_friend_tweet'].apply(lambda x: x['user']['screen_name'])
    df['tweet_text'] = df['user_friend_tweet'].apply(lambda x: str(x['full_text']).replace("\n","").replace("\r","").replace("\t",""))
    df['is_valid'] = df['tweet_text'].apply(is_concern)
    df = df[df['is_valid']==True]
    df = df[['user', 'user_friend_name', 'tweet_text']]
    df.to_csv("../data/valid_tweets.csv", header=True, index=False)
    return

if __name__ == '__main__':
    gen_users()
    # gen_user_friends_tweets()
    # read_file()
    # parse_data()
    pass
