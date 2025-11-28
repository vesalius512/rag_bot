import os

from dotenv import load_dotenv


load_dotenv()

YANDEX_CLOUD_API_KEY = os.environ.get('YANDEX_CLOUD_API_KEY')
YANDEX_CLOUD_FOLDER = os.environ.get('YANDEX_CLOUD_FOLDER')

PYTHON_KEYWORDS = ['pandas', 'numpy', 'django', 'flask', 'async', 'decorator', 'fastapi']
