from datetime import datetime
from abc import ABC, abstractmethod

from praw import Reddit
from orjson import dumps
from xdk import Client


class Connector(ABC):

    @abstractmethod
    def fetch(self, *args, **kwargs) -> list:
        pass


class RedditConnector(Connector):

    def __init__(self, client_id: str, client_secret: str, password: str, user_agent: str, username: str):
        self.reddit = Reddit(
            client_id=client_id,
            client_secret=client_secret,
            password=password,
            user_agent=user_agent,
            username=username,
        )

    def fetch(self, subreddit_name: str, limit: int = 100) -> list[dict]:
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        for post in subreddit.hot(limit=limit):
            posts.append({
                'source': 'reddit',
                'title': post.title,
                'text': post.selftext,
                'url': post.url,
                'created_utc': datetime.fromtimestamp(post.created_utc),
                'score': post.score
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
