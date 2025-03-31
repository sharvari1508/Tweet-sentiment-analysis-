import pandas as pd
from flask import Flask, render_template, request
import tweepy
import re
import time
from tweepy.errors import TooManyRequests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

# Twitter API credentials
API_KEY = "nirYSXEXIARxfSO434uj5bJay"
API_SECRET = "dc7bK8oI6dLJUVFFrRYYPYalJlbjDtTd5ivrLRQ5P9cM3aVtIq"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAMkn0QEAAAAAyZLBjv996qeeaf%2BcZaR4xaARfrw%3D3KzMuZkAPOyz1Dvn8HEOYh7KTwd1joTExv6lOD4OnEAlau8Y8T"

# Authenticate Twitter API client
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Function to clean the tweet text
def clean_tweet(text):
    text = re.sub(r"http\S+", "", text)  # Remove URLs
    text = re.sub(r"@\S+", "", text)  # Remove mentions
    text = re.sub(r"#\S+", "", text)  # Remove hashtags
    text = re.sub(r"[^A-Za-z0-9 ]+", "", text)  # Remove special characters
    text = text.replace("Bitcon", "Bitcoin")  # Fix common typo
    return text.lower().strip()

# Function to analyze sentiment using VADER
def analyze_sentiment(text):
    scores = analyzer.polarity_scores(text)
    if scores['compound'] >= 0.05:
        return "Positive"
    elif scores['compound'] <= -0.05:
        return "Negative"
    else:
        return "Neutral"

# Function to fetch tweets with rate limit handling
def fetch_tweets(query):
    try:
        tweets = client.search_recent_tweets(query=query, max_results=10)
        return tweets
    except TooManyRequests as e:
        reset_time = e.response.headers.get('x-rate-limit-reset')
        if reset_time:
            reset_time = int(reset_time)
            sleep_time = reset_time - int(time.time()) + 5
            print(f"Rate limit hit. Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)
            return fetch_tweets(query)
        else:
            print("Too many requests, retrying in 60 seconds...")
            time.sleep(60)
            return fetch_tweets(query)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form["query"]
        tweets = fetch_tweets(query)
        
        results = []
        if tweets and tweets.data:
            for tweet in tweets.data:
                cleaned_text = clean_tweet(tweet.text)
                sentiment = analyze_sentiment(cleaned_text)
                results.append({"tweet": tweet.text, "sentiment": sentiment})

        return render_template("index.html", results=results, query=query)
    return render_template("index.html", results=None)

if __name__ == "__main__":
    app.run(debug=True)  