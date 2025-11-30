import os

from dotenv import load_dotenv


load_dotenv()

YANDEX_CLOUD_API_KEY = os.environ.get('YANDEX_CLOUD_API_KEY')
YANDEX_CLOUD_FOLDER = os.environ.get('YANDEX_CLOUD_FOLDER')
YANDEX_CLOUD_MODEL = "yandexgpt-lite"

PYTHON_KEYWORDS = ['pandas', 'numpy', 'django', 'flask', 'async', 'decorator', 'fastapi']

PROMTP_TMPL = ("""Ты - полезный помощник, способный отвечать на вопросы. 
                  Используй предоставленные фрагменты контекста для формирования ответа.
                  Если в контексте нет информации для ответа на вопрос, 
                  ответь только этими словамим: 'Я не знаю, нет контекста'.
                  Вопрос: {}
                  Контекст: {}
                  Ответ: """)

