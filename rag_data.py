import logging
import re

import html
from datasets import load_dataset, DatasetDict
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from constants import PYTHON_KEYWORDS


class DataSetLoader:
    def __init__(self,
                 ds_name: str,
                 splitter: RecursiveCharacterTextSplitter,
                 logger: logging.Logger):
        self.ds_name = ds_name
        self.splitter = splitter
        self._dataset: DatasetDict | None = None
        self.logger = logger

    @property
    def dataset(self):
        return iter(self._dataset)

    @staticmethod
    def clean_html_text(text: str) -> str:
        """Очистка HTML текста"""

        text = re.sub(r'<[^>]+>', '', text)
        text = html.unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @staticmethod
    def find_tags(text: str) -> list[str]:
        return [tag for tag in PYTHON_KEYWORDS if tag in text]

    def process_dataset_for_rag(self, batch_size=1000) -> list[Document]:
        """Обработка датасета для RAG"""

        processed_data = []

        for item in self.dataset:
            clean_question = self.clean_html_text(item['вопрос'])
            clean_answer = self.clean_html_text(item['ответ'])
            combined_text = f'!Вопрос: {clean_question}###Ответ: {clean_answer}'

            doc = Document(page_content=combined_text,
                           metadata={'tags': ' '.join(self.find_tags(combined_text))})
            processed_data.append(doc)
            self.logger.info(f'Processed item: {doc}')

        self.logger.info(f'Processed {len(processed_data)} documents')
        return processed_data

    def load(self) -> list[Document]:
        self._dataset = load_dataset(self.ds_name, split='train')
        documents = self.process_dataset_for_rag()

        splits = self.splitter.split_documents(documents)
        self.logger.info(f'Total splits: {len(splits)}')

        return splits
