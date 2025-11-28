import logging

from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag_data import DataSetLoader


def init_logger():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


def communication():
    answer = ...
    question = yield answer


def main(ds_name: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500,
                                              chunk_overlap=200,
                                              add_start_index=True,
                                              separators=['!Вопрос: '])
    loader = DataSetLoader(ds_name=ds_name,
                           splitter=splitter,
                           logger=init_logger())
    docs = loader.load()
    vector_store = Chroma.from_documents(
        documents=docs[:100],
        collection_name='ru_stackoverflow_py',
        persist_directory='./chroma_db'
    )
    query = "Как использовать тип данных Literal в python?"
    results = vector_store.similarity_search(query, k=1)

    for doc in results:
        print(f"Найден документ: {doc}")


if __name__ == '__main__':
    main('zelkame/ru-stackoverflow-py')
