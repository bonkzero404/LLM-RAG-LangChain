from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from config import OPENAI_MODEL, OPENAI_EMBEDDINGS_MODEL, OLLAMA_MODEL, OLLAMA_EMBEDDINGS_MODEL, WITH_OLLAMA

class LLMModel:
    with_ollama = WITH_OLLAMA

    @staticmethod
    def llm():
        if not LLMModel.with_ollama:
            return ChatOpenAI(model=OPENAI_MODEL, temperature=1, max_tokens=1000)

        return ChatOllama(model=OLLAMA_MODEL, temperature=0.5, max_tokens=500)

    @staticmethod
    def embeddings():
        if not LLMModel.with_ollama:
            return OpenAIEmbeddings(model=OPENAI_EMBEDDINGS_MODEL)

        return OllamaEmbeddings(model=OLLAMA_EMBEDDINGS_MODEL)

    @staticmethod
    def bind_tools(llm, tools):
        setattr(llm, 'tools', tools)
        return llm