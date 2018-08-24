from flask import Flask
from flask import render_template, url_for, jsonify, request, flash, redirect
from inputs import CountryInput, SocialIssueInput
import json
from enum import Enum

app = Flask(__name__)

app.config['SECRET_KEY'] = "b9299e1261a5a482b0a250c3e7a6c041"

socialIssueData = [
    'data/tweets_immigration_processed.json',
    'data/tweets_extremism_processed.json',
    'data/tweets_gendereq_processed.json'
]

mapData = dict()

immigration_tweets = dict()
extremism_tweets = dict()
gender_eq_tweets = dict()
immigration_average_sentiments = dict()
extremism_average_sentiments = dict()
gender_eq_average_sentiments = dict()

def setup_server():
    global mapData
    global immigration_tweets
    global extremism_tweets
    global gender_eq_tweets
    global immigration_average_sentiments
    global extremism_average_sentiments
    global gender_eq_average_sentiments
    
    with open('data/world-countries.json') as f:
        mapData = json.load(f)
    with open(socialIssueData[0]) as f:
        immigration_tweets = json.load(f)
    with open(socialIssueData[1]) as f:
        extremism_tweets = json.load(f)
    with open(socialIssueData[2]) as f:
        gender_eq_tweets = json.load(f)

    immigration_average_sentiments = calculate_average_sentiment(grabCountryData(immigration_tweets))

    extremism_average_sentiments = calculate_average_sentiment(grabCountryData(extremism_tweets))

    gender_eq_average_sentiments = calculate_average_sentiment(grabCountryData(gender_eq_tweets))    

def grabCountryData(tweets):

    countries = dict()

    for tweet in tweets:
        country = tweet["place"]["country"]
        sentiment = tweet["sentiment"]
        if country in countries:
            countries[country][0] += sentiment
            countries[country][1] += 1
        else:
            countries[country] = [sentiment, 1]

    return countries

def calculate_average_sentiment(countries):

    averages = dict()

    for country in countries:
        if countries[country][1] != 0:
            averages[country] = (countries[country][0] / countries[country][1]) * 100  

    return averages    

@app.route("/", methods=["GET", "POST"])
def home():
    countryInput = CountryInput()
    socialIssueInput = SocialIssueInput()

    socialIssue = int(socialIssueInput.social.data)

    if socialIssue == 0:
        sentiments = immigration_average_sentiments
    elif socialIssue == 1:
        sentiments = extremism_average_sentiments
    else:
        sentiments = gender_eq_average_sentiments

    return render_template("main.html", social_issue_input=socialIssueInput, country_input=countryInput, mapData=mapData, sentiments=sentiments)

if __name__ == "__main__":
    setup_server()
    app.run(debug=True)