"""
File:           main.py
Author:         Dibyaranjan Sathua
Created on:     22/08/21, 6:22 pm
"""
import csv
from src.streaming_api import StreamingAPI


def main():
    """ Main entrypoint """
    streaming_api = StreamingAPI()
    # streaming_api.set_rules()
    # streaming_api.get_all_rules()
    # streaming_api.get_real_time_tweets()
    data = streaming_api.get_recent_tweets()
    tweets = data["data"]
    users = data["includes"]["users"]
    tweets_info = []
    for tweet in tweets:
        tweet_author_id = tweet["author_id"]
        tweet_author = next((x for x in users if x["id"] == tweet_author_id), None)
        temp = {
            "account_name": tweet_author["name"],
            "username": tweet_author["username"],
            "author_id": tweet_author["id"],
            "tweet_id": tweet["id"],
            "tweet": tweet["text"],
            "created_at": tweet["created_at"],
            "tweet_url": streaming_api.get_tweet_url(
                username=tweet_author["username"], tweet_id=tweet["id"]
            ),
            "retweeted": "referenced_tweets" in tweet
        }
        data = streaming_api.get_embedded_tweet(temp["tweet_url"])
        embedded_tweet = data["html"]
        temp["embedded_tweet"] = embedded_tweet
        tweets_info.append(temp)

    with open('tweets.csv', 'w', newline='') as csvfile:
        fieldnames = [
            'account_name', 'username', 'author_id', 'tweet_id', 'tweet', 'created_at',
            'tweet_url', 'retweeted', 'embedded_tweet'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for tweet in tweets_info:
            writer.writerow(tweet)


if __name__ == "__main__":
    main()
