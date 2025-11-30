import logging

import openai
from torch.distributed.rpc.api import docstring
from tqdm import tqdm
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

from constants import (YANDEX_CLOUD_FOLDER,
                       YANDEX_CLOUD_API_KEY,
                       YANDEX_CLOUD_MODEL,
                       PROMTP_TMPL)
from rag_data import DataSetLoader
from utils import coroutine


def init_logger():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger

@coroutine
def pipeline():
    print("Loading pipeline data...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500,
                                              chunk_overlap=200,
                                              add_start_index=True,
                                              separators=['!Вопрос: '])
    loader = DataSetLoader(ds_name='zelkame/ru-stackoverflow-py',
                           splitter=splitter,
                           logger=init_logger())
    docs = loader.load()

    batch_size = 100
    vector_store = None
    with tqdm(total=len(docs), desc="Ingesting documents") as pbar:
        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i:i+batch_size]
            if not vector_store:
                vector_store = Chroma.from_documents(
                    documents=batch_docs,
                    embedding=embeddings,
                    collection_name='ru_stackoverflow_py',
                    persist_directory='./chroma_db'
                )
            else:
                vector_store.add_documents(batch_docs)
            pbar.update(len(batch_docs))

    client = openai.OpenAI(
        api_key=YANDEX_CLOUD_API_KEY,
        base_url="https://rest-assistant.api.cloud.yandex.net/v1",
        project=YANDEX_CLOUD_FOLDER
    )

    try:
        while True:
            query = yield
            results = vector_store.similarity_search(query, k=1)
            for doc in results:
                print(f"Найден документ: {doc}")
            question, answer = doc.page_content.split('###')[0][8:], doc.page_content.split('###')[1][7:]
            prompt = PROMTP_TMPL.format(question, answer)
            response = client.responses.create(
                model=f"gpt://{YANDEX_CLOUD_FOLDER}/{YANDEX_CLOUD_MODEL}",
                input=prompt,
                temperature=0.8,
                max_output_tokens=1500
            )
            answer = response.output[0].content[0].text
            yield answer

    except GeneratorExit:
        print("rag bot stopped")


def main():
    rag = pipeline()

    while True:
        input_ = input('===> ')
        if input_ == 'exit':
            break
        response = rag.send(input_)
        print(f"chat: {response}")
        next(rag)


if __name__ == '__main__':
    main()
