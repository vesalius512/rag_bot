import logging.config

import openai
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm

from config import settings
from constants import (
    CHROMA_PATH,
    PROMTP_TMPL,
    YANDEX_CLOUD_API_KEY,
    YANDEX_CLOUD_FOLDER,
    YANDEX_CLOUD_MODEL,
)
from fetch_data import RedditConnector
from rag_data import DataSetLoader
from utils import coroutine


def init_logging():
    logging.config.dictConfig(settings.LOGGING_BASE_CONFIG)


@coroutine
def pipeline():
    logging.info("Loading pipeline data...")

    connector = RedditConnector()

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    loader = DataSetLoader(splitter=splitter, connector=connector)
    docs = loader.load()

    batch_size = 100
    vector_store = None
    with tqdm(total=len(docs), desc="Ingesting documents") as pbar:
        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i : i + batch_size]
            if not vector_store:
                vector_store = Chroma.from_documents(
                    documents=batch_docs,
                    embedding=embeddings,
                    collection_name="CryptoCurrency",
                    persist_directory=CHROMA_PATH,
                )
            else:
                vector_store.add_documents(batch_docs)
            pbar.update(len(batch_docs))

    client = openai.OpenAI(
        api_key=YANDEX_CLOUD_API_KEY,
        base_url="https://rest-assistant.api.cloud.yandex.net/v1",
        project=YANDEX_CLOUD_FOLDER,
    )

    try:
        while True:
            query = yield
            results = vector_store.similarity_search(query, k=5)
            for doc in results:
                logging.info(f"Найден документ: {doc}")
            prompt = PROMTP_TMPL.format(
                query, "\n".join([doc.page_content for doc in results])
            )
            response = client.responses.create(
                model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
                input=prompt,
                temperature=0.8,
                max_output_tokens=1500,
            )
            answer = response.output[0].content[0].text
            yield answer

    except GeneratorExit:
        logging.info("rag bot stopped")


def main():
    init_logging()
    rag = pipeline()

    while True:
        input_ = input("===> ")
        if input_ == "exit":
            break
        response = rag.send(input_)
        print(f"chat: {response}")
        next(rag)


if __name__ == "__main__":
    main()
