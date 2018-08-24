from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import csv
import json

# file_names = ['data\\tweets_southafrica.csv', 'data\\tweets_southafrica2.csv', 'data\\tweets_usa1.csv', 'data\\tweets_usa2.csv', 'data\\tweets_usa3.csv']
file_names = ['data/tweets_immigration.json', 'data/tweets_gendereq.json', 'data/tweets_extremism.json']

analyzer = SentimentIntensityAnalyzer()
for file_name in file_names:
    output_tweets = list()
    sentiment_sum = 0
    with open(file_name, 'rb') as json_file:
        for line in json_file:
            tweet = json.loads(line)
            if tweet['place'] is not None and tweet['place']['country_code'] == 'US':
                sentiment = analyzer.polarity_scores(tweet['full_text'])['compound']
                if abs(sentiment) > 0.5:
                    tweet['sentiment'] = sentiment
                    sentiment_sum += sentiment
                    output_tweets.append(tweet)
        json_file.close()
    print(file_name + ":")
    print("Average sentiment:", sentiment_sum/len(output_tweets))
    print("Number of filtered tweets:", len(output_tweets))

    with open(file_name.split(".json")[0] + '_processed.json', 'w') as output_file:
        json.dump(output_tweets, output_file)
        output_file.close()

