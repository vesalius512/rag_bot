from abc import ABC, abstractmethod

from praw import Reddit
import orjson
import requests
from requests import Session
from xdk import Client


class Connector(ABC):

    @abstractmethod
    def fetch(self, *args, **kwargs) -> list:
        pass


class RedditConnector(Connector):

    def __init__(self):
                 # client_id: str, client_secret: str, password: str, user_agent: str, username: str):
        self.session = Session()
        # Reddit(
        #     client_id=client_id,
        #     client_secret=client_secret,
        #     password=password,
        #     user_agent=user_agent,
        #     username=username,
        # )

    def fetch(self, subreddit_name: str = 'CryptoCurrency', limit: int = 100) -> list[dict]:
        # subreddit = self.reddit.subreddit(subreddit_name)
        response = self.session.get(f'https://www.reddit.com/r/{subreddit_name}/hot/.json?limit={limit}')
        posts = []

        if response.status_code == requests.codes.too_many:
            print('Too many for reddit api, using local mock json')
            with open('./posts.json', 'r') as file:
                data = orjson.loads(file.read())
        elif response.status_code != requests.codes.ok and response.status_code != requests.codes.too_many:
            data = response.json()
            print(f'Invalid response, data:', data)
            return posts
        else:
            data = response.json()

        for post in data['data']['children']:
            post_data = post['data']
            post_text = post_data['selftext']
            posts.append({
                'source': 'reddit',
                'title': post_data['title'],
                'text': post_text if post_text else post_data['title'],
                'url': post_data['url'],
                'created': post_data['created'],
                'score': post_data['score']
            })
        return posts


class TwitterConnector(Connector):
    def __init__(self, bearer_token: str):
        self.client = Client(bearer_token=bearer_token)
        self.query = '(from:xdevelopers -is:retweet) OR #xdevelopers'

    def fetch(self) -> list:
        all_posts = []
        for page in self.client.posts.search_all(
                query=self.query,
                max_results=100,
                tweet_fields=["author_id", "created_at"]
        ):
            page_data = getattr(page, 'data', []) or []
            all_posts.extend(page_data)
            print(f"Fetched {len(page_data)} Posts (total: {len(all_posts)})")

        print(f"\nTotal Posts: {len(all_posts)}")
        print(dumps({"data": all_posts[:5]}))
        return all_posts
