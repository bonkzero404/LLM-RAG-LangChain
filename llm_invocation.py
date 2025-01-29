import numpy as np
import uuid
import redis
import json
import hashlib
import torch
from transformers import BertTokenizer, BertModel
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from scipy.spatial.distance import cosine
from llm_model import LLMModel
from tools import run_tool
from config import QUESTION_THRESHOLD, REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD

class LLMInvocation:
    redis_client = redis.StrictRedis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
    )
    tokenizer = BertTokenizer.from_pretrained("indobenchmark/indobert-base-p2")
    model = BertModel.from_pretrained("indobenchmark/indobert-base-p2")

    store = {}
    config = {}

    @staticmethod
    def generate_session_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def get_session_history(session_id: str) -> ChatMessageHistory:
        if session_id not in LLMInvocation.store:
            LLMInvocation.store[session_id] = ChatMessageHistory()
        return LLMInvocation.store[session_id]

    @staticmethod
    def add_message_to_session(session_id: str, message) -> None:
        if session_id not in LLMInvocation.store:
            LLMInvocation.store[session_id] = ChatMessageHistory()
        LLMInvocation.store[session_id].add_message(message)

    @staticmethod
    def clear_session_history(session_id: str) -> None:
        if session_id in LLMInvocation.store:
            del LLMInvocation.store[session_id]

    @staticmethod
    def get_current_session_id(agent_scratchpad: dict) -> str:
        return agent_scratchpad.get("session_id", None)

    @staticmethod
    def normalize_question_indoBERT(question: str) -> np.ndarray:
        inputs = LLMInvocation.tokenizer(question, return_tensors="pt", truncation=True, padding=True, max_length=128)
        with torch.no_grad():
            outputs = LLMInvocation.model(**inputs)

        sentence_embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
        sentence_embedding_rounded = np.round(sentence_embedding, 4)

        return sentence_embedding_rounded

    @staticmethod
    def generate_cache_key(session_id: str, question: str) -> str:
        normalized_question = LLMInvocation.normalize_question_indoBERT(question)
        normalized_question_str = str(normalized_question.tolist())

        key = hashlib.md5(f"{session_id}-{normalized_question_str}".encode()).hexdigest()
        return f"cache:{key}"

    @staticmethod
    def clear_all_cache():
        LLMInvocation.redis_client.flushall()

    @staticmethod
    def compare_similarity(question1: str, question2: str) -> bool:
        embedding1 = LLMInvocation.normalize_question_indoBERT(question1)
        embedding2 = LLMInvocation.normalize_question_indoBERT(question2)

        similarity = 1 - cosine(embedding1, embedding2)
        print(f"Similarity: {similarity}")

        return similarity > QUESTION_THRESHOLD

    @staticmethod
    def create_agent(tools):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", (
                    "Kamu adalah asisten layanan server, nama kamu adalah BotJuraganKlod. "
                    "Gunakan konteks yang diberikan untuk menjawab pertanyaan. "
                    "Jangan memberikan jawaban yang tidak berkaitan dengan konteks. "
                    "Hasil tidak boleh ambigu, dan jawaban harus singkat. "
                    "Jika terdapat kata kunci layanan itu maksudnya adalah produk. "
                    "Jika ada pertanyaan mengenai ini apa, atau seperti kebingungan tentang apa, berikan konteks tentang JuraganKlod. "
                    "Jika ada pertanyaan mengenai cara order, berikan jawaban dengan cara mengirimkan nama lengkap, email dan SKU produk atau Nama Produk. "
                    "Jangan menjawab tidak tahu, atau tidak mendapatkan referensi, coba proses jawaban dengan tool lainnya yang relevan. "
                    "Gunakan tool 'get-content-tool' jika kamu membutuhkan informasi lebih lanjut dan tanpa merubah query input. "
                )),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        agent = create_tool_calling_agent(llm=LLMModel.llm(), tools=tools, prompt=prompt)
        agent_executor = AgentExecutor(
            name="BotJuraganKlod",
            agent=agent,
            tools=tools,
            return_intermediate_steps=True,
        )

        agent_with_history = RunnableWithMessageHistory(
            agent_executor,
            LLMInvocation.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="output",
            stream_runnable=False,
        )

        return agent_with_history

    @staticmethod
    def invoke(question: str, session_id: str) -> str:
        tools = run_tool()
        agent_with_history = LLMInvocation.create_agent(tools)

        LLMInvocation.config = {
            "configurable": {
                "session_id": session_id
            }
        }

        output = agent_with_history.invoke(
            {
                "input": question,
                "chat_history": LLMInvocation.get_session_history(session_id).messages
            },
            LLMInvocation.config
        )

        output_data = output.get("output", "")

        return output_data

    @staticmethod
    def invoke_with_cache(question: str, session_id: str) -> str:
        tools = run_tool()
        agent_with_history = LLMInvocation.create_agent(tools)
        cache_key = LLMInvocation.generate_cache_key(session_id, question)

        cached_response = LLMInvocation.redis_client.get(cache_key)
        if cached_response:
            cached_data = json.loads(cached_response)

            if cached_data.get("must_cache"):
                print("🔄 Cache ditemukan tetapi diabaikan karena menggunakan tools")
            else:
                print("🔥 Menggunakan cache")
                memory = LLMInvocation.get_session_history(session_id)

                memory.add_user_message(question)
                memory.add_ai_message(cached_data["output"])

                return cached_data["output"]

        for stored_key in LLMInvocation.redis_client.keys("cache:*"):
            cached_question_data = LLMInvocation.redis_client.get(stored_key)
            if not cached_question_data:
                continue

            cached_json = json.loads(cached_question_data)
            before_question = cached_json.get("input")

            if before_question and LLMInvocation.compare_similarity(question, before_question):
                if cached_json.get("must_cache"):
                    print("🔄 Cache pertanyaan mirip ditemukan tetapi diabaikan karena menggunakan tools")
                else:
                    print("🔥 Pertanyaan mirip, menggunakan cache")
                    print("🔥 Pertanyaan sebelumnya:", before_question)
                    print("🔥 Pertanyaan saat ini:", question)

                    memory = LLMInvocation.get_session_history(session_id)

                    memory.add_user_message(question)
                    memory.add_ai_message(cached_json["output"])

                    return cached_json["output"]

        LLMInvocation.config = {"configurable": {"session_id": session_id}}
        output = agent_with_history.invoke({"input": question}, LLMInvocation.config)

        if isinstance(output, dict):
            output_data = output.get("output", "")

            must_cache = False

            for step in output.get("intermediate_steps", []):
                tool_action = step[0]
                if hasattr(tool_action, "tool") and "get-content-tool" not in tool_action.tool:
                    must_cache = True
                    break

            LLMInvocation.redis_client.set(cache_key, json.dumps({
                "input": question,
                "output": output_data,
                "must_cache": must_cache
            }), ex=3600)

            return output_data
        else:
            print("Output tidak dapat diserialisasi:", output)
            return "Terjadi kesalahan dalam proses."