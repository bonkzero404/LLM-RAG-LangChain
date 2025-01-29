from typing import List
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_core.vectorstores.base import VectorStoreRetriever
from llm_model import LLMModel
from config import CHROMA_PATH, CHROMA_COLLECTION

class VectorStoreDocuments:
    def __init__(self):
        self.vectorstore = None

    def vector_store(self) -> 'VectorStoreDocuments':
        self.vectorstore = Chroma(
            collection_name=CHROMA_COLLECTION,
            embedding_function=LLMModel.embeddings(),
            persist_directory=CHROMA_PATH,
        )
        return self

    def store_documents(self, documents: List[Document]) -> None:
        self.vectorstore.add_documents(documents=documents, overwrite=True)

    def retriever(self) -> VectorStoreRetriever:
        return self.vectorstore.as_retriever()

    def remove_collection(self):
        self.vectorstore.reset_collection()

    def search(self, query: str, k: int = 5) -> List[Document]:
        return self.vectorstore.similarity_search(query=query, k=k)
