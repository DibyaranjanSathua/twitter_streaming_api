"""
File:           streaming_api.py
Author:         Dibyaranjan Sathua
Created on:     22/08/21, 5:38 pm
"""
import json
import requests
from requests.auth import AuthBase
from src.config import TwitterConfig
from src.exceptions import TwitterStreamingAPIError


class BearerTokenAuth(AuthBase):
    """ Bearer token authentication """
    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {TwitterConfig.BEARER}"
        r.headers["User-Agent"] = "SathuaLabsCodingTwitterAPI"
        return r


class StreamingAPI:
    """ Wrapper around twitter real time stream and rules API """
    BASE_URL: str = "https://api.twitter.com/2"

    def __init__(self):
        TwitterConfig.init()
        self._bearer_token_auth = BearerTokenAuth()

    def get_all_rules(self):
        """ Get all the rules for the streaming API """
        response = requests.get(self.rules_endpoint, auth=self._bearer_token_auth)
        if not response.ok:
            raise TwitterStreamingAPIError(
                f"Error getting rules (HTTP {response.status_code}): {response.text}"
            )
        print(json.dumps(response.json(), indent=4, sort_keys=True))
        return response.json()

    def delete_all_rules(self):
        """ Delete all the rules """
        rules = self.get_all_rules().get("data", [])
        ids = [x["id"] for x in rules]
        payload = {
            "delete": {"ids": ids}
        }
        response = requests.post(self.rules_endpoint, auth=self._bearer_token_auth, json=payload)
        if not response.ok:
            raise TwitterStreamingAPIError(
                f"Error setting rules (HTTP {response.status_code}): {response.text}"
            )
        return response.json()

    def set_rules(self):
        """ Set rules for the streaming API """
        payload = {
            "add": [
                {"value": "from:sathualabs"},
            ]
        }
        response = requests.post(self.rules_endpoint, auth=self._bearer_token_auth, json=payload)
        if response.ok:
            print(f"Rule created successfully")
            print(response.json())
        else:
            print(f"Error: Rule creation failed.")
            print(response.text)

    def get_real_time_tweets(self):
        """ Get real time stream """
        query_params = {
            "tweet.fields": "text,attachments,author_id,entities,referenced_tweets,created_at",
            "user.fields": "id,name,username",
            "expansions": "author_id,attachments.media_keys,referenced_tweets.id,referenced_tweets.id.author_id",
            "media.fields": "url,type,media_key,preview_image_url",
        }
        response = requests.get(
            self.stream_endpoint, auth=self._bearer_token_auth, stream=True, params=query_params
        )
        if not response.ok:
            raise TwitterStreamingAPIError(
                f"Error getting stream (HTTP {response.status_code}): {response.text}"
            )
        print(f"Filtered stream connection established successfully")
        for response_line in response.iter_lines():
            if response_line:
                json_response = json.loads(response_line)
                print(json.dumps(json_response, indent=4, sort_keys=True))

    def get_sample_real_time_tweets(self):
        """ Get real time stream """
        response = requests.get(
            self.sample_stream_endpoint, auth=self._bearer_token_auth, stream=True,
        )
        if not response.ok:
            raise TwitterStreamingAPIError(
                f"Error getting sample stream (HTTP {response.status_code}): {response.text}"
            )
        print(f"Connection established successfully")
        for response_line in response.iter_lines():
            if response_line:
                json_response = json.loads(response_line)
                print(json.dumps(json_response, indent=4, sort_keys=True))

    def get_recent_tweets(self):
        """ Get recent tweets """
        query_params = {
            # "query": "from:tweetviewertest",
            "query": "from:UFC",
            "tweet.fields": "text,attachments,author_id,entities,referenced_tweets,created_at",
            "user.fields": "id,name,username",
            "expansions": "author_id,attachments.media_keys,referenced_tweets.id,referenced_tweets.id.author_id",
            "media.fields": "url,type,media_key,preview_image_url",
            "max_results": 10
        }
        response = requests.get(
            self.search_endpoint, auth=self._bearer_token_auth, params=query_params
        )
        if not response.ok:
            raise TwitterStreamingAPIError(
                f"Error in recent tweet search (HTTP {response.status_code}): {response.text}"
            )
        print(json.dumps(response.json(), indent=4, sort_keys=True))
        return response.json()

    def get_tweet_by_id(self, tweet_id):
        """ Get tweet by id """
        url = f"{self.tweet_lookup_endpoint}/{tweet_id}"
        response = requests.get(url, auth=self._bearer_token_auth)
        if not response.ok:
            raise TwitterStreamingAPIError(
                f"Error in tweet lookup (HTTP {response.status_code}): {response.text}"
            )
        print(json.dumps(response.json(), indent=4, sort_keys=True))
        return response.json()

    def get_embedded_tweet(self, tweet_url):
        """ Return embed HTML in an oEmbed-compatible format """
        query_params = {
            "url": tweet_url
        }
        response = requests.get(self.get_oembed_endpoint, params=query_params)
        if not response.ok:
            raise TwitterStreamingAPIError(
                f"Error in oEmbed API (HTTP {response.status_code}): {response.text}"
            )
        # print(json.dumps(response.json(), indent=4, sort_keys=True))
        return response.json()

    @staticmethod
    def get_tweet_url(username, tweet_id):
        """ Return tweet url using username and tweet_id """
        return f"https://twitter.com/{username}/status/{tweet_id}"

    @property
    def rules_endpoint(self):
        """ Return rules endpoint url """
        return f"{self.BASE_URL}/tweets/search/stream/rules"

    @property
    def stream_endpoint(self):
        """ Return stream endpoint url """
        return f"{self.BASE_URL}/tweets/search/stream"

    @property
    def search_endpoint(self):
        """ Return search endpoint """
        return f"{self.BASE_URL}/tweets/search/recent"

    @property
    def sample_stream_endpoint(self):
        """ Return sample stream endpoint url """
        return f"{self.BASE_URL}/tweets/sample/stream"

    @property
    def get_oembed_endpoint(self):
        """ Return embed HTML in an oEmbed-compatible format """
        return "https://publish.twitter.com/oembed"

    @property
    def tweet_lookup_endpoint(self):
        """ Return endpoint for tweet lookup """
        return f"{self.BASE_URL}/tweets"
