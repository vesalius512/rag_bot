import os

from dotenv import load_dotenv


load_dotenv()

YANDEX_CLOUD_API_KEY = os.environ.get('YANDEX_CLOUD_API_KEY')
YANDEX_CLOUD_FOLDER = os.environ.get('YANDEX_CLOUD_FOLDER')
YANDEX_CLOUD_MODEL = "yandexgpt-lite"

REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
REDDIT_PASSWORD = os.environ.get('REDDIT_PASSWORD')
REDDIT_USERAGENT = os.environ.get('REDDIT_USERAGENT')
REDDIT_USERNAME = os.environ.get('REDDIT_USERNAME')

CHROMA_PATH = './chroma_db'

PROMTP_TMPL = ("""Ты - финансовый аналитик. Ответь на вопрос, используя только контекст ниже.
                  Контекст: {}
                  Вопрос: {}
                  Ответ:""")
