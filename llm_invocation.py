import uuid
# from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from llm_model import LLMModel
from tools import run_tool

class LLMInvocation:

    store = {}
    config = {}

    @staticmethod
    def generate_session_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in LLMInvocation.store:
            LLMInvocation.store[session_id] = ChatMessageHistory()
        return LLMInvocation.store[session_id]

    @staticmethod
    def get_current_session_id(agent_scratchpad: dict) -> str:
        return agent_scratchpad.get("session_id", None)

    @staticmethod
    def clear_session_history(session_id: str) -> None:
        if session_id in LLMInvocation.store:
            del LLMInvocation.store[session_id]

    @staticmethod
    def create_agent(tools):

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "Kamu adalah asisten layanan server, nama kamu adalah BotJuraganKlod. "
                        "Gunakan konteks yang diberikan untuk menjawab pertanyaan. "
                        "Coba gunakan tool get-content-tool untuk mencari referensi dari konteks yang diberikan. "
                        "Jangan memberikan jawaban yang tidak berkaitan dengan konteks. "
                        "Hasil tidak boleh ambigu, dan jawaban harus singkat. "
                        "Jika terdapat kata kunci layanan itu maksudnya adalah produk. "
                        "Jika ada pertanyaan mengenai ini apa, atau seperti kebingungan tentang apa, berikan konteks tentang JuraganKlod. "
                        "Jika ada pertanyaan mengenai cara order, berikan jawaban dengan cara mengirimkan nama lengkap, email dan SKU produk atau Nama Produk. "
                        "Jangan menjawab tidak tahu, atau tidak mendapatkan referensi, coba proses jawaban dengan tool lainnya yang relevan. "
                        "Gunakan tool 'get-content-tool' jika kamu membutuhkan informasi lebih lanjut dan tanpa merubah query input. "
                    ),
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        # llm_with_tools = LLMModel.llm().bind_tools(tools)
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
    def invoke(question: str, session_id: str, history: list[BaseMessage]) -> str:
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

        return output