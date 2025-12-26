import logging
import re
from datetime import datetime

import html
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from fetch_data import Connector


class DataSetLoader:
    def __init__(self,
                 splitter: RecursiveCharacterTextSplitter,
                 logger: logging.Logger,
                 connector: Connector):
        self.splitter = splitter
        self.logger = logger
        self.connector = connector

    @staticmethod
    def clean_html_text(text: str) -> str:
        """Очистка HTML текста"""

        text = html.unescape(text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?$€£%()\[\]:;@#/+\-*]', '', text)

        return text.strip()

    def process_dataset_for_rag(self, documents: list[dict]) -> list[Document]:
        """Обработка датасета для RAG"""

        processed_data = []

        for item in documents:
            clean_text = self.clean_html_text(item.get('text', ''))
            metadata = {
                'source': item.get('source', 'unknown'),
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'date': item.get('created', datetime.now()),
                'score': item.get('score', 0),
            }
            doc = Document(page_content=clean_text,
                           metadata=metadata)
            processed_data.append(doc)

            self.logger.info(f'Processed item: {doc}')

        self.logger.info(f'Processed {len(processed_data)} documents')
        return processed_data

    def load(self) -> list[Document]:
        raw_data = self.connector.fetch()
        documents = self.process_dataset_for_rag(raw_data)

        splits = self.splitter.split_documents(documents)
        self.logger.info(f'Total splits: {len(splits)}')

        return splits
